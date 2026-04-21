# State Schema

The `CustomerSupportState` dict matches the capstone spec and is designed for
LangGraph compatibility.

```python
from typing import TypedDict, Annotated, Optional, List, Dict, Any

class CustomerSupportState(TypedDict, total=False):
    messages: List[Dict]            # with `add_messages` reducer semantics
    customer_id: str
    current_agent: str              # "triage" | "billing" | "technical" | "refund"
    ticket_id: Optional[str]
    conversation_summary: str
    pending_actions: List[Dict]     # HITL queue
    guardrail_flags: List[Dict]
    trace_id: str
    hitl_required: bool
    hitl_decision: Optional[str]    # "approve" | "deny" | None
    metadata: Dict[str, Any]
```

## `messages`

List of `{"role": "user"|"assistant"|"tool"|"system", "content": str, "agent": Optional[str]}`.
Managed by `orchestrator.Orchestrator.step` and reduced via `add_messages` in
the LangGraph adapter (concatenation).

## `guardrail_flags`

Each entry is a structured record, e.g.

```json
{
  "kind": "injection" | "pii" | "toxicity" | "policy",
  "severity": "low" | "medium" | "high",
  "direction": "input" | "output",
  "detail": "human readable reason",
  "turn": "input" | "output" | "output_post_hitl"
}
```

## `pending_actions`

```json
{
  "action_id": "act_<id>",
  "tool": "process_refund",
  "arguments": { ... },
  "amount": 158.00,
  "order_id": "ORD-5002",
  "status": "pending" | "approved" | "denied" | "executed",
  "reason": "..."
}
```
