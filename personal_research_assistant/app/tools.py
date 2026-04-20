"""Tool implementations for web search, notes, and calendar lookup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .memory import FactMemory
from .types import ToolResult


@dataclass
class WebSearchTool:
    """Mock web search tool."""

    def run(self, query: str) -> ToolResult:
        return ToolResult(
            tool_name="web_search",
            success=True,
            output=(
                f"Mock search results for '{query}':\n"
                "1. AI policy landscape (https://example.com/ai-policy)\n"
                "2. Research methods guide (https://example.com/methods)\n"
                "3. Domain trends report (https://example.com/trends)"
            ),
        )


@dataclass
class NoteTool:
    """Tool for saving and recalling long-term notes."""

    memory: FactMemory

    def save(self, content: str, important: bool = False) -> ToolResult:
        tags = ["important"] if important else []
        record = self.memory.add(text=content, tags=tags)
        return ToolResult(
            tool_name="note_save",
            success=True,
            output=f"Saved note #{record.id}: {record.text}",
            metadata={"fact_id": record.id, "important": important},
        )

    def recall(self, query: str) -> ToolResult:
        matches = self.memory.search(query)
        if not matches:
            return ToolResult(
                tool_name="note_lookup",
                success=True,
                output="No matching notes found.",
            )
        lines = [f"{item.id}. {item.text}" for item in matches[:5]]
        return ToolResult(
            tool_name="note_lookup",
            success=True,
            output="Matched notes:\n" + "\n".join(lines),
            metadata={"match_count": len(matches)},
        )


@dataclass
class CalendarTool:
    """Tool for simple calendar phrase lookup."""

    def run(self, phrase: str) -> ToolResult:
        parsed = _parse_date_phrase(phrase)
        if parsed is None:
            return ToolResult(
                tool_name="calendar_lookup",
                success=False,
                output=f"Could not parse date phrase: '{phrase}'.",
            )
        weekday = parsed.strftime("%A")
        return ToolResult(
            tool_name="calendar_lookup",
            success=True,
            output=f"Calendar lookup for {parsed.isoformat()} ({weekday}): no events scheduled.",
            metadata={"date": parsed.isoformat()},
        )


def _parse_date_phrase(phrase: str) -> date | None:
    token = phrase.strip().lower()
    for marker in ("calendar", "lookup", "schedule", "for", "on", "date", "what is"):
        token = token.replace(marker, " ")
    token = " ".join(token.split())
    today = date.today()
    if token in {"today", "now"}:
        return today
    if token == "tomorrow":
        return today + timedelta(days=1)
    if token == "yesterday":
        return today - timedelta(days=1)
    try:
        return datetime.strptime(token, "%Y-%m-%d").date()
    except ValueError:
        return None
