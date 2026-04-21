"""Optional LangGraph adapter.

If `langgraph` is installed the orchestrator can be expressed as a
StateGraph, which mirrors the capstone spec. When not installed this
module raises ImportError on build() but the pure-Python Orchestrator
still works.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .orchestrator import Orchestrator


def build_langgraph_app(orchestrator: Optional[Orchestrator] = None) -> Any:
    """Build a LangGraph StateGraph that mirrors the in-process orchestrator."""
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
    except Exception as e:  # pragma: no cover - optional path
        raise ImportError(
            "langgraph is not installed. Install with `pip install langgraph` "
            "to use the LangGraph adapter."
        ) from e

    orch = orchestrator or Orchestrator()

    def _input_guard(state: Dict[str, Any]) -> Dict[str, Any]:
        decision = orch.input_guard.check(state["user_message"])
        state["guardrail_flags"] = list(state.get("guardrail_flags", [])) + [
            {**f, "turn": "input"} for f in decision.flags
        ]
        state["sanitized"] = decision.sanitized_text
        state["blocked"] = not decision.allowed
        return state

    def _triage(state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("blocked"):
            return state
        route = orch.triage.classify(
            state["sanitized"], state.get("trace_id", "trace_anon")
        )
        state["current_agent"] = route if route != "triage" else state.get("current_agent", "triage")
        return state

    def _specialist(state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("blocked"):
            return state
        agent_name = state.get("current_agent", "triage")
        agent = orch.specialists.get(agent_name) or orch.triage
        resp = agent.handle(state, state["sanitized"])
        state["reply"] = resp.text
        state["hitl_required"] = resp.hitl_required
        state["pending_action"] = resp.pending_action
        return state

    def _output_guard(state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("reply", "")
        decision = orch.output_guard.check(text)
        state["reply"] = decision.sanitized_text
        state["guardrail_flags"] = list(state.get("guardrail_flags", [])) + [
            {**f, "turn": "output"} for f in decision.flags
        ]
        return state

    g = StateGraph(dict)
    g.add_node("input_guard", _input_guard)
    g.add_node("triage", _triage)
    g.add_node("specialist", _specialist)
    g.add_node("output_guard", _output_guard)
    g.set_entry_point("input_guard")
    g.add_edge("input_guard", "triage")
    g.add_edge("triage", "specialist")
    g.add_edge("specialist", "output_guard")
    g.add_edge("output_guard", END)
    return g.compile()
