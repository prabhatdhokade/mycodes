"""Short-term conversation memory with rolling summarization.

Keeps the last N raw turns verbatim and, when history gets long, asks
the LLM to produce a running summary that replaces older messages.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import time
from typing import Iterable

from ..config import settings
from ..observability import get_logger, log_event

logger = get_logger("memory.conversation")


@dataclass
class Message:
    role: str
    content: str
    ts: float = field(default_factory=time)

    def to_chat(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class ConversationMemory:
    """Rolling conversation with a summary block at the front."""

    def __init__(
        self,
        session_id: str = "default",
        *,
        keep_last: int = 10,
        summarize_after: int | None = None,
        path: Path | None = None,
    ) -> None:
        self.session_id = session_id
        self.keep_last = keep_last
        self.summarize_after = summarize_after or settings.summarize_after_turns
        self.path = path or (settings.data_dir / f"conversation_{session_id}.json")
        self.summary: str = ""
        self.messages: list[Message] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.summary = data.get("summary", "")
            self.messages = [Message(**m) for m in data.get("messages", [])]
        except Exception as exc:
            logger.warning(
                "conversation_load_failed",
                extra={"event": "conversation_load_failed", "error": repr(exc)},
            )

    def _persist(self) -> None:
        payload = {
            "session_id": self.session_id,
            "summary": self.summary,
            "messages": [asdict(m) for m in self.messages],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add(self, role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self._persist()
        log_event(
            logger,
            "conversation.append",
            session_id=self.session_id,
            role=role,
            length=len(content),
            total_turns=len(self.messages),
        )
        return msg

    def last_n(self, n: int) -> list[Message]:
        return self.messages[-n:]

    def as_chat(self, include_summary: bool = True) -> list[dict[str, str]]:
        """Return the conversation formatted for an LLM chat request."""

        chat: list[dict[str, str]] = []
        if include_summary and self.summary:
            chat.append({"role": "system", "content": f"Prior conversation summary:\n{self.summary}"})
        chat.extend(m.to_chat() for m in self.last_n(self.keep_last))
        return chat

    def clear(self) -> None:
        self.summary = ""
        self.messages = []
        self._persist()

    def maybe_summarize(self, llm) -> bool:
        """Summarize older turns when the log grows past the threshold.

        Returns ``True`` when a summarization occurred.
        """

        if len(self.messages) < self.summarize_after:
            return False

        older = self.messages[: -self.keep_last] if self.keep_last < len(self.messages) else []
        if not older:
            return False

        transcript = "\n".join(f"{m.role}: {m.content}" for m in older)
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a helpful summarizer. Produce a concise running "
                    "summary (max 200 words) preserving names, decisions, and "
                    "open questions. Merge with any prior summary."
                ),
            },
            {
                "role": "user",
                "content": f"Prior summary:\n{self.summary or '(none)'}\n\nNew turns:\n{transcript}",
            },
        ]
        response = llm.complete(prompt, temperature=0.0, max_tokens=400)
        self.summary = response.content.strip()
        self.messages = self.messages[-self.keep_last :]
        self._persist()
        log_event(
            logger,
            "conversation.summarized",
            session_id=self.session_id,
            summary_chars=len(self.summary),
            remaining_turns=len(self.messages),
        )
        return True

    def recent_as_string(self, n: int | None = None) -> str:
        msgs: Iterable[Message] = self.messages if n is None else self.last_n(n)
        return "\n".join(f"{m.role}: {m.content}" for m in msgs)
