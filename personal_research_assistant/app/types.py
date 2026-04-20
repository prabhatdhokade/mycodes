"""Shared datatypes for the Personal Research Assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return an ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ChatMessage:
    """One conversation message."""

    role: str
    content: str
    timestamp: str = field(default_factory=utc_now_iso)


@dataclass
class FactRecord:
    """One long-term memory record."""

    id: int
    text: str
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def tags_as_text(self) -> str:
        return " ".join(self.tags)


@dataclass
class StructuredDecision:
    """Structured ReAct decision payload."""

    thought: str
    action: str
    action_input: str
    should_save_fact: bool
    importance: str = "normal"


@dataclass
class ToolResult:
    """Normalized tool output."""

    tool_name: str
    success: bool
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentReply:
    """Final user-facing response."""

    text: str
    trace_id: str
    latency_ms: float
    used_tools: list[str] = field(default_factory=list)


@dataclass
class LogEvent:
    """Structured log event persisted as JSON lines."""

    event_type: str
    latency_ms: float
    payload: dict[str, Any]
    timestamp: str
    trace_id: str
