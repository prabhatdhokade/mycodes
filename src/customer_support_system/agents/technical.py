from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.agents.base import BaseAgent
from customer_support_system.tools.registry import ToolRegistry


@dataclass
class TechnicalAgent(BaseAgent):
    registry: ToolRegistry

    def handle(self, customer_id: str, user_input: str, memory: dict[str, object]) -> dict[str, object]:
        diagnostics = self.registry.call("run_diagnostics", customer_id=customer_id)
        self.recorder.tool_call("run_diagnostics", {"customer_id": customer_id}, diagnostics)
        status = self.registry.call("check_service_status", customer_id=customer_id)
        self.recorder.tool_call("check_service_status", {"customer_id": customer_id}, status)
        outputs = [diagnostics, status]
        ticket = None
        if diagnostics["diagnosis"] != "healthy" or "ticket" in user_input.lower() or "escalate" in user_input.lower():
            ticket = self.registry.call("create_ticket", customer_id=customer_id, summary=user_input)
            self.recorder.tool_call("create_ticket", {"customer_id": customer_id, "summary": user_input}, ticket)
            outputs.append(ticket)
        knowledge = self.knowledge(user_input)
        response = (
            f"Technical support checked service status: {status['status']} with {status['latency_ms']} ms latency. "
            f"Diagnostics classified the issue as {diagnostics['diagnosis']}."
        )
        if ticket:
            response += f" Ticket {ticket['ticket_id']} has been opened and will use {memory['preferences']['preferred_contact']} updates."
        response += f" Runbook note: {knowledge[0]}"
        return {"response": response, "tool_outputs": outputs, "ticket_id": ticket['ticket_id'] if ticket else None}
