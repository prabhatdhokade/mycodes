"""Persistent-ish memory store for customer context.

Uses JSON files on disk for durability in a dev/demo setting. The API is
intentionally simple so it can be swapped for Redis, Postgres, or a vector
store without touching callers.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CustomerProfile:
    customer_id: str
    name: str = ""
    email: str = ""
    plan: str = "basic"
    preferences: Dict[str, Any] = field(default_factory=dict)
    past_tickets: List[Dict[str, Any]] = field(default_factory=list)
    conversation_log: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""


class MemoryStore:
    """Simple thread-safe JSON-backed customer memory store."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self._lock = threading.RLock()
        self._data: Dict[str, CustomerProfile] = {}
        if path and os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._data = {
            cid: CustomerProfile(**profile) for cid, profile in raw.items()
        }

    def _persist(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                {cid: asdict(p) for cid, p in self._data.items()},
                f,
                indent=2,
                default=str,
            )

    def upsert(self, profile: CustomerProfile) -> CustomerProfile:
        with self._lock:
            self._data[profile.customer_id] = profile
            self._persist()
            return profile

    def get(self, customer_id: str) -> Optional[CustomerProfile]:
        with self._lock:
            return self._data.get(customer_id)

    def get_or_create(self, customer_id: str, **defaults: Any) -> CustomerProfile:
        with self._lock:
            if customer_id not in self._data:
                self._data[customer_id] = CustomerProfile(
                    customer_id=customer_id, **defaults
                )
                self._persist()
            return self._data[customer_id]

    def append_message(self, customer_id: str, message: Dict[str, Any]) -> None:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile.conversation_log.append(message)
            # Keep a rolling window to bound memory size
            if len(profile.conversation_log) > 200:
                profile.conversation_log = profile.conversation_log[-200:]
            self._persist()

    def update_summary(self, customer_id: str, summary: str) -> None:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile.summary = summary
            self._persist()

    def add_ticket(self, customer_id: str, ticket: Dict[str, Any]) -> None:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile.past_tickets.append(ticket)
            self._persist()

    def set_preference(self, customer_id: str, key: str, value: Any) -> None:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile.preferences[key] = value
            self._persist()

    def all_ids(self) -> List[str]:
        with self._lock:
            return list(self._data.keys())

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            if self.path and os.path.exists(self.path):
                os.remove(self.path)
