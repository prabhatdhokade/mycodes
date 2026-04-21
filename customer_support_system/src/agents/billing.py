"""Billing specialist agent."""
from __future__ import annotations

import re
from typing import Any, Dict

from ..state import CustomerSupportState
from .base import AgentResponse, BaseAgent

BILLING_SYSTEM = (
    "You are the Billing specialist. You help customers with invoices, "
    "payments, and subscription plans. Use your tools: get_invoice, "
    "get_payment_history, update_payment_method."
)


class BillingAgent(BaseAgent):
    name = "billing"
    description = "Handles invoices, payments, and plan questions."
    system_prompt = BILLING_SYSTEM

    def handle(
        self, state: CustomerSupportState, user_message: str
    ) -> AgentResponse:
        with self._trace_agent(state, {"message": user_message[:400]}):
            text = user_message.lower()
            customer_id = state.get("customer_id", "cust_unknown")
            tool_calls = []

            if "payment history" in text or "payments" in text or "paid" in text:
                res = self._run_tool(
                    "get_payment_history", {"customer_id": customer_id}, state
                )
                tool_calls.append({"name": "get_payment_history", "result": res.data, "ok": res.ok})
                if res.ok and res.data:
                    count = res.data.get("count", 0)
                    payments = res.data.get("payments", [])
                    if payments:
                        latest = payments[-1]
                        reply = (
                            f"I found {count} payment(s) on file. Your most "
                            f"recent payment was ${latest['amount']:.2f} via "
                            f"{latest['method']} on {latest['date']}."
                        )
                    else:
                        reply = "I don't see any payments on file for your account yet."
                else:
                    reply = "I couldn't retrieve your payment history right now."
                return AgentResponse(
                    agent=self.name, text=reply, tool_calls=tool_calls
                )

            if "update" in text and ("payment" in text or "card" in text or "method" in text):
                new_method = _extract_payment_method(user_message) or "card-on-file"
                res = self._run_tool(
                    "update_payment_method",
                    {"customer_id": customer_id, "new_method": new_method},
                    state,
                )
                tool_calls.append({"name": "update_payment_method", "result": res.data, "ok": res.ok})
                if res.ok:
                    reply = (
                        f"Your payment method has been updated to "
                        f"{res.data['new_method']}. "
                        f"Effective immediately."
                    )
                else:
                    reply = f"I couldn't update your payment method: {res.error}"
                return AgentResponse(
                    agent=self.name, text=reply, tool_calls=tool_calls
                )

            if "plan" in text or "subscription" in text or "pricing" in text:
                reply = (
                    "Our plans are Basic ($9/mo), Pro ($29/mo), and Enterprise "
                    "(contact sales). Plan changes take effect on the next "
                    "billing cycle. Would you like to change plans?"
                )
                return AgentResponse(agent=self.name, text=reply)

            # Default: invoice lookup
            invoice_id = _extract_invoice_id(user_message)
            args: Dict[str, Any] = {"customer_id": customer_id}
            if invoice_id:
                args["invoice_id"] = invoice_id
            res = self._run_tool("get_invoice", args, state)
            tool_calls.append({"name": "get_invoice", "result": res.data, "ok": res.ok})
            if not res.ok:
                return AgentResponse(
                    agent=self.name,
                    text=f"I couldn't find that invoice: {res.error}",
                    tool_calls=tool_calls,
                )
            data = res.data or {}
            if "latest" in data:
                latest = data["latest"]
                reply = (
                    f"Your latest invoice is {latest['invoice_id']} for "
                    f"${latest['amount']:.2f} (status: {latest['status']}, "
                    f"due {latest['due']})."
                )
            elif "invoices" in data and not data["invoices"]:
                reply = "You have no invoices on file."
            else:
                reply = (
                    f"Invoice {data.get('invoice_id')} — ${data.get('amount', 0):.2f} "
                    f"({data.get('status')}), due {data.get('due')}."
                )
            return AgentResponse(
                agent=self.name, text=reply, tool_calls=tool_calls
            )


_INVOICE_RE = re.compile(r"INV-\d{3,}", re.IGNORECASE)


def _extract_invoice_id(text: str) -> str | None:
    m = _INVOICE_RE.search(text)
    return m.group().upper() if m else None


def _extract_payment_method(text: str) -> str | None:
    text_l = text.lower()
    if "paypal" in text_l:
        return "paypal"
    if "amex" in text_l:
        return "amex"
    if "visa" in text_l:
        return "visa"
    if "mastercard" in text_l or "master card" in text_l:
        return "mastercard"
    if "bank" in text_l:
        return "bank-transfer"
    return None
