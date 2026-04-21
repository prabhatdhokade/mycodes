from __future__ import annotations

from customer_support_system.data import CUSTOMERS, INVOICES, PAYMENTS


def get_invoice(customer_id: str) -> dict[str, object]:
    customer = CUSTOMERS[customer_id]
    invoice = INVOICES[customer_id]
    return {"customer": customer["name"], **invoice}


def get_payment_history(customer_id: str) -> dict[str, object]:
    return {"customer_id": customer_id, "payments": PAYMENTS[customer_id]}


def update_payment_method(customer_id: str, method: str = "Visa ending 4242") -> dict[str, object]:
    return {
        "customer_id": customer_id,
        "status": "updated",
        "payment_method": method,
    }
