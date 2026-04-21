from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.agents.base import BaseAgent
from customer_support_system.tools.registry import ToolRegistry


@dataclass
class RefundAgent(BaseAgent):
    registry: ToolRegistry

    def _extract_order_id(self, user_input: str, memory: dict[str, object]) -> str:
        for token in user_input.replace(",", " ").split():
            cleaned = token.strip(".,!?;:()[]{}")
            if cleaned.startswith("ORD-"):
                return cleaned
        return str(memory.get("last_order_id") or "ORD-001")

    def handle(self, customer_id: str, user_input: str, memory: dict[str, object], approval_granted: bool) -> dict[str, object]:
        order_id = self._extract_order_id(user_input, memory)
        details = self.registry.call("get_order_details", order_id=order_id)
        self.recorder.tool_call("get_order_details", {"order_id": order_id}, details)
        calculation = self.registry.call("calculate_refund", order_id=order_id)
        self.recorder.tool_call("calculate_refund", {"order_id": order_id}, calculation)
        outputs = [details, calculation]
        knowledge = self.knowledge(user_input)
        if calculation["refund_amount"] > 50 and not approval_granted:
            pending = {
                "type": "refund_approval",
                "order_id": order_id,
                "refund_amount": calculation["refund_amount"],
            }
            response = (
                f"Refund for order {order_id} is eligible for ${calculation['refund_amount']:.2f}, "
                "but human approval is required before processing."
            )
            response += f" Policy note: {knowledge[1]}"
            return {
                "response": response,
                "tool_outputs": outputs,
                "approval_required": True,
                "pending_actions": [pending],
                "order_id": order_id,
            }
        processed = self.registry.call("process_refund", order_id=order_id, approved=True)
        self.recorder.tool_call("process_refund", {"order_id": order_id, "approved": True}, processed)
        outputs.append(processed)
        response = (
            f"Refund for order {order_id} has been {processed['status']} for ${calculation['refund_amount']:.2f} "
            "to the original payment method."
        )
        response += f" Policy note: {knowledge[0]}"
        return {
            "response": response,
            "tool_outputs": outputs,
            "approval_required": False,
            "pending_actions": [],
            "order_id": order_id,
        }
