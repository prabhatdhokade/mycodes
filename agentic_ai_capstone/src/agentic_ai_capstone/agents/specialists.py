"""Specialist agent implementations."""

from __future__ import annotations

import re
from typing import Callable

from ..knowledge import KnowledgeBase
from ..memory.store import MemoryStore
from ..observability.tracer import Tracer
from ..state import CustomerSupportState, append_message, latest_user_message
from ..tools.registry import ToolRegistry


def _extract_order_id(text: str) -> str:
    match = re.search(r"\b(ord-[0-9]+)\b", text.lower())
    return match.group(1) if match else "ord-120"


def _extract_amount(text: str) -> float:
    money = re.search(r"\$([0-9]+(?:\.[0-9]{1,2})?)", text)
    if money:
        return float(money.group(1))
    generic = re.search(r"\b([0-9]+(?:\.[0-9]{1,2})?)\b", text)
    if generic:
        return float(generic.group(1))
    return 25.0


def billing_agent(
    state: CustomerSupportState,
    tools: ToolRegistry,
    tracer: Tracer,
    memory_store: MemoryStore,
    knowledge: KnowledgeBase,
) -> CustomerSupportState:
    query = latest_user_message(state).lower()
    customer_id = state["customer_id"]
    outputs: list[str] = []
    actions: list[str] = []

    if "invoice" in query or "billing" in query or "plan" in query:
        invoice = tools.call("get_invoice", customer_id=customer_id, invoice_id="inv-500")
        outputs.append(
            f"Invoice {invoice['invoice_id']} is {invoice['status']} with amount due ${invoice['amount_due']:.2f}."
        )
        actions.append("billing:get_invoice")
    if "payment" in query:
        history = tools.call("get_payment_history", customer_id=customer_id)
        if history:
            latest = history[0]
            outputs.append(
                f"Latest payment was ${latest['amount']:.2f} using {latest['method']}."
            )
        actions.append("billing:get_payment_history")
    if "update payment method" in query or "new card" in query or "update" in query:
        changed = tools.call(
            "update_payment_method",
            customer_id=customer_id,
            payment_token="tok-demo-4242",
        )
        outputs.append(f"Payment method {changed['status']} (last4={changed['last4']}).")
        actions.append("billing:update_payment_method")

    if not outputs:
        outputs.append("I can help with invoices, payments, and plan-related billing questions.")
    outputs.append(knowledge.lookup("billing"))
    response = " ".join(outputs)

    append_message(state, "assistant", response)
    state["pending_actions"].extend(actions)
    state["conversation_summary"] = response[:200]
    state["current_agent"] = "billing"
    memory_store.append_message(customer_id, latest_user_message(state))
    tracer.record("billing_agent", "respond", query, response)
    return state


def technical_agent(
    state: CustomerSupportState,
    tools: ToolRegistry,
    tracer: Tracer,
    memory_store: MemoryStore,
    knowledge: KnowledgeBase,
) -> CustomerSupportState:
    query = latest_user_message(state).lower()
    customer_id = state["customer_id"]
    outputs: list[str] = []
    actions: list[str] = []

    diagnostics = tools.call("run_diagnostics", customer_id=customer_id)
    outputs.append(
        f"Diagnostics complete: health={diagnostics['health']} packet_loss={diagnostics['packet_loss']}%."
    )
    actions.append("technical:run_diagnostics")

    if "status" in query or "outage" in query or "service" in query:
        status = tools.call("check_service_status", service="internet")
        outputs.append(f"Service status is {status['status']} (incident={status['incident']}).")
        actions.append("technical:check_service_status")

    if "ticket" in query or "escalate" in query:
        ticket = tools.call("create_ticket", customer_id=customer_id, issue="Escalated issue")
        state["ticket_id"] = ticket["ticket_id"]
        outputs.append(f"Escalated and created ticket {ticket['ticket_id']}.")
        actions.append("technical:create_ticket")

    outputs.append(knowledge.lookup("technical"))
    response = " ".join(outputs)

    append_message(state, "assistant", response)
    state["pending_actions"].extend(actions)
    state["conversation_summary"] = response[:200]
    state["current_agent"] = "technical"
    memory_store.append_message(customer_id, latest_user_message(state))
    tracer.record("technical_agent", "respond", query, response)
    return state


def refund_agent(
    state: CustomerSupportState,
    tools: ToolRegistry,
    tracer: Tracer,
    memory_store: MemoryStore,
    knowledge: KnowledgeBase,
    approver: Callable[[str, float], bool],
) -> CustomerSupportState:
    query = latest_user_message(state)
    customer_id = state["customer_id"]
    order_id = _extract_order_id(query)
    requested = _extract_amount(query)

    order = tools.call("get_order_details", customer_id=customer_id, order_id=order_id)
    if order.get("status") == "not_found":
        response = f"Order {order_id} not found. Please verify the order number."
        append_message(state, "assistant", response)
        state["pending_actions"].append("refund:get_order_details")
        state["current_agent"] = "refund"
        memory_store.append_message(customer_id, latest_user_message(state))
        tracer.record("refund_agent", "respond", query, response)
        return state

    quote = tools.call("calculate_refund", order_total=float(order["order_total"]), reason="customer_request")
    amount = min(requested, float(quote["eligible_amount"]))
    state["pending_actions"].extend(["refund:get_order_details", "refund:calculate_refund"])

    if amount > 50.0 and not approver(customer_id, amount):
        response = f"Refund request of ${amount:.2f} requires human approval before processing."
        append_message(state, "assistant", response)
        state["pending_actions"].append("refund:approval_required")
        state["conversation_summary"] = response[:200]
        state["current_agent"] = "refund"
        memory_store.append_message(customer_id, latest_user_message(state))
        tracer.record("refund_agent", "hitl_gate", query, response)
        return state

    refund = tools.call(
        "process_refund",
        order_id=order_id,
        amount=amount,
        approved_by_human=(amount <= 50.0 or approver(customer_id, amount)),
    )
    state["pending_actions"].append("refund:process_refund")
    response = (
        f"Refund processed for order {order_id}: ${refund['amount']:.2f}, status={refund['status']}. "
        f"{knowledge.lookup('refund')}"
    )
    append_message(state, "assistant", response)
    state["conversation_summary"] = response[:200]
    state["current_agent"] = "refund"
    memory_store.append_message(customer_id, latest_user_message(state))
    tracer.record("refund_agent", "respond", query, response)
    return state
