"""Mock billing tools: invoices, payment history, payment method updates."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict

from .registry import Tool, ToolRegistry, ToolResult

# Deterministic mock data seeded by customer_id so tests are stable.
_INVOICES: Dict[str, list] = {
    "cust_001": [
        {"invoice_id": "INV-1001", "amount": 29.00, "status": "paid", "due": "2026-01-01"},
        {"invoice_id": "INV-1002", "amount": 29.00, "status": "paid", "due": "2026-02-01"},
        {"invoice_id": "INV-1003", "amount": 29.00, "status": "open", "due": "2026-03-01"},
    ],
    "cust_002": [
        {"invoice_id": "INV-2001", "amount": 9.00, "status": "paid", "due": "2026-02-01"},
    ],
}

_PAYMENTS: Dict[str, list] = {
    "cust_001": [
        {"payment_id": "PAY-9001", "amount": 29.00, "method": "visa-4242", "date": "2026-01-03"},
        {"payment_id": "PAY-9002", "amount": 29.00, "method": "visa-4242", "date": "2026-02-02"},
    ],
    "cust_002": [
        {"payment_id": "PAY-9101", "amount": 9.00, "method": "paypal", "date": "2026-02-01"},
    ],
}

_PAYMENT_METHODS: Dict[str, str] = {
    "cust_001": "visa-4242",
    "cust_002": "paypal",
}


def get_invoice(customer_id: str, invoice_id: str | None = None) -> ToolResult:
    invoices = _INVOICES.get(customer_id, [])
    if invoice_id:
        matches = [i for i in invoices if i["invoice_id"] == invoice_id]
        if not matches:
            return ToolResult(ok=False, error=f"Invoice {invoice_id} not found")
        return ToolResult(ok=True, data=matches[0])
    if not invoices:
        return ToolResult(ok=True, data={"invoices": [], "message": "No invoices on file."})
    latest = sorted(invoices, key=lambda i: i["due"], reverse=True)[0]
    return ToolResult(ok=True, data={"invoices": invoices, "latest": latest})


def get_payment_history(customer_id: str, limit: int = 10) -> ToolResult:
    payments = _PAYMENTS.get(customer_id, [])
    return ToolResult(ok=True, data={"payments": payments[:limit], "count": len(payments)})


def update_payment_method(customer_id: str, new_method: str) -> ToolResult:
    if not new_method or len(new_method) < 3:
        return ToolResult(ok=False, error="Invalid payment method identifier.")
    old = _PAYMENT_METHODS.get(customer_id)
    _PAYMENT_METHODS[customer_id] = new_method
    return ToolResult(
        ok=True,
        data={
            "customer_id": customer_id,
            "old_method": old,
            "new_method": new_method,
            "effective": datetime.now(timezone.utc).isoformat(),
        },
    )


def register(registry: ToolRegistry) -> None:
    registry.register(
        Tool(
            name="get_invoice",
            description="Retrieve a specific invoice or the most recent invoice for a customer.",
            fn=get_invoice,
            owner_agent="billing",
            parameters={"customer_id": "string", "invoice_id": "string?"},
        )
    )
    registry.register(
        Tool(
            name="get_payment_history",
            description="Retrieve the customer's payment history.",
            fn=get_payment_history,
            owner_agent="billing",
            parameters={"customer_id": "string", "limit": "int?"},
        )
    )
    registry.register(
        Tool(
            name="update_payment_method",
            description="Update the default payment method on file for a customer.",
            fn=update_payment_method,
            owner_agent="billing",
            parameters={"customer_id": "string", "new_method": "string"},
        )
    )
