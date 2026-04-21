from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class TraceRecorder:
    events: list[dict[str, Any]] = field(default_factory=list)
    costs: list[dict[str, Any]] = field(default_factory=list)

    def event(self, kind: str, name: str, payload: dict[str, Any]) -> None:
        self.events.append(
            {
                "timestamp": utc_now(),
                "kind": kind,
                "name": name,
                "payload": payload,
            }
        )

    def llm_call(self, model: str, prompt: str, response: str, purpose: str) -> None:
        input_tokens = max(1, len(prompt.split()))
        output_tokens = max(1, len(response.split()))
        cost = round((input_tokens / 1000 * 0.0015) + (output_tokens / 1000 * 0.0025), 6)
        record = {
            "timestamp": utc_now(),
            "model": model,
            "purpose": purpose,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": cost,
        }
        self.costs.append(record)
        self.event(
            kind="llm",
            name=purpose,
            payload={
                "model": model,
                "prompt": prompt,
                "response": response,
                "estimated_cost_usd": cost,
            },
        )

    def tool_call(self, tool_name: str, arguments: dict[str, Any], result: dict[str, Any]) -> None:
        self.event("tool", tool_name, {"arguments": arguments, "result": result})

    def guardrail(self, name: str, result: dict[str, Any]) -> None:
        self.event("guardrail", name, result)

    def memory(self, action: str, payload: dict[str, Any]) -> None:
        self.event("memory", action, payload)

    def snapshot(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return list(self.events), list(self.costs)
