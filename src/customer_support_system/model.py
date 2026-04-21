from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.tracing import TraceRecorder


@dataclass
class DeterministicSupportModel:
    recorder: TraceRecorder
    model_name: str = "deterministic-support-model"

    def route(self, user_text: str) -> str:
        text = user_text.lower()
        if any(keyword in text for keyword in ["refund", "return", "chargeback", "cancel order"]):
            decision = "refund"
        elif any(
            keyword in text
            for keyword in [
                "invoice",
                "payment",
                "billing",
                "card",
                "plan",
                "contact method",
                "contact preference",
                "email",
                "sms",
            ]
        ):
            decision = "billing"
        else:
            decision = "technical"
        self.recorder.llm_call(self.model_name, f"route::{user_text}", decision, "triage_route")
        return decision

    def summarize(self, user_text: str, memory_hint: str) -> str:
        summary = f"Last request: {user_text.strip()} | Context: {memory_hint.strip()}".strip()
        self.recorder.llm_call(self.model_name, f"summary::{user_text}::{memory_hint}", summary, "conversation_summary")
        return summary
