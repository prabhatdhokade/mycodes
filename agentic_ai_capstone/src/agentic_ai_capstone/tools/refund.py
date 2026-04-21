"""Refund specialist tools."""

from __future__ import annotations

from typing import Dict

from .context import ToolContext


def get_order_details(
    context: ToolContext,
    customer_id: str,
    order_id: str,
) -> Dict[str, object]:
    orders = context.orders.get(customer_id, {})
    order = orders.get(order_id)
    if not order:
        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_total": 0.0,
            "currency": "USD",
            "status": "not_found",
        }
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "order_total": float(order["order_total"]),
        "currency": "USD",
        "status": str(order["status"]),
    }


def calculate_refund(order_total: float, reason: str) -> Dict[str, float]:
    fee = 0.0 if reason in {"service_outage", "duplicate_charge"} else round(order_total * 0.1, 2)
    eligible_amount = max(0.0, round(order_total - fee, 2))
    return {"order_total": order_total, "fee": fee, "eligible_amount": eligible_amount}


def process_refund(
    context: ToolContext,
    order_id: str,
    amount: float,
    approved_by_human: bool,
) -> Dict[str, object]:
    if amount > 50.0 and not approved_by_human:
        return {"order_id": order_id, "amount": amount, "status": "blocked", "reason": "approval_required"}
    context.refunds.append(
        {
            "order_id": order_id,
            "amount": round(amount, 2),
            "approved_by_human": approved_by_human,
        }
    )
    return {"order_id": order_id, "amount": round(amount, 2), "status": "processed"}
