"""Shared state schema and state helper functions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, TypedDict


class CustomerSupportState(TypedDict):
    """
    Runtime state aligned with the required schema:

    class CustomerSupportState(TypedDict):
        messages: Annotated[list, add_messages]
        customer_id: str
        current_agent: str
        ticket_id: Optional[str]
        conversation_summary: str
        pending_actions: list
        guardrail_flags: list
    """

    messages: list[dict[str, Any]]
    customer_id: str
    current_agent: str
    ticket_id: Optional[str]
    conversation_summary: str
    pending_actions: list[str]
    guardrail_flags: list[str]
    context: dict[str, Any]
    metadata: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_state(
    customer_id: str,
    ticket_id: str | None = None,
    conversation_summary: str = "",
    context: dict[str, Any] | None = None,
) -> CustomerSupportState:
    return CustomerSupportState(
        messages=[],
        customer_id=customer_id,
        current_agent="triage",
        ticket_id=ticket_id,
        conversation_summary=conversation_summary,
        pending_actions=[],
        guardrail_flags=[],
        context=context or {},
        metadata={},
    )


def append_message(state: CustomerSupportState, role: str, content: str) -> None:
    state["messages"].append(
        {
            "role": role,
            "content": content,
            "timestamp_utc": utc_now(),
        }
    )


def latest_user_message(state: CustomerSupportState) -> str:
    for message in reversed(state["messages"]):
        if message.get("role") in {"user", "customer"}:
            return str(message.get("content", ""))
    return ""
