from __future__ import annotations

from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph

from customer_support_system.agents import BillingAgent, RefundAgent, TechnicalAgent, TriageAgent
from customer_support_system.guardrails import apply_input_guardrails, apply_output_guardrails
from customer_support_system.memory import MemoryStore
from customer_support_system.model import DeterministicSupportModel
from customer_support_system.state import CustomerSupportState
from customer_support_system.tools.registry import ToolRegistry
from customer_support_system.tracing import TraceRecorder


@dataclass
class CustomerSupportSystem:
    memory_store: MemoryStore = field(default_factory=MemoryStore)
    registry: ToolRegistry = field(default_factory=ToolRegistry)

    def __post_init__(self) -> None:
        self.graph = self._build_graph().compile()

    def _services(self) -> tuple[TraceRecorder, TriageAgent, BillingAgent, TechnicalAgent, RefundAgent]:
        recorder = TraceRecorder()
        model = DeterministicSupportModel(recorder)
        triage = TriageAgent(model)
        billing = BillingAgent(name="billing", recorder=recorder, registry=self.registry)
        technical = TechnicalAgent(name="technical", recorder=recorder, registry=self.registry)
        refund = RefundAgent(name="refund", recorder=recorder, registry=self.registry)
        return recorder, triage, billing, technical, refund

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(CustomerSupportState)
        graph.add_node("input_guardrails", self._input_guardrails)
        graph.add_node("load_memory", self._load_memory)
        graph.add_node("triage", self._triage)
        graph.add_node("billing", self._billing)
        graph.add_node("technical", self._technical)
        graph.add_node("refund", self._refund)
        graph.add_node("finalize", self._finalize)
        graph.add_edge(START, "input_guardrails")
        graph.add_conditional_edges(
            "input_guardrails",
            self._input_decision,
            {"blocked": "finalize", "continue": "load_memory"},
        )
        graph.add_edge("load_memory", "triage")
        graph.add_conditional_edges(
            "triage",
            self._route_decision,
            {"billing": "billing", "technical": "technical", "refund": "refund"},
        )
        graph.add_edge("billing", "finalize")
        graph.add_edge("technical", "finalize")
        graph.add_edge("refund", "finalize")
        graph.add_edge("finalize", END)
        return graph

    def _input_guardrails(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder = TraceRecorder()
        result = apply_input_guardrails(state["user_input"])
        recorder.guardrail("input", result)
        traces, costs = recorder.snapshot()
        response = ""
        if result["blocked"]:
            response = "Your request was blocked because it attempted to override system safety instructions."
        return {
            "sanitized_input": result["sanitized_input"],
            "guardrail_flags": result["guardrail_flags"],
            "blocked": result["blocked"],
            "last_response": response,
            "messages": [{"role": "user", "content": result["sanitized_input"]}],
            "traces": traces,
            "model_costs": costs,
            "pending_actions": [],
            "tool_outputs": [],
            "route": "blocked" if result["blocked"] else "triage",
        }

    def _input_decision(self, state: CustomerSupportState) -> str:
        return "blocked" if state.get("blocked") else "continue"

    def _load_memory(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder = TraceRecorder()
        memory = self.memory_store.load(state["customer_id"])
        recorder.memory("load", {"customer_id": state["customer_id"], "summary": memory["summary"]})
        traces, costs = recorder.snapshot()
        return {
            "memory": memory,
            "conversation_summary": memory["summary"],
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def _triage(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder, triage, _, _, _ = self._services()
        route = triage.route(state["sanitized_input"])
        traces, costs = recorder.snapshot()
        return {
            "route": route,
            "current_agent": "triage",
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def _route_decision(self, state: CustomerSupportState) -> str:
        return state["route"]

    def _billing(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder, _, billing, _, _ = self._services()
        result = billing.handle(state["customer_id"], state["sanitized_input"], state["memory"])
        traces, costs = recorder.snapshot()
        return {
            "current_agent": "billing",
            "last_response": result["response"],
            "tool_outputs": result["tool_outputs"],
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def _technical(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder, _, _, technical, _ = self._services()
        result = technical.handle(state["customer_id"], state["sanitized_input"], state["memory"])
        traces, costs = recorder.snapshot()
        return {
            "current_agent": "technical",
            "last_response": result["response"],
            "tool_outputs": result["tool_outputs"],
            "ticket_id": result.get("ticket_id"),
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def _refund(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder, _, _, _, refund = self._services()
        result = refund.handle(
            state["customer_id"],
            state["sanitized_input"],
            state["memory"],
            state.get("approval_granted", False),
        )
        traces, costs = recorder.snapshot()
        return {
            "current_agent": "refund",
            "last_response": result["response"],
            "tool_outputs": result["tool_outputs"],
            "approval_required": result.get("approval_required", False),
            "pending_actions": result.get("pending_actions", []),
            "order_id": result.get("order_id"),
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def _finalize(self, state: CustomerSupportState) -> CustomerSupportState:
        recorder = TraceRecorder()
        response_result = apply_output_guardrails(state.get("last_response", ""))
        recorder.guardrail("output", response_result)
        summary_model = DeterministicSupportModel(recorder)
        summary = summary_model.summarize(state.get("sanitized_input", ""), state.get("conversation_summary", ""))
        self.memory_store.save_turn(
            customer_id=state["customer_id"],
            user_input=state.get("sanitized_input", ""),
            response=response_result["response"],
            route=state.get("route", "blocked"),
            ticket_id=state.get("ticket_id"),
            summary=summary,
            order_id=state.get("order_id"),
        )
        traces, costs = recorder.snapshot()
        combined_flags = sorted(set(state.get("guardrail_flags", []) + response_result["guardrail_flags"]))
        assistant_message = [{"role": "assistant", "content": response_result["response"]}]
        return {
            "last_response": response_result["response"],
            "guardrail_flags": combined_flags,
            "conversation_summary": summary,
            "messages": assistant_message,
            "traces": state.get("traces", []) + traces,
            "model_costs": state.get("model_costs", []) + costs,
        }

    def handle_message(self, customer_id: str, user_input: str, approval_granted: bool = False) -> dict[str, object]:
        state: CustomerSupportState = {
            "customer_id": customer_id,
            "user_input": user_input,
            "approval_granted": approval_granted,
        }
        result = self.graph.invoke(state)
        return {
            "response": result["last_response"],
            "current_agent": result.get("current_agent", "blocked"),
            "ticket_id": result.get("ticket_id"),
            "pending_actions": result.get("pending_actions", []),
            "guardrail_flags": result.get("guardrail_flags", []),
            "messages": result.get("messages", []),
            "summary": result.get("conversation_summary", ""),
            "tool_outputs": result.get("tool_outputs", []),
            "trace_count": len(result.get("traces", [])),
            "traces": result.get("traces", []),
            "costs": result.get("model_costs", []),
            "total_cost_usd": round(sum(item["estimated_cost_usd"] for item in result.get("model_costs", [])), 6),
        }
