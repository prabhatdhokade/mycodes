CUSTOMERS = {
    "CUST-001": {
        "name": "Avery Brooks",
        "plan": "pro",
        "preferred_contact": "email",
        "email": "avery@example.com",
        "phone": "+1 555 123 4567",
        "last_invoice_id": "INV-1001",
        "service_id": "SVC-001",
    },
    "CUST-002": {
        "name": "Jordan Lee",
        "plan": "starter",
        "preferred_contact": "sms",
        "email": "jordan@example.com",
        "phone": "+1 555 222 3333",
        "last_invoice_id": "INV-1002",
        "service_id": "SVC-002",
    },
}

INVOICES = {
    "CUST-001": {
        "invoice_id": "INV-1001",
        "amount_due": 129.99,
        "status": "paid",
        "due_date": "2026-04-10",
    },
    "CUST-002": {
        "invoice_id": "INV-1002",
        "amount_due": 49.00,
        "status": "overdue",
        "due_date": "2026-04-14",
    },
}

PAYMENTS = {
    "CUST-001": [
        {"date": "2026-03-10", "amount": 129.99, "status": "settled"},
        {"date": "2026-02-10", "amount": 129.99, "status": "settled"},
    ],
    "CUST-002": [
        {"date": "2026-03-14", "amount": 49.00, "status": "failed"},
        {"date": "2026-02-14", "amount": 49.00, "status": "settled"},
    ],
}

SERVICES = {
    "SVC-001": {"status": "operational", "latency_ms": 42, "last_incident": None},
    "SVC-002": {"status": "degraded", "latency_ms": 315, "last_incident": "INC-204"},
}

ORDERS = {
    "ORD-001": {"customer_id": "CUST-001", "product": "Annual Pro Plan", "days_since_purchase": 14, "amount": 120.00},
    "ORD-002": {"customer_id": "CUST-002", "product": "Starter Add-on", "days_since_purchase": 4, "amount": 40.00},
}
