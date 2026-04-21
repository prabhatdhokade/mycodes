"""Shared state schema for the customer support multi-agent system.

Mirrors the LangGraph `TypedDict` pattern from the capstone spec so that the
same state object can be consumed by a LangGraph StateGraph or by our own
in-process orchestrator.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict


class Message(TypedDict, total=False):
    """A single chat message in the conversation history."""

    role: str  # "user" | "assistant" | "system" | "tool" | "human"
    content: str
    agent: Optional[str]
    metadata: Dict[str, Any]


def add_messages(existing: List[Message], new: List[Message]) -> List[Message]:
    """Reducer used by LangGraph-style state updates. Appends new messages."""
    if not existing:
        existing = []
    if not new:
        return existing
    return [*existing, *new]


class CustomerSupportState(TypedDict, total=False):
    """Canonical state schema for the customer support system."""

    messages: List[Message]
    customer_id: str
    current_agent: str
    ticket_id: Optional[str]
    conversation_summary: str
    pending_actions: List[Dict[str, Any]]
    guardrail_flags: List[Dict[str, Any]]
    trace_id: str
    hitl_required: bool
    hitl_decision: Optional[str]  # "approve" | "deny" | None
    metadata: Dict[str, Any]


@dataclass
class PendingAction:
    """Represents an action queued for HITL approval."""

    action_id: str
    tool: str
    arguments: Dict[str, Any]
    reason: str
    status: str = "pending"  # pending | approved | denied | executed
    result: Optional[Any] = None


@dataclass
class GuardrailFlag:
    """Structured record of a guardrail event."""

    kind: str  # "injection" | "pii" | "toxicity" | "policy"
    severity: str  # "low" | "medium" | "high"
    detail: str
    direction: str  # "input" | "output"
    sample: str = ""


def new_state(
    customer_id: str,
    trace_id: str,
    initial_agent: str = "triage",
) -> CustomerSupportState:
    """Create a fresh state dictionary with sensible defaults."""
    return CustomerSupportState(
        messages=[],
        customer_id=customer_id,
        current_agent=initial_agent,
        ticket_id=None,
        conversation_summary="",
        pending_actions=[],
        guardrail_flags=[],
        trace_id=trace_id,
        hitl_required=False,
        hitl_decision=None,
        metadata={},
    )
