"""Tracing and lightweight cost tracking utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class TraceEvent:
    component: str
    operation: str
    input_preview: str
    output_preview: str
    token_estimate: int
    cost_usd: float
    timestamp_utc: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "operation": self.operation,
            "input_preview": self.input_preview,
            "output_preview": self.output_preview,
            "token_estimate": self.token_estimate,
            "cost_usd": self.cost_usd,
            "timestamp_utc": self.timestamp_utc,
        }


@dataclass
class Tracer:
    """Collect trace events and summarize estimated model costs."""

    cost_per_1k_tokens: float = 0.002
    events: list[TraceEvent] = field(default_factory=list)

    def record(self, component: str, operation: str, input_text: str, output_text: str) -> TraceEvent:
        token_estimate = max(1, int((len(input_text) + len(output_text)) / 4))
        cost_usd = round((token_estimate / 1000.0) * self.cost_per_1k_tokens, 8)
        event = TraceEvent(
            component=component,
            operation=operation,
            input_preview=input_text[:240],
            output_preview=output_text[:240],
            token_estimate=token_estimate,
            cost_usd=cost_usd,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )
        self.events.append(event)
        return event

    def summary(self) -> dict[str, Any]:
        return {
            "llm_calls": len(self.events),
            "estimated_tokens": sum(item.token_estimate for item in self.events),
            "estimated_cost_usd": round(sum(item.cost_usd for item in self.events), 8),
            "events": [event.to_dict() for event in self.events],
        }
