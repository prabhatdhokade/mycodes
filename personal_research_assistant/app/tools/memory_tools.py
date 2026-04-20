"""Tools that expose long-term memory to the ReAct loop."""

from __future__ import annotations

import json
from typing import Any

from ..memory import FactStore
from .base import Tool, ToolResult


class FactLookupTool(Tool):
    name = "recall_fact"
    description = (
        "Search the user's long-term memory / saved notes for relevant facts. "
        "Use this when the user asks what they saved or referenced earlier."
    )
    parameters = {
        "query": {"type": "string", "description": "What to look up in stored notes."},
        "k": {"type": "integer", "description": "Max number of matches (default 3)."},
    }

    def __init__(self, fact_store: FactStore | None = None) -> None:
        self.fact_store = fact_store or FactStore()

    def execute(self, query: str = "", k: int = 3, **_: Any) -> ToolResult:
        query = (query or "").strip()
        if not query:
            return ToolResult(ok=False, output="Empty query.")
        k = max(1, min(int(k or 3), 10))
        hits = self.fact_store.search(query, k=k)
        payload = {
            "query": query,
            "results": [
                {
                    "id": f.id,
                    "score": round(score, 4),
                    "importance": f.importance,
                    "tags": f.tags,
                    "content": f.content,
                }
                for f, score in hits
            ],
        }
        return ToolResult(
            ok=True,
            output=json.dumps(payload, ensure_ascii=False),
            meta={"count": len(hits)},
        )
