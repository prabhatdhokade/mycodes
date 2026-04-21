"""Shared mutable tool context for mock integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolContext:
    invoice_store: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "cust-1001": {"invoice_id": "inv-500", "amount_due": 79.99, "status": "open"},
            "cust-1002": {"invoice_id": "inv-501", "amount_due": 0.00, "status": "paid"},
        }
    )
    payment_history: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: {
            "cust-1001": [
                {"payment_id": "pay-1", "amount": 79.99, "method": "card", "date": "2026-04-01"}
            ],
            "cust-1002": [
                {"payment_id": "pay-2", "amount": 49.00, "method": "bank", "date": "2026-03-15"}
            ],
        }
    )
    payment_methods: dict[str, str] = field(
        default_factory=lambda: {"cust-1001": "4242", "cust-1002": "1000"}
    )
    service_status: dict[str, str] = field(
        default_factory=lambda: {"cust-1001": "degraded", "cust-1002": "healthy"}
    )
    ticket_store: dict[str, dict[str, Any]] = field(default_factory=dict)
    orders: dict[str, dict[str, dict[str, Any]]] = field(
        default_factory=lambda: {
            "cust-1001": {
                "ord-120": {"order_total": 39.0, "status": "delivered", "item": "Mouse"},
                "ord-121": {"order_total": 129.0, "status": "delivered", "item": "Headphones"},
            },
            "cust-1002": {
                "ord-220": {"order_total": 49.0, "status": "delivered", "item": "USB Hub"}
            },
            "cust-ref-low": {
                "ord-700": {"order_total": 40.0, "status": "delivered", "item": "Cable"}
            },
            "cust-ref-high": {
                "ord-701": {"order_total": 85.0, "status": "delivered", "item": "Keyboard"}
            },
        }
    )
    refunds: list[dict[str, Any]] = field(default_factory=list)
