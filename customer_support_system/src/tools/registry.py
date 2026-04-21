"""Central tool registry with schema + HITL support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..observability import get_tracer


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error: Optional[str] = None
    hitl_required: bool = False
    hitl_reason: Optional[str] = None


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., ToolResult]
    owner_agent: str  # "billing" | "technical" | "refund"
    parameters: Dict[str, str] = field(default_factory=dict)
    requires_hitl: bool = False
    hitl_predicate: Optional[Callable[[Dict[str, Any]], bool]] = None

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "owner_agent": self.owner_agent,
            "requires_hitl": self.requires_hitl,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_for_agent(self, agent: str) -> List[Tool]:
        return [t for t in self._tools.values() if t.owner_agent == agent]

    def all(self) -> List[Tool]:
        return list(self._tools.values())

    def call(
        self,
        name: str,
        arguments: Dict[str, Any],
        trace_id: str,
        hitl_decision: Optional[str] = None,
    ) -> ToolResult:
        """Invoke a tool. If it needs HITL approval and we don't have one,
        return a ToolResult flagged as hitl_required=True without executing.
        """
        tool = self.get(name)
        needs_hitl = tool.requires_hitl
        if tool.hitl_predicate:
            try:
                needs_hitl = needs_hitl or bool(tool.hitl_predicate(arguments))
            except Exception:
                needs_hitl = True

        tracer = get_tracer()
        with tracer.span(
            f"tool.{name}", "tool", trace_id=trace_id, inputs=arguments
        ) as span:
            if needs_hitl and hitl_decision != "approve":
                if hitl_decision == "deny":
                    res = ToolResult(
                        ok=False,
                        error="Action denied by human reviewer.",
                        hitl_required=True,
                    )
                else:
                    res = ToolResult(
                        ok=False,
                        hitl_required=True,
                        hitl_reason=(
                            f"Tool {name!r} requires human approval before execution."
                        ),
                    )
                span.outputs = {
                    "ok": res.ok,
                    "hitl_required": res.hitl_required,
                    "hitl_reason": res.hitl_reason,
                    "error": res.error,
                }
                return res
            try:
                result = tool.fn(**arguments)
                if not isinstance(result, ToolResult):
                    result = ToolResult(ok=True, data=result)
            except Exception as e:  # defensive: tool failures shouldn't crash agent
                result = ToolResult(ok=False, error=f"{type(e).__name__}: {e}")
            span.outputs = {"ok": result.ok, "data": result.data, "error": result.error}
            return result


_DEFAULT: Optional[ToolRegistry] = None


def get_default_registry() -> ToolRegistry:
    global _DEFAULT
    if _DEFAULT is None:
        from . import billing_tools, technical_tools, refund_tools

        reg = ToolRegistry()
        billing_tools.register(reg)
        technical_tools.register(reg)
        refund_tools.register(reg)
        _DEFAULT = reg
    return _DEFAULT


def reset_default_registry() -> None:
    global _DEFAULT
    _DEFAULT = None
