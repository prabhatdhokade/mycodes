"""Triage/Supervisor agent: classify and route incoming queries."""
from __future__ import annotations

from typing import Optional

from ..observability import get_tracer
from ..state import CustomerSupportState
from .base import AgentResponse, BaseAgent

TRIAGE_SYSTEM = (
    "You are the Triage Supervisor for a customer support system. Your job "
    "is to classify incoming queries and route them to the correct specialist. "
    "Valid routes: billing, technical, refund, triage (if unclear). "
    "Respond with exactly 'ROUTE: <category>'."
)


class TriageAgent(BaseAgent):
    name = "triage"
    description = "Classifies queries and routes to the appropriate specialist."
    system_prompt = TRIAGE_SYSTEM

    def classify(self, text: str, trace_id: str) -> str:
        tracer = get_tracer()
        with tracer.span(
            "router.triage.classify",
            "router",
            trace_id=trace_id,
            inputs={"text": text[:400]},
        ) as span:
            resp = self.llm.complete(
                system=TRIAGE_SYSTEM + "\n(Task: classify)",
                user=text,
                trace_id=trace_id,
                temperature=0.0,
            )
            out = (resp.text or "").strip()
            route = "triage"
            for cand in ("billing", "technical", "refund", "triage"):
                if f"ROUTE: {cand}" in out or f"route: {cand}" in out.lower():
                    route = cand
                    break
            span.outputs = {"route": route, "raw": out[:200]}
            return route

    def handle(
        self, state: CustomerSupportState, user_message: str
    ) -> AgentResponse:
        with self._trace_agent(state, {"message": user_message[:400]}):
            route = self.classify(user_message, state.get("trace_id", "trace_anon"))
            if route == "triage":
                return AgentResponse(
                    agent=self.name,
                    text=(
                        "I'd like to make sure I route you to the right team. "
                        "Could you tell me if this is about billing, a technical "
                        "issue, or a refund/return?"
                    ),
                )
            return AgentResponse(
                agent=self.name,
                text=f"Routing you to our {route} specialist now.",
                handoff_to=route,
                metadata={"classification": route},
            )
