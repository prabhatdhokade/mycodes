"""Technical specialist tools."""

from __future__ import annotations

from typing import Any

from .context import ToolContext


def run_diagnostics(context: ToolContext, customer_id: str) -> dict[str, Any]:
    """Run synthetic diagnostics for a customer."""
    health = context.service_status.get(customer_id, "degraded")
    packet_loss_pct = 8 if health != "healthy" else 0
    return {
        "customer_id": customer_id,
        "health": "warning" if packet_loss_pct else "ok",
        # Keep both keys for compatibility with test and agent formatting.
        "packet_loss": packet_loss_pct,
        "packet_loss_pct": packet_loss_pct,
        "detail": (
            "Packet loss detected on region edge"
            if packet_loss_pct
            else "No abnormalities found"
        ),
    }


def check_service_status(context: ToolContext, service: str) -> dict[str, Any]:
    """Check service status by service name."""
    status = "degraded" if service == "internet" else "operational"
    incident_id = "INC-784" if status != "operational" else "none"
    return {
        "service": service,
        "status": status,
        "region": "us-east-1",
        "incident_id": incident_id,
    }


def create_ticket(context: ToolContext, customer_id: str, issue: str) -> dict[str, Any]:
    """Create an escalation ticket."""
    ticket_id = f"TKT-{customer_id}-{len(context.ticket_store) + 1}"
    context.ticket_store[ticket_id] = {
        "customer_id": customer_id,
        "issue": issue,
        "status": "open",
    }
    return {"ticket_id": ticket_id, "status": "created"}

