"""Mock refund tools: order lookup, refund calculation, refund processing (HITL)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from .registry import Tool, ToolRegistry, ToolResult

HITL_THRESHOLD_USD = 50.0

def _recent(days_ago: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).date().isoformat()


_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-5001": {
        "order_id": "ORD-5001",
        "customer_id": "cust_001",
        "items": [{"sku": "WIDGET-A", "qty": 1, "price": 29.00}],
        "total": 29.00,
        "ordered_at": _recent(10),
        "delivered_at": _recent(7),
        "status": "delivered",
    },
    "ORD-5002": {
        "order_id": "ORD-5002",
        "customer_id": "cust_001",
        "items": [{"sku": "WIDGET-B", "qty": 2, "price": 79.00}],
        "total": 158.00,
        "ordered_at": _recent(8),
        "delivered_at": _recent(5),
        "status": "delivered",
    },
    "ORD-5003": {
        "order_id": "ORD-5003",
        "customer_id": "cust_002",
        "items": [{"sku": "GIZMO", "qty": 1, "price": 9.00}],
        "total": 9.00,
        "ordered_at": _recent(3),
        "delivered_at": None,
        "status": "shipped",
    },
    # Older order intentionally outside 30-day window for policy tests
    "ORD-5099": {
        "order_id": "ORD-5099",
        "customer_id": "cust_001",
        "items": [{"sku": "OLDIE", "qty": 1, "price": 19.00}],
        "total": 19.00,
        "ordered_at": _recent(120),
        "delivered_at": _recent(100),
        "status": "delivered",
    },
}


def get_order_details(order_id: str) -> ToolResult:
    order = _ORDERS.get(order_id)
    if not order:
        return ToolResult(ok=False, error=f"Order {order_id} not found")
    return ToolResult(ok=True, data=dict(order))


def calculate_refund(order_id: str, reason: str = "customer_request") -> ToolResult:
    order = _ORDERS.get(order_id)
    if not order:
        return ToolResult(ok=False, error=f"Order {order_id} not found")
    total = float(order["total"])

    delivered_at = order.get("delivered_at")
    eligible = True
    policy_notes = []

    if delivered_at:
        try:
            days = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(delivered_at).replace(tzinfo=timezone.utc)
            ).days
        except Exception:
            days = 0
        if days > 30:
            eligible = False
            policy_notes.append("Order delivered more than 30 days ago.")

    if reason == "damaged":
        refund_amount = round(total, 2)
        policy_notes.append("Damaged item: full refund.")
    elif reason == "partial":
        refund_amount = round(total * 0.5, 2)
        policy_notes.append("Partial refund: 50% of order total.")
    else:
        refund_amount = round(total, 2)
        policy_notes.append("Standard refund: full order total.")

    return ToolResult(
        ok=True,
        data={
            "order_id": order_id,
            "refund_amount": refund_amount,
            "eligible": eligible,
            "requires_hitl": refund_amount > HITL_THRESHOLD_USD,
            "policy_notes": policy_notes,
        },
    )


def process_refund(
    order_id: str,
    amount: float,
    reason: str = "customer_request",
) -> ToolResult:
    order = _ORDERS.get(order_id)
    if not order:
        return ToolResult(ok=False, error=f"Order {order_id} not found")
    amount = float(amount)
    if amount <= 0:
        return ToolResult(ok=False, error="Refund amount must be positive.")
    if amount > order["total"]:
        return ToolResult(
            ok=False,
            error=(
                f"Refund amount ${amount:.2f} exceeds order total "
                f"${order['total']:.2f}."
            ),
        )
    order = dict(order)
    order["status"] = "refunded"
    order["refund_amount"] = amount
    order["refund_reason"] = reason
    order["refunded_at"] = datetime.now(timezone.utc).isoformat()
    _ORDERS[order_id] = order
    return ToolResult(ok=True, data=order)


def register(registry: ToolRegistry) -> None:
    registry.register(
        Tool(
            name="get_order_details",
            description="Look up the details of a specific order.",
            fn=get_order_details,
            owner_agent="refund",
            parameters={"order_id": "string"},
        )
    )
    registry.register(
        Tool(
            name="calculate_refund",
            description="Calculate the refund amount given an order and a reason.",
            fn=calculate_refund,
            owner_agent="refund",
            parameters={"order_id": "string", "reason": "string?"},
        )
    )
    registry.register(
        Tool(
            name="process_refund",
            description=(
                f"Process a refund for an order. Refunds > ${HITL_THRESHOLD_USD:.0f} "
                "require human approval."
            ),
            fn=process_refund,
            owner_agent="refund",
            parameters={"order_id": "string", "amount": "number", "reason": "string?"},
            hitl_predicate=lambda args: float(args.get("amount", 0) or 0)
            > HITL_THRESHOLD_USD,
        )
    )
