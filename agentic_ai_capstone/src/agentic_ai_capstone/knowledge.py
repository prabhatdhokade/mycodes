"""Static knowledge base for policy and product documentation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KnowledgeBase:
    entries: dict[str, str] = field(
        default_factory=lambda: {
            "billing": (
                "Billing policy: invoices are generated monthly, "
                "and payment methods can be updated via secure tokenization."
            ),
            "technical": (
                "Technical support flow: run diagnostics, verify service status, "
                "and create escalation tickets if unresolved."
            ),
            "refund": (
                "Refund policy: refunds are eligible within 30 days. "
                "Amounts greater than $50 require human-in-the-loop approval."
            ),
        }
    )

    def lookup(self, domain: str) -> str:
        return self.entries.get(domain, "No matching article found.")
