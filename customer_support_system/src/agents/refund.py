"""Refund specialist agent with HITL gating on high-value refunds."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from ..state import CustomerSupportState
from ..tools.refund_tools import HITL_THRESHOLD_USD
from .base import AgentResponse, BaseAgent

REFUND_SYSTEM = (
    "You are the Refund specialist. You help customers return orders and "
    "process refunds according to policy. Refunds over $"
    f"{HITL_THRESHOLD_USD:.0f} require human approval. Use your tools: "
    "get_order_details, calculate_refund, process_refund."
)

_ORDER_RE = re.compile(r"ORD-\d{3,}", re.IGNORECASE)


class RefundAgent(BaseAgent):
    name = "refund"
    description = "Handles refunds, returns, and refund policy questions."
    system_prompt = REFUND_SYSTEM

    def handle(
        self, state: CustomerSupportState, user_message: str
    ) -> AgentResponse:
        with self._trace_agent(state, {"message": user_message[:400]}):
            text = user_message.lower()
            tool_calls = []

            if "policy" in text or "policies" in text:
                reply = (
                    "Refunds are available within 30 days of delivery. "
                    f"Refunds over ${HITL_THRESHOLD_USD:.0f} require manager "
                    "approval. Damaged items are fully refundable. Digital "
                    "goods are non-refundable after activation."
                )
                return AgentResponse(agent=self.name, text=reply)

            order_id = _extract_order_id(user_message)
            if not order_id:
                return AgentResponse(
                    agent=self.name,
                    text=(
                        "I can help with a refund. Could you share your order "
                        "number (format ORD-####) so I can look it up?"
                    ),
                )

            # Look up order and calculate refund
            order_res = self._run_tool("get_order_details", {"order_id": order_id}, state)
            tool_calls.append({"name": "get_order_details", "result": order_res.data, "ok": order_res.ok})
            if not order_res.ok:
                return AgentResponse(
                    agent=self.name,
                    text=f"I couldn't find that order: {order_res.error}",
                    tool_calls=tool_calls,
                )

            reason = _detect_reason(text)
            calc_res = self._run_tool(
                "calculate_refund", {"order_id": order_id, "reason": reason}, state
            )
            tool_calls.append({"name": "calculate_refund", "result": calc_res.data, "ok": calc_res.ok})
            if not calc_res.ok:
                return AgentResponse(
                    agent=self.name,
                    text=f"I couldn't calculate the refund: {calc_res.error}",
                    tool_calls=tool_calls,
                )
            calc = calc_res.data
            if not calc["eligible"]:
                notes = " ".join(calc.get("policy_notes", []))
                return AgentResponse(
                    agent=self.name,
                    text=(
                        f"Unfortunately order {order_id} isn't eligible for a "
                        f"refund. {notes}".strip()
                    ),
                    tool_calls=tool_calls,
                )

            amount = float(calc["refund_amount"])

            # If user only asked for policy/quote, don't execute
            if "policy" in text or "how much" in text or "quote" in text:
                reply = (
                    f"For order {order_id}, the refund amount would be "
                    f"${amount:.2f}. "
                    + (
                        "This requires human approval before I can process it."
                        if calc["requires_hitl"]
                        else "I can process this now - shall I proceed?"
                    )
                )
                return AgentResponse(
                    agent=self.name, text=reply, tool_calls=tool_calls
                )

            # Attempt to process refund; HITL predicate gates > $50
            hitl_decision: Optional[str] = state.get("hitl_decision")
            proc_args = {"order_id": order_id, "amount": amount, "reason": reason}
            proc_res = self._run_tool(
                "process_refund", proc_args, state, hitl_decision=hitl_decision
            )
            tool_calls.append({"name": "process_refund", "result": proc_res.data, "ok": proc_res.ok, "hitl_required": proc_res.hitl_required})

            if proc_res.hitl_required and not proc_res.ok:
                if hitl_decision == "deny":
                    return AgentResponse(
                        agent=self.name,
                        text=(
                            f"Per your reviewer's decision, the ${amount:.2f} "
                            f"refund on {order_id} has been denied. I've "
                            f"logged the decision and will not process it."
                        ),
                        tool_calls=tool_calls,
                    )
                return AgentResponse(
                    agent=self.name,
                    text=(
                        f"The refund for {order_id} is ${amount:.2f}, which "
                        f"exceeds the ${HITL_THRESHOLD_USD:.0f} approval "
                        f"threshold. I've queued it for human review. Once "
                        f"approved I'll process it immediately."
                    ),
                    tool_calls=tool_calls,
                    hitl_required=True,
                    hitl_reason=proc_res.hitl_reason
                    or f"Refund ${amount:.2f} exceeds ${HITL_THRESHOLD_USD:.0f}.",
                    pending_action={
                        "tool": "process_refund",
                        "arguments": proc_args,
                        "amount": amount,
                        "order_id": order_id,
                    },
                )

            if not proc_res.ok:
                return AgentResponse(
                    agent=self.name,
                    text=f"I couldn't process the refund: {proc_res.error}",
                    tool_calls=tool_calls,
                )

            return AgentResponse(
                agent=self.name,
                text=(
                    f"Done - I've processed a ${amount:.2f} refund for order "
                    f"{order_id}. You should see it on your statement within "
                    f"5-7 business days."
                ),
                tool_calls=tool_calls,
                metadata={"refund_amount": amount, "order_id": order_id},
            )


def _extract_order_id(text: str) -> str | None:
    m = _ORDER_RE.search(text)
    return m.group().upper() if m else None


def _detect_reason(text: str) -> str:
    if "damaged" in text or "broken" in text or "defective" in text:
        return "damaged"
    if "partial" in text or "half" in text:
        return "partial"
    return "customer_request"
