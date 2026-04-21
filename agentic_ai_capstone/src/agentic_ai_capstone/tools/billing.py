"""Billing specialist tools."""

from __future__ import annotations

from typing import Any

from .context import ToolContext


def get_invoice(context: ToolContext, customer_id: str, invoice_id: str) -> dict[str, Any]:
    invoice = context.invoice_store.get(customer_id)
    if not invoice:
        return {"invoice_id": invoice_id, "amount_due": 0.0, "status": "not_found"}
    return invoice


def get_payment_history(context: ToolContext, customer_id: str) -> list[dict[str, Any]]:
    return context.payment_history.get(
        customer_id,
        [{"payment_id": "pay-demo", "amount": 0.0, "method": "none", "date": "n/a"}],
    )


def update_payment_method(
    context: ToolContext,
    customer_id: str,
    payment_token: str,
) -> dict[str, Any]:
    context.payment_methods[customer_id] = payment_token[-4:]
    return {"customer_id": customer_id, "status": "updated", "last4": payment_token[-4:]}
