"""Technical support specialist agent."""
from __future__ import annotations

import re
from typing import Any, Dict

from ..state import CustomerSupportState
from .base import AgentResponse, BaseAgent

TECHNICAL_SYSTEM = (
    "You are the Technical Support specialist. You help customers with app "
    "crashes, login issues, service status, and troubleshooting. Use your "
    "tools: run_diagnostics, check_service_status, create_ticket."
)


class TechnicalAgent(BaseAgent):
    name = "technical"
    description = "Handles crashes, diagnostics, service outages, and tickets."
    system_prompt = TECHNICAL_SYSTEM

    def handle(
        self, state: CustomerSupportState, user_message: str
    ) -> AgentResponse:
        with self._trace_agent(state, {"message": user_message[:400]}):
            text = user_message.lower()
            customer_id = state.get("customer_id", "cust_unknown")
            tool_calls = []

            if "status" in text or "outage" in text or "down" in text:
                service = _extract_service(user_message)
                res = self._run_tool(
                    "check_service_status", {"service": service or "all"}, state
                )
                tool_calls.append({"name": "check_service_status", "result": res.data, "ok": res.ok})
                if not res.ok:
                    return AgentResponse(
                        agent=self.name,
                        text=f"I couldn't check service status: {res.error}",
                        tool_calls=tool_calls,
                    )
                if service:
                    reply = (
                        f"Current status of {service}: {res.data['status']}. "
                        f"You can view live status at status.example.com."
                    )
                else:
                    parts = [f"{k}: {v}" for k, v in res.data["services"].items()]
                    reply = "Current service status — " + ", ".join(parts) + "."
                return AgentResponse(
                    agent=self.name, text=reply, tool_calls=tool_calls
                )

            if (
                "create ticket" in text
                or "open ticket" in text
                or "create a ticket" in text
                or "open a ticket" in text
                or "escalate" in text
                or "raise ticket" in text
                or "raise a ticket" in text
            ):
                priority = "high" if "urgent" in text or "critical" in text else "normal"
                res = self._run_tool(
                    "create_ticket",
                    {
                        "customer_id": customer_id,
                        "subject": _first_sentence(user_message),
                        "description": user_message,
                        "priority": priority,
                    },
                    state,
                )
                tool_calls.append({"name": "create_ticket", "result": res.data, "ok": res.ok})
                if not res.ok:
                    return AgentResponse(
                        agent=self.name,
                        text=f"I couldn't create a ticket: {res.error}",
                        tool_calls=tool_calls,
                    )
                ticket_id = res.data["ticket_id"]
                reply = (
                    f"I've opened ticket {ticket_id} ({priority} priority). "
                    f"Our engineering team will follow up shortly."
                )
                return AgentResponse(
                    agent=self.name,
                    text=reply,
                    tool_calls=tool_calls,
                    metadata={"ticket_id": ticket_id},
                )

            # Default: run diagnostics
            component = _extract_component(user_message) or "app"
            res = self._run_tool(
                "run_diagnostics",
                {"customer_id": customer_id, "component": component},
                state,
            )
            tool_calls.append({"name": "run_diagnostics", "result": res.data, "ok": res.ok})
            if not res.ok:
                return AgentResponse(
                    agent=self.name,
                    text=f"I couldn't run diagnostics: {res.error}",
                    tool_calls=tool_calls,
                )
            data = res.data
            if data["healthy"]:
                reply = (
                    f"Diagnostics on {component} look healthy "
                    f"(CPU {data['cpu_pct']}%, memory {data['memory_pct']}%, "
                    f"network {data['network_ms']}ms). If you're still seeing "
                    f"issues I can open a ticket for the engineering team."
                )
            else:
                issues = ", ".join(data["issues"])
                reply = (
                    f"Diagnostics on {component} detected: {issues} "
                    f"(CPU {data['cpu_pct']}%, memory {data['memory_pct']}%, "
                    f"network {data['network_ms']}ms). I can escalate this as "
                    f"a ticket — just say 'create ticket'."
                )
            return AgentResponse(
                agent=self.name, text=reply, tool_calls=tool_calls
            )


def _first_sentence(text: str) -> str:
    m = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)
    return m[0][:120] if m else text[:120]


def _extract_service(text: str) -> str | None:
    for svc in ("api", "dashboard", "billing", "auth"):
        if svc in text.lower():
            return svc
    return None


def _extract_component(text: str) -> str | None:
    for comp in ("app", "mobile", "web", "api", "database", "dashboard"):
        if comp in text.lower():
            return comp
    return None
