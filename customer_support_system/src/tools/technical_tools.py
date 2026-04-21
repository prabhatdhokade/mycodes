"""Mock technical support tools: diagnostics, status checks, ticket creation."""
from __future__ import annotations

import hashlib
import random
import time
from typing import Dict

from .registry import Tool, ToolRegistry, ToolResult

_SERVICE_STATUS: Dict[str, str] = {
    "api": "operational",
    "dashboard": "operational",
    "billing": "operational",
    "auth": "degraded",
}

_TICKET_COUNTER = {"n": 500}


def run_diagnostics(customer_id: str, component: str = "app") -> ToolResult:
    seed = int(hashlib.md5(f"{customer_id}:{component}".encode()).hexdigest(), 16)
    rng = random.Random(seed)
    cpu = round(rng.uniform(5, 95), 1)
    mem = round(rng.uniform(10, 90), 1)
    net_ms = round(rng.uniform(15, 400), 1)
    issues = []
    if cpu > 85:
        issues.append("high_cpu")
    if mem > 85:
        issues.append("high_memory")
    if net_ms > 300:
        issues.append("network_latency")
    return ToolResult(
        ok=True,
        data={
            "component": component,
            "cpu_pct": cpu,
            "memory_pct": mem,
            "network_ms": net_ms,
            "issues": issues,
            "healthy": not issues,
        },
    )


def check_service_status(service: str = "all") -> ToolResult:
    if service == "all":
        return ToolResult(ok=True, data={"services": dict(_SERVICE_STATUS)})
    if service not in _SERVICE_STATUS:
        return ToolResult(ok=False, error=f"Unknown service: {service}")
    return ToolResult(
        ok=True, data={"service": service, "status": _SERVICE_STATUS[service]}
    )


def create_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: str = "normal",
) -> ToolResult:
    if priority not in {"low", "normal", "high", "urgent"}:
        return ToolResult(ok=False, error=f"Invalid priority: {priority}")
    _TICKET_COUNTER["n"] += 1
    ticket_id = f"TCK-{_TICKET_COUNTER['n']:05d}"
    return ToolResult(
        ok=True,
        data={
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "created_at": int(time.time()),
            "status": "open",
        },
    )


def register(registry: ToolRegistry) -> None:
    registry.register(
        Tool(
            name="run_diagnostics",
            description="Run health diagnostics on a component (cpu/memory/network).",
            fn=run_diagnostics,
            owner_agent="technical",
            parameters={"customer_id": "string", "component": "string?"},
        )
    )
    registry.register(
        Tool(
            name="check_service_status",
            description="Check current service status (api, dashboard, billing, auth, or 'all').",
            fn=check_service_status,
            owner_agent="technical",
            parameters={"service": "string?"},
        )
    )
    registry.register(
        Tool(
            name="create_ticket",
            description="Create a technical support ticket and assign a ticket id.",
            fn=create_ticket,
            owner_agent="technical",
            parameters={
                "customer_id": "string",
                "subject": "string",
                "description": "string",
                "priority": "string?",
            },
        )
    )
