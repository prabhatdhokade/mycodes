from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.agents.base import BaseAgent
from customer_support_system.tools.registry import ToolRegistry


@dataclass
class BillingAgent(BaseAgent):
    registry: ToolRegistry

    def handle(self, customer_id: str, user_input: str, memory: dict[str, object]) -> dict[str, object]:
        invoice = self.registry.call("get_invoice", customer_id=customer_id)
        self.recorder.tool_call("get_invoice", {"customer_id": customer_id}, invoice)
        history = self.registry.call("get_payment_history", customer_id=customer_id)
        self.recorder.tool_call("get_payment_history", {"customer_id": customer_id}, history)
        outputs = [invoice, history]
        payment_update = None
        if "update" in user_input.lower() or "card" in user_input.lower():
            payment_update = self.registry.call("update_payment_method", customer_id=customer_id)
            self.recorder.tool_call("update_payment_method", {"customer_id": customer_id}, payment_update)
            outputs.append(payment_update)
        knowledge = self.knowledge(user_input)
        response = (
            f"Billing update for {invoice['customer']}: invoice {invoice['invoice_id']} is {invoice['status']} "
            f"for ${invoice['amount_due']:.2f}. Recent payments reviewed: {len(history['payments'])}."
        )
        if payment_update:
            response += f" Payment method {payment_update['payment_method']} has been updated."
        response += f" Preference on file: {memory['preferences']['preferred_contact']}."
        response += f" Policy note: {knowledge[0]}"
        return {"response": response, "tool_outputs": outputs}
