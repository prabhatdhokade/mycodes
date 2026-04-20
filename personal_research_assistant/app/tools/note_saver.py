"""Note-saving tool (HITL-gated for important notes)."""

from __future__ import annotations

from typing import Any

from ..memory import FactStore
from .base import Tool, ToolResult


class NoteSaverTool(Tool):
    name = "save_note"
    description = (
        "Save a note to long-term memory. Important notes require human "
        "approval before persisting."
    )
    parameters = {
        "title": {"type": "string", "description": "Short title or topic for the note."},
        "content": {"type": "string", "description": "Full body of the note."},
        "tags": {"type": "array", "description": "Optional list of string tags."},
        "important": {
            "type": "boolean",
            "description": "If true, require human approval before saving.",
        },
    }
    requires_approval = True  # gated by the registry's HITL callback

    def __init__(self, fact_store: FactStore | None = None) -> None:
        self.fact_store = fact_store or FactStore()

    def execute(
        self,
        title: str = "",
        content: str = "",
        tags: list[str] | None = None,
        important: bool = False,
        **_: Any,
    ) -> ToolResult:
        body = (content or "").strip()
        if not body:
            return ToolResult(ok=False, output="Note content is empty.")
        title = (title or body[:60]).strip()
        merged = f"{title}\n\n{body}" if title and title not in body else body
        importance = 5 if important else 3
        fact = self.fact_store.add(
            merged,
            tags=list(tags or []),
            source="note",
            importance=importance,
        )
        return ToolResult(
            ok=True,
            output=f"Saved note '{title}' with id {fact.id}.",
            meta={"fact_id": fact.id, "importance": importance},
        )
