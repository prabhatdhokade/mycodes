"""The ReAct-pattern Personal Research Assistant.

The agent orchestrates:
  * short-term conversation memory (with rolling summarization)
  * long-term fact memory + preferences
  * tool calling (web search, calendar, notes, recall)
  * HITL approval for important notes
  * structured JSON outputs at every reasoning step
  * observability: every LLM call and tool call is logged with latency
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from pydantic import BaseModel, Field, ValidationError

from ..config import settings
from ..llm import LLMClient, get_llm
from ..memory import ConversationMemory, FactStore, PreferenceStore
from ..observability import get_logger, log_event
from ..tools import (
    CalendarLookupTool,
    FactLookupTool,
    HumanApproval,
    NoteSaverTool,
    ToolRegistry,
    WebSearchTool,
)
from .prompts import render_system_prompt

logger = get_logger("agent")


class ReActStep(BaseModel):
    """Strict schema every LLM turn must conform to."""

    thought: str = Field(default="")
    action: str
    action_input: dict[str, Any] = Field(default_factory=dict)


@dataclass
class AgentStep:
    thought: str
    action: str
    action_input: dict[str, Any]
    observation: str = ""
    approved: bool | None = None


@dataclass
class AgentRunResult:
    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    summarized: bool = False


def _default_approval(_tool: str, _args: dict) -> bool:
    """Auto-approve only if the user opted in via settings."""

    return settings.auto_approve_notes


class ResearchAgent:
    """High-level ReAct agent facade. One instance per conversation session."""

    def __init__(
        self,
        *,
        session_id: str = "default",
        llm: LLMClient | None = None,
        approval: HumanApproval | None = None,
        fact_store: FactStore | None = None,
        preferences: PreferenceStore | None = None,
        conversation: ConversationMemory | None = None,
        max_steps: int | None = None,
    ) -> None:
        self.session_id = session_id
        self.llm = llm or get_llm()
        self.approval = approval or _default_approval
        self.fact_store = fact_store or FactStore()
        self.preferences = preferences or PreferenceStore()
        self.conversation = conversation or ConversationMemory(session_id=session_id)
        self.max_steps = max_steps or settings.max_react_steps

        self.tools = ToolRegistry(
            [
                WebSearchTool(),
                NoteSaverTool(fact_store=self.fact_store),
                CalendarLookupTool(),
                FactLookupTool(fact_store=self.fact_store),
            ]
        )

    # ---- public API ------------------------------------------------------

    def run(self, user_message: str) -> AgentRunResult:
        """Handle one user turn and return the final answer + trace."""

        user_message = (user_message or "").strip()
        if not user_message:
            return AgentRunResult(answer="(empty message)", steps=[])

        log_event(
            logger,
            "agent.turn.start",
            session_id=self.session_id,
            message_length=len(user_message),
        )
        self.conversation.add("user", user_message)

        memory_hits = self._memory_snippet(user_message)
        system_prompt = render_system_prompt(
            tools_block=self.tools.render_for_prompt(),
            preferences=self.preferences.all(),
            memory_hits=memory_hits,
        )

        steps: list[AgentStep] = []
        final_answer: str | None = None

        for step_idx in range(1, self.max_steps + 1):
            messages = self._build_messages(system_prompt, steps)
            response = self.llm.complete(messages, temperature=0.2, max_tokens=600)
            parsed = self._parse_step(response.content)

            if parsed is None:
                final_answer = response.content.strip() or "I couldn't produce a structured answer."
                steps.append(
                    AgentStep(
                        thought="(unparseable LLM output - falling back to raw text)",
                        action="final_answer",
                        action_input={"answer": final_answer},
                    )
                )
                break

            log_event(
                logger,
                "agent.step",
                session_id=self.session_id,
                step=step_idx,
                action=parsed.action,
                thought=parsed.thought[:200],
            )

            if parsed.action == "final_answer":
                final_answer = str(parsed.action_input.get("answer", "")).strip()
                if not final_answer:
                    final_answer = "I don't have enough information to answer that yet."
                steps.append(
                    AgentStep(
                        thought=parsed.thought,
                        action=parsed.action,
                        action_input=parsed.action_input,
                        observation=final_answer,
                    )
                )
                break

            tool = self.tools.get(parsed.action)
            if tool is None:
                obs = f"Unknown tool '{parsed.action}'. Available: {', '.join(self.tools.names())}."
                steps.append(
                    AgentStep(
                        thought=parsed.thought,
                        action=parsed.action,
                        action_input=parsed.action_input,
                        observation=obs,
                    )
                )
                continue

            result = tool.invoke(parsed.action_input, approval=self.approval)
            steps.append(
                AgentStep(
                    thought=parsed.thought,
                    action=parsed.action,
                    action_input=parsed.action_input,
                    observation=result.as_observation(),
                    approved=result.meta.get("approved") if tool.requires_approval else None,
                )
            )
        else:
            final_answer = (
                "I hit my reasoning budget before finishing. "
                "Here's what I found so far:\n"
                + "\n".join(f"- {s.action}: {s.observation[:200]}" for s in steps if s.observation)
            )

        assert final_answer is not None
        self.conversation.add("assistant", final_answer)
        summarized = self.conversation.maybe_summarize(self.llm)

        log_event(
            logger,
            "agent.turn.end",
            session_id=self.session_id,
            steps=len(steps),
            summarized=summarized,
        )
        return AgentRunResult(answer=final_answer, steps=steps, summarized=summarized)

    def stream(self, user_message: str) -> Iterator[str]:
        """Word-by-word streaming of the final answer.

        The ReAct loop itself runs synchronously (it has to in order to
        invoke tools), then the final answer is streamed token-ish for UX.
        """

        result = self.run(user_message)
        for chunk in re.findall(r"\S+\s*", result.answer):
            yield chunk

    # ---- helpers ---------------------------------------------------------

    def _memory_snippet(self, query: str, k: int = 3) -> str:
        hits = self.fact_store.search(query, k=k)
        if not hits:
            return ""
        lines = []
        for fact, score in hits:
            preview = fact.content.replace("\n", " ")
            if len(preview) > 180:
                preview = preview[:180] + "…"
            lines.append(f"- [{fact.id} · score={score:.2f} · importance={fact.importance}] {preview}")
        return "\n".join(lines)

    def _build_messages(
        self, system_prompt: str, steps: list[AgentStep]
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation.as_chat())
        for s in steps:
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "thought": s.thought,
                            "action": s.action,
                            "action_input": s.action_input,
                        }
                    ),
                }
            )
            if s.observation and s.action != "final_answer":
                messages.append(
                    {
                        "role": "user",
                        "content": f"Observation: {s.observation}",
                    }
                )
        return messages

    @staticmethod
    def _parse_step(raw: str) -> ReActStep | None:
        """Extract a ReActStep from the LLM output (tolerant of code fences)."""

        text = (raw or "").strip()
        if not text:
            return None
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        try:
            return ReActStep(**obj)
        except ValidationError:
            return None
