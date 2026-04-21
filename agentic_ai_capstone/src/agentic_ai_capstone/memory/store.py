"""Memory persistence for customer support conversations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryStore:
    """In-memory store for profiles, transcripts, and state snapshots."""

    _profiles: dict[str, dict[str, str]] = field(default_factory=dict)
    _history: dict[str, list[str]] = field(default_factory=dict)
    _events: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    _state_snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get_profile(self, customer_id: str) -> dict[str, str]:
        return self._profiles.setdefault(
            customer_id,
            {"tier": "standard", "preferred_contact": "email", "last_issue": "none"},
        )

    def update_profile(self, customer_id: str, **fields: str) -> None:
        self.get_profile(customer_id).update(fields)

    def append_message(self, customer_id: str, text: str) -> None:
        self._history.setdefault(customer_id, []).append(text)

    def append_turn(self, customer_id: str, agent: str, user_message: str, response: str) -> None:
        self.append_message(customer_id, user_message)
        self.append_message(customer_id, response)
        self._events.setdefault(customer_id, []).append(
            {
                "agent": agent,
                "user_message": user_message,
                "response": response,
            }
        )

    def append_event(self, customer_id: str, agent: str, detail: str) -> None:
        self._events.setdefault(customer_id, []).append({"agent": agent, "detail": detail})

    def get_recent_messages(self, customer_id: str, limit: int = 6) -> list[str]:
        return self._history.get(customer_id, [])[-limit:]

    def get_events(self, customer_id: str) -> list[dict[str, str]]:
        return list(self._events.get(customer_id, []))

    def save_state(self, customer_id: str, state: dict[str, Any]) -> None:
        self._state_snapshots[customer_id] = dict(state)

    def get_state(self, customer_id: str) -> dict[str, Any] | None:
        snapshot = self._state_snapshots.get(customer_id)
        return dict(snapshot) if snapshot else None
