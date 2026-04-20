"""Core ReAct-style personal research assistant implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Iterable
import uuid

from .hitl import ConsoleApprovalProvider, HITLGate, StaticApprovalProvider
from .llm import MockReActLLM
from .memory import ConversationMemory, FactMemory
from .observability import StructuredLogger
from .tools import CalendarTool, NoteTool, WebSearchTool
from .types import AgentReply, StructuredDecision, ToolResult


@dataclass
class AgentConfig:
    summarize_after_turns: int = 12
    enable_streaming: bool = True


class PersonalResearchAssistant:
    """A complete ReAct assistant with memory, tools, HITL, and logs."""

    def __init__(
        self,
        *,
        conversation_memory: ConversationMemory,
        fact_memory: FactMemory,
        web_search: WebSearchTool,
        note_tool: NoteTool,
        calendar_tool: CalendarTool,
        llm: MockReActLLM,
        logger: StructuredLogger,
        hitl_gate: HITLGate,
        config: AgentConfig | None = None,
    ) -> None:
        self.conversation_memory = conversation_memory
        self.fact_memory = fact_memory
        self.web_search = web_search
        self.note_tool = note_tool
        self.calendar_tool = calendar_tool
        self.llm = llm
        self.logger = logger
        self.hitl_gate = hitl_gate
        self.config = config or AgentConfig()

    @classmethod
    def with_defaults(
        cls,
        *,
        base_dir: str = "runtime",
        auto_approve_notes: bool = False,
        enable_streaming: bool = True,
        summarize_after_turns: int = 12,
        interactive_hitl: bool = False,
    ) -> "PersonalResearchAssistant":
        base = Path(base_dir)
        conv = ConversationMemory(base / "memory" / "conversation.json")
        facts = FactMemory(base / "memory" / "facts.json")
        logger = StructuredLogger(log_dir=str(base / "logs"))
        provider = ConsoleApprovalProvider() if interactive_hitl else StaticApprovalProvider(auto_approve_notes)
        return cls(
            conversation_memory=conv,
            fact_memory=facts,
            web_search=WebSearchTool(),
            note_tool=NoteTool(memory=facts),
            calendar_tool=CalendarTool(),
            llm=MockReActLLM(),
            logger=logger,
            hitl_gate=HITLGate(provider=provider),
            config=AgentConfig(
                summarize_after_turns=summarize_after_turns,
                enable_streaming=enable_streaming,
            ),
        )

    def handle_turn(self, user_input: str, stream: bool = False) -> AgentReply | Iterable[str]:
        trace_id = str(uuid.uuid4())
        started = time.perf_counter()

        self.conversation_memory.add("user", user_input)
        self.logger.log("agent_input", trace_id, {"user_input": user_input})

        conversation = self.conversation_memory.all_messages()
        facts = self.fact_memory.search("")
        with self.logger.timed("llm_call", trace_id) as timer:
            decision = self.llm.decide(user_input=user_input, conversation=conversation, facts=facts)
            timer.payload = {
                "system_prompt": self.llm.SYSTEM_PROMPT,
                "structured_output": self.llm.to_react_json(decision),
            }

        self.logger.log(
            "agent_decision",
            trace_id,
            {
                "thought": decision.thought,
                "action": decision.action,
                "action_input": decision.action_input,
                "should_save_fact": decision.should_save_fact,
                "importance": decision.importance,
            },
        )

        tool_result = self._invoke_tool(decision, trace_id)
        note_saved = False
        if decision.action == "note_save":
            if decision.importance == "high":
                tool_result = self._handle_note_save_hitl(decision, trace_id)
                note_saved = tool_result.success
            else:
                with self.logger.timed("tool_invocation", trace_id) as timer:
                    tool_result = self.note_tool.save(
                        content=decision.action_input,
                        important=False,
                    )
                    timer.payload = {
                        "tool": "note_save",
                        "input": decision.action_input,
                        "output": tool_result.output,
                        "success": tool_result.success,
                    }
                note_saved = tool_result.success
        elif decision.action == "respond":
            note_saved = True

        recalled_facts = self.fact_memory.search(user_input)
        final_text = self.llm.compose_final_answer(
            decision=decision,
            tool_observation=tool_result.output,
            recalled_facts=recalled_facts,
            note_saved=note_saved or decision.action != "note_save",
        )

        self.conversation_memory.add("assistant", final_text)
        self._maybe_summarize(trace_id)

        latency_ms = (time.perf_counter() - started) * 1000.0
        self.logger.log(
            "agent_output",
            trace_id,
            {"response": final_text, "used_tools": [tool_result.tool_name], "latency_ms": round(latency_ms, 3)},
        )

        if stream and self.config.enable_streaming:
            return self._stream_text(final_text)
        return AgentReply(
            text=final_text,
            trace_id=trace_id,
            latency_ms=round(latency_ms, 3),
            used_tools=[tool_result.tool_name],
        )

    def _invoke_tool(self, decision: StructuredDecision, trace_id: str) -> ToolResult:
        if decision.action == "respond":
            return ToolResult(tool_name="none", success=True, output="No tool needed.")

        with self.logger.timed("tool_invocation", trace_id) as timer:
            if decision.action == "web_search":
                result = self.web_search.run(decision.action_input)
            elif decision.action == "calendar_lookup":
                result = self.calendar_tool.run(decision.action_input)
            elif decision.action == "note_lookup":
                result = self.note_tool.recall(decision.action_input)
            elif decision.action == "note_save":
                result = ToolResult(
                    tool_name="note_save",
                    success=True,
                    output="Pending HITL approval before saving note.",
                )
            else:
                result = ToolResult(
                    tool_name=decision.action,
                    success=False,
                    output=f"Unknown action: {decision.action}",
                )
            timer.payload = {
                "tool": decision.action,
                "input": decision.action_input,
                "output": result.output,
                "success": result.success,
            }
            return result

    def _handle_note_save_hitl(self, decision: StructuredDecision, trace_id: str) -> ToolResult:
        approved = self.hitl_gate.request_save_approval(
            note_text=decision.action_input,
            importance=decision.importance,
        )
        self.logger.log(
            "hitl_checkpoint",
            trace_id,
            {
                "note": decision.action_input,
                "importance": decision.importance,
                "approved": approved,
            },
        )
        if not approved:
            return ToolResult(
                tool_name="note_save",
                success=False,
                output="Important note save request was declined at HITL checkpoint.",
            )
        with self.logger.timed("tool_invocation", trace_id) as timer:
            saved = self.note_tool.save(
                content=decision.action_input,
                important=(decision.importance == "high"),
            )
            timer.payload = {
                "tool": "note_save",
                "input": decision.action_input,
                "output": saved.output,
                "success": saved.success,
            }
        return saved

    def _maybe_summarize(self, trace_id: str) -> None:
        messages = self.conversation_memory.all_messages()
        if len(messages) < self.config.summarize_after_turns:
            return
        summary = self.llm.summarize(messages[-self.config.summarize_after_turns :])
        self.conversation_memory.append_summary(summary)
        self.logger.log(
            "conversation_summary",
            trace_id,
            {"summary": summary, "window_size": self.config.summarize_after_turns},
        )

    @staticmethod
    def _stream_text(text: str) -> Iterable[str]:
        for token in text.split():
            yield token + " "
