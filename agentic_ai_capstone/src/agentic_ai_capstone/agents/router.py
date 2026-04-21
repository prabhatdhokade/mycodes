from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..memory.store import MemoryStore
from ..observability.tracer import Tracer
from ..state import CustomerSupportState, append_message, latest_user_message

Route = Literal["billing", "technical", "refund", "triage"]


@dataclass(frozen=True)
class RoutingResult:
    route: Route
    confidence: float
    reason: str


class TriageRouter:
    """Deterministic triage router with high-precision keyword matching."""

    def classify(self, text: str) -> RoutingResult:
        content = text.lower()
        if any(k in content for k in ("refund", "return", "money back", "chargeback")):
            return RoutingResult("refund", 0.97, "refund intent")
        if any(k in content for k in ("ticket", "escalate", "cannot connect", "can't connect")):
            return RoutingResult("technical", 0.95, "technical escalation intent")
        if any(k in content for k in ("invoice", "payment", "billing", "plan", "card")):
            return RoutingResult("billing", 0.94, "billing intent")
        if any(
            k in content
            for k in (
                "error",
                "issue",
                "bug",
                "latency",
                "outage",
                "cannot login",
                "can't login",
                "diagnostic",
                "slow",
                "status",
                "service down",
            )
        ):
            return RoutingResult("technical", 0.95, "technical intent")
        return RoutingResult("triage", 0.55, "fallback triage")


def triage_agent(
    state: CustomerSupportState,
    tracer: Tracer,
    memory_store: MemoryStore,
) -> CustomerSupportState:
    user_text = latest_user_message(state)
    result = TriageRouter().classify(user_text)
    state["current_agent"] = result.route
    state["metadata"]["routing_confidence"] = result.confidence
    state["metadata"]["routing_reason"] = result.reason
    memory_store.append_message(state["customer_id"], f"triage:{result.route}")
    tracer.record("triage_agent", "route", user_text, f"{result.route}:{result.confidence}")

    if result.route == "triage":
        append_message(
            state,
            "assistant",
            "I can help with billing, technical issues, or refunds. Please share more detail.",
        )
    return state
