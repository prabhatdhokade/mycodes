"""Calendar lookup tool backed by a simple JSON file.

Events are stored as ``{title, start, end, location, notes}``. The tool
supports natural queries like "today", "tomorrow", "next week", or a
fuzzy substring match on the title/notes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from ..config import settings
from .base import Tool, ToolResult


@dataclass
class CalendarEvent:
    title: str
    start: str  # ISO datetime
    end: str    # ISO datetime
    location: str = ""
    notes: str = ""


def _seed_events(today: date | None = None) -> list[CalendarEvent]:
    today = today or date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    return [
        CalendarEvent(
            title="Morning standup",
            start=f"{today.isoformat()}T09:30:00",
            end=f"{today.isoformat()}T09:45:00",
            location="Zoom",
            notes="Daily sync with the team.",
        ),
        CalendarEvent(
            title="Research review",
            start=f"{today.isoformat()}T14:00:00",
            end=f"{today.isoformat()}T15:00:00",
            location="Room 4B",
            notes="Review the ReAct agent prototype.",
        ),
        CalendarEvent(
            title="Dentist",
            start=f"{tomorrow.isoformat()}T11:00:00",
            end=f"{tomorrow.isoformat()}T11:30:00",
            location="Downtown clinic",
            notes="Bring insurance card.",
        ),
        CalendarEvent(
            title="Quarterly planning",
            start=f"{next_week.isoformat()}T10:00:00",
            end=f"{next_week.isoformat()}T12:00:00",
            location="HQ",
            notes="Prep roadmap slides.",
        ),
    ]


class CalendarLookupTool(Tool):
    name = "calendar_lookup"
    description = (
        "Look up calendar events. Accepts a natural-language query like "
        "'today', 'tomorrow', 'next week', or any keyword to match."
    )
    parameters = {
        "query": {
            "type": "string",
            "description": "When / what to look up, e.g. 'today' or 'dentist'.",
        }
    }

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.data_dir / "calendar.json")
        self._ensure_seed()

    def _ensure_seed(self) -> None:
        if self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(e) for e in _seed_events()], indent=2),
            encoding="utf-8",
        )

    def _load(self) -> list[CalendarEvent]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [CalendarEvent(**e) for e in raw]

    def execute(self, query: str = "", **_: Any) -> ToolResult:
        events = self._load()
        query_l = (query or "").lower().strip()
        today = date.today()

        def event_date(e: CalendarEvent) -> date:
            return datetime.fromisoformat(e.start).date()

        selection: list[CalendarEvent]
        if query_l == "" or "today" in query_l:
            selection = [e for e in events if event_date(e) == today]
            window = "today"
        elif "tomorrow" in query_l:
            selection = [e for e in events if event_date(e) == today + timedelta(days=1)]
            window = "tomorrow"
        elif "week" in query_l:
            end = today + timedelta(days=7)
            selection = [e for e in events if today <= event_date(e) <= end]
            window = "next 7 days"
        else:
            selection = [
                e
                for e in events
                if query_l in e.title.lower() or query_l in e.notes.lower()
            ]
            window = f"matching '{query}'"

        if not selection:
            return ToolResult(
                ok=True,
                output=json.dumps({"window": window, "events": []}),
                meta={"count": 0},
            )

        selection.sort(key=lambda e: e.start)
        payload = {
            "window": window,
            "events": [asdict(e) for e in selection],
        }
        return ToolResult(ok=True, output=json.dumps(payload), meta={"count": len(selection)})
