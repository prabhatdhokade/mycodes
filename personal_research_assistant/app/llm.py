"""Deterministic ReAct-style planner with structured outputs."""

from __future__ import annotations

import json
import re
from typing import Iterable

from .types import ChatMessage, FactRecord, StructuredDecision


class MockReActLLM:
    """A deterministic planner that mimics LLM structured output."""

    SYSTEM_PROMPT = (
        "You are a personal research assistant using ReAct. "
        "Return a structured decision with Thought, Action, and Action Input."
    )

    def decide(
        self,
        *,
        user_input: str,
        conversation: list[ChatMessage],
        facts: list[FactRecord],
    ) -> StructuredDecision:
        _ = conversation
        _ = facts
        text = user_input.strip()
        lower = text.lower()

        if any(token in lower for token in ("search", "find", "look up", "latest", "paper", "news")):
            return StructuredDecision(
                thought="Need external information, so web search is best.",
                action="web_search",
                action_input=text,
                should_save_fact=False,
            )
        if any(token in lower for token in ("calendar", "schedule", "today", "tomorrow", "date")):
            return StructuredDecision(
                thought="User asked about date/schedule; use calendar tool.",
                action="calendar_lookup",
                action_input=text,
                should_save_fact=False,
            )
        if any(token in lower for token in ("what do you remember", "recall", "memory", "fact", "facts")):
            return StructuredDecision(
                thought="User asks about saved notes; query memory.",
                action="note_lookup",
                action_input=text,
                should_save_fact=False,
            )
        if any(token in lower for token in ("remember", "save note", "store note", "important note")):
            note_text = self.extract_note_content(text)
            return StructuredDecision(
                thought="User asks to store knowledge as long-term memory.",
                action="note_save",
                action_input=note_text,
                should_save_fact=True,
                importance="high" if "important" in lower else "normal",
            )
        return StructuredDecision(
            thought="No tool required; respond directly.",
            action="respond",
            action_input=text,
            should_save_fact=False,
        )

    def to_react_json(self, decision: StructuredDecision) -> str:
        """Return structured JSON text for observability/debugging."""
        payload = {
            "thought": decision.thought,
            "action": decision.action,
            "action_input": decision.action_input,
            "should_save_fact": decision.should_save_fact,
            "importance": decision.importance,
        }
        return json.dumps(payload, ensure_ascii=True)

    def compose_final_answer(
        self,
        *,
        decision: StructuredDecision,
        tool_observation: str,
        recalled_facts: list[FactRecord],
        note_saved: bool,
    ) -> str:
        if decision.action == "respond":
            return (
                "I can help with research, note-taking, and calendar lookups. "
                "Ask me to search, save a note, or check a date."
            )
        if decision.action == "note_lookup":
            return tool_observation
        if decision.action == "note_save" and not note_saved:
            return "I did not save that important note because approval was declined."
        if recalled_facts and decision.action != "note_save":
            tail = "\n".join(f"- {item.text}" for item in recalled_facts[:2])
            return f"{tool_observation}\n\nRelated saved facts:\n{tail}"
        return tool_observation

    @staticmethod
    def summarize(messages: Iterable[ChatMessage]) -> str:
        parts: list[str] = []
        for msg in messages:
            parts.append(f"{msg.role}: {msg.content[:45]}")
        return " | ".join(parts)

    @staticmethod
    def extract_note_content(text: str) -> str:
        patterns = [
            r"save important note\s*:\s*(.+)$",
            r"remember this\s*:\s*(.+)$",
            r"save note\s*:\s*(.+)$",
            r"store note\s*:\s*(.+)$",
            r"remember\s+(.+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return text

