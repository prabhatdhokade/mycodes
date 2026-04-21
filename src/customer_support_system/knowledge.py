from __future__ import annotations

KNOWLEDGE_BASE = {
    "billing": [
        "Invoices close on the 10th of each month and overdue balances trigger reminders after 3 days.",
        "Payment method updates become active immediately for future invoices.",
        "Pro plan customers can request invoice PDFs by email.",
    ],
    "technical": [
        "Degraded service should trigger diagnostics before opening a ticket.",
        "Tickets include service status, recent incidents, and customer contact preference.",
        "Latency above 250 ms is considered degraded for this support workflow.",
    ],
    "refund": [
        "Orders under 30 days are eligible for prorated refunds.",
        "Refunds above $50 require human approval before processing.",
        "Processed refunds are returned to the original payment method.",
    ],
}


def retrieve_knowledge(domain: str, query: str) -> list[str]:
    snippets = KNOWLEDGE_BASE.get(domain, [])
    lowered = query.lower()
    ranked = sorted(
        snippets,
        key=lambda snippet: sum(1 for token in lowered.split() if token in snippet.lower()),
        reverse=True,
    )
    return ranked[:2]
