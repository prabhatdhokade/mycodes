from __future__ import annotations

import json
from dataclasses import dataclass

from customer_support_system.system import CustomerSupportSystem

ROUTING_CASES = [
    ("Need a copy of my invoice.", "billing"),
    ("My payment failed and I need help.", "billing"),
    ("Please update the credit card on file.", "billing"),
    ("The app is down and I need diagnostics.", "technical"),
    ("Create a ticket for the service outage.", "technical"),
    ("My service is slow this morning.", "technical"),
    ("I want a refund for ORD-001.", "refund"),
    ("Can I return this order and get my money back?", "refund"),
    ("Chargeback question on order ORD-002.", "refund"),
    ("Can you explain my plan pricing?", "billing"),
]


@dataclass
class EvaluationSummary:
    routing_accuracy: float
    scenarios_passed: int
    scenarios_total: int

    def to_dict(self) -> dict[str, object]:
        return {
            "routing_accuracy": self.routing_accuracy,
            "scenarios_passed": self.scenarios_passed,
            "scenarios_total": self.scenarios_total,
        }


def run_evaluation() -> EvaluationSummary:
    system = CustomerSupportSystem()
    correct = 0
    for prompt, expected in ROUTING_CASES:
        result = system.handle_message("CUST-001", prompt)
        if result["current_agent"] == expected:
            correct += 1
    return EvaluationSummary(
        routing_accuracy=round(correct / len(ROUTING_CASES), 2),
        scenarios_passed=correct,
        scenarios_total=len(ROUTING_CASES),
    )


def main() -> None:
    summary = run_evaluation()
    print(json.dumps(summary.to_dict(), indent=2))


if __name__ == "__main__":
    main()
