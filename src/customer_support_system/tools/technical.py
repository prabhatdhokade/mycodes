from __future__ import annotations

from customer_support_system.data import CUSTOMERS, SERVICES


def run_diagnostics(customer_id: str) -> dict[str, object]:
    service = SERVICES[CUSTOMERS[customer_id]["service_id"]]
    diagnosis = "healthy" if service["latency_ms"] < 250 else "network_degradation"
    return {"customer_id": customer_id, "diagnosis": diagnosis, "latency_ms": service["latency_ms"]}


def check_service_status(customer_id: str) -> dict[str, object]:
    service = SERVICES[CUSTOMERS[customer_id]["service_id"]]
    return {"customer_id": customer_id, **service}


def create_ticket(customer_id: str, summary: str) -> dict[str, object]:
    ticket_id = f"TICK-{customer_id[-3:]}-{len(summary)}"
    return {"customer_id": customer_id, "ticket_id": ticket_id, "status": "open", "summary": summary}
