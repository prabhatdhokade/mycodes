from __future__ import annotations

import operator
from typing import Annotated, Any, Optional, TypedDict


class CustomerSupportState(TypedDict, total=False):
    messages: Annotated[list[dict[str, str]], operator.add]
    customer_id: str
    current_agent: str
    ticket_id: Optional[str]
    conversation_summary: str
    pending_actions: list[dict[str, Any]]
    guardrail_flags: list[str]
    traces: list[dict[str, Any]]
    model_costs: list[dict[str, Any]]
    last_response: str
    route: str
    user_input: str
    sanitized_input: str
    blocked: bool
    memory: dict[str, Any]
    approval_required: bool
    approval_granted: bool
    tool_outputs: list[dict[str, Any]]
    order_id: Optional[str]
