"""Orchestrator: stitches agents + guardrails + memory + HITL + tracing.

This is an in-process implementation of the LangGraph StateGraph pattern
described in the capstone spec. Each node (guardrails, triage, specialist,
hitl, persist) updates the shared `CustomerSupportState` dict. It can be
adapted to LangGraph by wrapping each method as a node in a StateGraph.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .agents import BillingAgent, RefundAgent, TechnicalAgent, TriageAgent
from .agents.base import AgentResponse, BaseAgent
from .guardrails.input_guardrails import InputGuardrails
from .guardrails.output_guardrails import OutputGuardrails
from .knowledge_base import KnowledgeBase
from .llm import LLMClient
from .memory.store import CustomerProfile, MemoryStore
from .observability import get_tracer
from .state import CustomerSupportState, new_state
from .tools.registry import ToolRegistry, get_default_registry


@dataclass
class TurnResult:
    reply: str
    agent: str
    state: CustomerSupportState
    hitl_required: bool = False
    hitl_reason: Optional[str] = None
    pending_action: Optional[Dict[str, Any]] = None
    blocked: bool = False
    tool_calls: List[Dict[str, Any]] = None  # type: ignore

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


class HITLPolicy:
    """Pluggable HITL approval policy.

    The default ConsolePolicy prompts the user via stdin; tests use
    AutoApprovePolicy / AutoDenyPolicy to keep runs deterministic.
    """

    def approve(self, pending_action: Dict[str, Any]) -> str:  # pragma: no cover
        raise NotImplementedError


class AutoApprovePolicy(HITLPolicy):
    def approve(self, pending_action: Dict[str, Any]) -> str:
        return "approve"


class AutoDenyPolicy(HITLPolicy):
    def approve(self, pending_action: Dict[str, Any]) -> str:
        return "deny"


class QueuedPolicy(HITLPolicy):
    """Queue the action for external approval (e.g. via CLI command)."""

    def approve(self, pending_action: Dict[str, Any]) -> str:
        return "pending"


class Orchestrator:
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        memory: Optional[MemoryStore] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        llm: Optional[LLMClient] = None,
        input_guardrails: Optional[InputGuardrails] = None,
        output_guardrails: Optional[OutputGuardrails] = None,
        hitl_policy: Optional[HITLPolicy] = None,
    ):
        self.tools = tool_registry or get_default_registry()
        self.memory = memory or MemoryStore()
        self.kb = knowledge_base or KnowledgeBase()
        self.llm = llm or LLMClient()
        self.input_guard = input_guardrails or InputGuardrails()
        self.output_guard = output_guardrails or OutputGuardrails()
        self.hitl_policy = hitl_policy or QueuedPolicy()

        self.specialists: Dict[str, BaseAgent] = {
            "billing": BillingAgent(self.tools, self.llm),
            "technical": TechnicalAgent(self.tools, self.llm),
            "refund": RefundAgent(self.tools, self.llm),
        }
        self.triage = TriageAgent(self.tools, self.llm)

    # ---------------------------------------------------------- public API

    def create_session(self, customer_id: str) -> CustomerSupportState:
        tracer = get_tracer()
        trace_id = tracer.new_trace_id()
        state = new_state(customer_id=customer_id, trace_id=trace_id)
        # Hydrate from memory
        profile = self.memory.get_or_create(customer_id)
        state["conversation_summary"] = profile.summary
        state["metadata"] = {"session_id": f"sess_{uuid.uuid4().hex[:8]}"}
        return state

    def step(
        self,
        state: CustomerSupportState,
        user_message: str,
        hitl_decision: Optional[str] = None,
    ) -> TurnResult:
        """Process a single user turn."""
        tracer = get_tracer()
        trace_id = state.get("trace_id", "trace_anon")
        if hitl_decision:
            state["hitl_decision"] = hitl_decision

        with tracer.span("orchestrator.turn", "agent", trace_id=trace_id):
            # Input guardrails
            decision = self.input_guard.check(user_message)
            for f in decision.flags:
                state.setdefault("guardrail_flags", []).append({**f, "turn": "input"})
            if not decision.allowed:
                msg = (
                    "I can't process that request — it looks like an attempt "
                    "to override my instructions. If you have a genuine "
                    "question, please rephrase it."
                )
                self._persist_turn(state, user_message, msg, agent="guardrails")
                return TurnResult(
                    reply=msg, agent="guardrails", state=state, blocked=True
                )
            sanitized = decision.sanitized_text
            state["messages"] = state.get("messages", []) + [
                {"role": "user", "content": sanitized}
            ]

            # Always let triage classify; stay with current agent only if the
            # classifier is uncertain (route == "triage"), otherwise honor the
            # new route. This gives us free topic-switching across turns.
            current_agent = state.get("current_agent") or "triage"
            route = self.triage.classify(sanitized, trace_id)
            if route == "triage":
                if current_agent in self.specialists:
                    target = current_agent
                else:
                    # True triage (ambiguous): ask for clarification
                    triage_resp = self.triage.handle(state, sanitized)
                    response = triage_resp
                    target = None
            else:
                target = route
            if target is not None:
                state["current_agent"] = target
                agent = self.specialists[target]
                response = agent.handle(state, sanitized)

            # Output guardrails
            out_decision = self.output_guard.check(response.text)
            for f in out_decision.flags:
                state.setdefault("guardrail_flags", []).append({**f, "turn": "output"})
            final_text = out_decision.sanitized_text

            # HITL handling
            if response.hitl_required and response.pending_action:
                pending = {
                    "action_id": f"act_{uuid.uuid4().hex[:8]}",
                    **response.pending_action,
                    "status": "pending",
                    "reason": response.hitl_reason,
                }
                state.setdefault("pending_actions", []).append(pending)
                state["hitl_required"] = True
                with tracer.span(
                    "hitl.queue",
                    "hitl",
                    trace_id=trace_id,
                    inputs={"pending": pending},
                ):
                    decision_outcome = self.hitl_policy.approve(pending)
                if decision_outcome in ("approve", "deny"):
                    # Re-run the tool with decision
                    state["hitl_decision"] = decision_outcome
                    agent = self.specialists[state["current_agent"]]
                    response = agent.handle(state, sanitized)
                    out_decision = self.output_guard.check(response.text)
                    for f in out_decision.flags:
                        state.setdefault("guardrail_flags", []).append(
                            {**f, "turn": "output_post_hitl"}
                        )
                    final_text = out_decision.sanitized_text
                    for p in state["pending_actions"]:
                        if p.get("action_id") == pending.get("action_id"):
                            p["status"] = (
                                "approved" if decision_outcome == "approve" else "denied"
                            )
                    state["hitl_required"] = False

            state["messages"] = state.get("messages", []) + [
                {"role": "assistant", "content": final_text, "agent": response.agent}
            ]

            # Persist + update summary
            self._persist_turn(state, sanitized, final_text, agent=response.agent)

            return TurnResult(
                reply=final_text,
                agent=response.agent,
                state=state,
                hitl_required=bool(state.get("hitl_required")),
                hitl_reason=response.hitl_reason,
                pending_action=response.pending_action,
                tool_calls=response.tool_calls,
            )

    # ---------------------------------------------------------- helpers

    def _persist_turn(
        self,
        state: CustomerSupportState,
        user_text: str,
        assistant_text: str,
        agent: str,
    ) -> None:
        cid = state.get("customer_id", "cust_unknown")
        ts = int(time.time())
        self.memory.append_message(
            cid, {"role": "user", "content": user_text, "ts": ts, "agent": agent}
        )
        self.memory.append_message(
            cid,
            {
                "role": "assistant",
                "content": assistant_text,
                "ts": ts,
                "agent": agent,
            },
        )
        # Cheap summarization: keep a sliding bag of topics mentioned
        profile = self.memory.get_or_create(cid)
        topics = set(profile.summary.split(", ")) if profile.summary else set()
        topics.discard("")
        for kw in ("invoice", "payment", "plan", "refund", "order", "diagnostic", "ticket", "login"):
            if kw in user_text.lower() or kw in assistant_text.lower():
                topics.add(kw)
        new_summary = ", ".join(sorted(topics))
        if new_summary != profile.summary:
            self.memory.update_summary(cid, new_summary)
            state["conversation_summary"] = new_summary


def _looks_like_new_topic(text: str) -> bool:
    """Heuristic: force a triage re-routing if the user clearly jumps topic."""
    text_l = text.lower()
    strong_cues = [
        "now i have a different",
        "switch to",
        "separate question",
        "different question",
        "another question",
        "also, about my",
    ]
    return any(c in text_l for c in strong_cues)
