from __future__ import annotations

from customer_support_system.data import ORDERS


def get_order_details(order_id: str) -> dict[str, object]:
    order = ORDERS[order_id]
    return {"order_id": order_id, **order}


def calculate_refund(order_id: str) -> dict[str, object]:
    order = ORDERS[order_id]
    if order["days_since_purchase"] <= 30:
        amount = round(order["amount"] * 0.8, 2)
    else:
        amount = 0.0
    return {"order_id": order_id, "refund_amount": amount, "eligible": amount > 0}


def process_refund(order_id: str, approved: bool) -> dict[str, object]:
    status = "processed" if approved else "awaiting_approval"
    return {"order_id": order_id, "status": status}
