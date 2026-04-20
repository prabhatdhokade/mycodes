"""Memory stores for short-term conversation and long-term facts."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .types import ChatMessage, FactRecord


class ConversationMemory:
    """Persist short-term conversation across turns."""

    def __init__(self, path: Path, max_messages: int = 40) -> None:
        self.path = path
        self.max_messages = max_messages
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def all_messages(self) -> list[ChatMessage]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [ChatMessage(**item) for item in raw]

    def _write(self, messages: list[ChatMessage]) -> None:
        payload = [asdict(msg) for msg in messages[-self.max_messages :]]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add(self, role: str, content: str) -> list[ChatMessage]:
        messages = self.all_messages()
        messages.append(ChatMessage(role=role, content=content))
        self._write(messages)
        return messages[-self.max_messages :]

    def append_summary(self, summary: str) -> None:
        messages = self.all_messages()
        compacted = [ChatMessage(role="system", content=f"Conversation summary: {summary}")]
        compacted.extend(messages[-8:])
        self._write(compacted)


class FactMemory:
    """Persist long-term facts/notes."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def all_facts(self) -> list[FactRecord]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [FactRecord(**item) for item in raw]

    def _write(self, facts: list[FactRecord]) -> None:
        payload = [asdict(item) for item in facts]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add(self, text: str, tags: list[str] | None = None) -> FactRecord:
        facts = self.all_facts()
        next_id = (facts[-1].id + 1) if facts else 1
        record = FactRecord(id=next_id, text=text, tags=tags or [])
        facts.append(record)
        self._write(facts)
        return record

    def search(self, query: str) -> list[FactRecord]:
        q = query.strip().lower()
        facts = self.all_facts()
        if not q:
            return facts[-10:]
        tokens = [token for token in q.replace("?", " ").replace(",", " ").split() if len(token) >= 3]
        matches: list[FactRecord] = []
        for fact in facts:
            haystack = f"{fact.text.lower()} {fact.tags_as_text().lower()}"
            if q in haystack:
                matches.append(fact)
                continue
            if any(token in haystack for token in tokens):
                matches.append(fact)
        return matches
