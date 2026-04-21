from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from langgraph.graph import END, StateGraph

from .agents import billing_agent, refund_agent, technical_agent, triage_agent
from .guardrails.policies import check_input_guardrails, mask_pii
from .knowledge import KnowledgeBase
from .memory.store import MemoryStore
from .metrics.iteration import IterationTracker
from .observability.tracer import TraceCollector
from .state import CustomerSupportState, clone_state, initialize_state, with_message
from .tools.context import ToolContext
from .tools.registry import ToolRegistry, build_default_registry


@dataclass
class RunResult:
    response: str
    state: CustomerSupportState


class CustomerSupportEngine:
    """LangGraph-backed orchestrator for customer support workflows."""

    def __init__(
        self,
        memory_store: MemoryStore | None = None,
        knowledge_base: KnowledgeBase | None = None,
        tracer: TraceCollector | None = None,
        metrics: IterationTracker | None = None,
        refund_approver: Callable[[str, float], bool] | None = None,
    ) -> None:
        self.memory_store = memory_store or MemoryStore()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.tracer = tracer or TraceCollector()
        self.metrics = metrics or IterationTracker()
        self.refund_approver = refund_approver or (lambda _customer_id, _amount: False)
        self.tool_context = ToolContext()
        self.tool_registry: ToolRegistry = build_default_registry(self.tool_context)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(dict)
        graph.add_node(
            "triage",
            lambda state: triage_agent(
                state=state, tracer=self.tracer, memory_store=self.memory_store
            ),
        )
        graph.add_node(
            "billing",
            lambda state: billing_agent(
                state=state,
                tools=self.tool_registry,
                tracer=self.tracer,
                memory_store=self.memory_store,
                knowledge=self.knowledge_base,
            ),
        )
        graph.add_node(
            "technical",
            lambda state: technical_agent(
                state=state,
                tools=self.tool_registry,
                tracer=self.tracer,
                memory_store=self.memory_store,
                knowledge=self.knowledge_base,
            ),
        )
        graph.add_node(
            "refund",
            lambda state: refund_agent(
                state=state,
                tools=self.tool_registry,
                tracer=self.tracer,
                memory_store=self.memory_store,
                knowledge=self.knowledge_base,
                approver=self.refund_approver,
            ),
        )

        graph.set_entry_point("triage")
        graph.add_conditional_edges(
            "triage",
            lambda state: state.get("current_agent", END),
            {"billing": "billing", "technical": "technical", "refund": "refund", END: END},
        )
        graph.add_edge("billing", END)
        graph.add_edge("technical", END)
        graph.add_edge("refund", END)
        return graph.compile()

    def handle_message(
        self,
        customer_id: str,
        text: str,
        ticket_id: str | None = None,
        prior_state: CustomerSupportState | None = None,
        human_approval: bool = False,
    ) -> RunResult:
        self.metrics.start_iteration()

        guard = check_input_guardrails(text)
        if guard.blocked:
            blocked_state = clone_state(prior_state) if prior_state else initialize_state(customer_id, ticket_id)
            blocked_state["guardrail_flags"].extend(guard.flags + guard.reasons)
            with_message(blocked_state, "user", text)
            with_message(blocked_state, "assistant", "Request blocked by input guardrails.")
            self.memory_store.append_event(customer_id, "guardrail", "blocked_input")
            self.metrics.complete_iteration(success=False)
            return RunResult(response="Request blocked by safety guardrails.", state=blocked_state)

        state = clone_state(prior_state) if prior_state else initialize_state(customer_id, ticket_id)
        state["context"]["human_approval"] = human_approval
        state["guardrail_flags"] = list(state.get("guardrail_flags", []))
        with_message(state, "user", guard.sanitized_text)
        self.memory_store.append_message(customer_id, guard.sanitized_text)

        result: CustomerSupportState = self.graph.invoke(state)

        response_text = result["messages"][-1]["content"] if result["messages"] else ""
        masked = mask_pii(response_text)
        if masked.flags:
            result["guardrail_flags"].extend(masked.flags)
            result["messages"][-1]["content"] = masked.sanitized_text
            response_text = masked.sanitized_text

        self.memory_store.save_state(customer_id, result)
        self.metrics.complete_iteration(success=True)
        return RunResult(response=response_text, state=result)

    def respond(
        self,
        customer_id: str,
        user_message: str,
        ticket_id: str | None = None,
        human_approval: bool = False,
        prior_state: CustomerSupportState | None = None,
    ) -> dict:
        result = self.handle_message(
            customer_id=customer_id,
            text=user_message,
            ticket_id=ticket_id,
            prior_state=prior_state,
            human_approval=human_approval,
        )
        return {
            "response": result.response,
            "state": result.state,
            "current_agent": result.state.get("current_agent", "triage"),
            "tracing": self.tracer.summary(),
            "metrics": self.metrics.summary(),
        }
