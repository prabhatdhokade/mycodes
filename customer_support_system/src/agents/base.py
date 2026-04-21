"""Shared base class for all agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..llm import LLMClient
from ..observability import get_tracer
from ..state import CustomerSupportState
from ..tools.registry import ToolRegistry


@dataclass
class AgentResponse:
    agent: str
    text: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    handoff_to: Optional[str] = None
    hitl_required: bool = False
    hitl_reason: Optional[str] = None
    pending_action: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name: str = "base"
    description: str = ""
    system_prompt: str = ""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        llm: Optional[LLMClient] = None,
    ) -> None:
        self.tools = tool_registry
        self.llm = llm or LLMClient()

    def handle(
        self, state: CustomerSupportState, user_message: str
    ) -> AgentResponse:  # pragma: no cover - overridden
        raise NotImplementedError

    def _run_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        state: CustomerSupportState,
        hitl_decision: Optional[str] = None,
    ):
        trace_id = state.get("trace_id", "trace_anon")
        return self.tools.call(name, arguments, trace_id=trace_id, hitl_decision=hitl_decision)

    def _trace_agent(self, state: CustomerSupportState, inputs: Dict[str, Any]):
        tracer = get_tracer()
        return tracer.span(
            f"agent.{self.name}",
            "agent",
            trace_id=state.get("trace_id", "trace_anon"),
            inputs=inputs,
        )
