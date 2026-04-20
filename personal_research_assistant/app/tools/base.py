"""Tool base class and registry.

A ``Tool`` has a name, human-readable description, a JSON-schema-ish
parameter spec (for prompting), an optional HITL gate, and an ``execute``
implementation. Tool invocations are logged with latency.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from ..observability import get_logger, timed

logger = get_logger("tools")


HumanApproval = Callable[[str, Mapping[str, Any]], bool]
"""Signature for a HITL approval callback.

Receives ``(tool_name, arguments)`` and must return ``True`` to proceed.
"""


@dataclass
class ToolResult:
    ok: bool
    output: Any
    meta: dict[str, Any] = field(default_factory=dict)

    def as_observation(self) -> str:
        if self.ok:
            return str(self.output)
        return f"ERROR: {self.output}"


class Tool(ABC):
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = {}
    requires_approval: bool = False

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult: ...

    def invoke(
        self,
        arguments: Mapping[str, Any],
        *,
        approval: HumanApproval | None = None,
    ) -> ToolResult:
        """Run ``execute`` with logging and an optional HITL gate."""

        args = dict(arguments or {})
        with timed(logger, "tool.invoke", tool=self.name, tool_args=_safe_args(args)) as ctx:
            if self.requires_approval:
                if approval is None:
                    ctx["approved"] = False
                    return ToolResult(
                        ok=False,
                        output=(
                            "HITL approval required but no approval callback was "
                            "provided for this run."
                        ),
                        meta={"requires_approval": True},
                    )
                granted = bool(approval(self.name, args))
                ctx["approved"] = granted
                if not granted:
                    return ToolResult(
                        ok=False,
                        output="User declined approval for this action.",
                        meta={"requires_approval": True, "approved": False},
                    )

            try:
                result = self.execute(**args)
            except TypeError as exc:
                return ToolResult(ok=False, output=f"Bad arguments: {exc}")
            except Exception as exc:
                logger.exception("tool.crashed", extra={"tool": self.name})
                return ToolResult(ok=False, output=f"Tool crashed: {exc!r}")
            ctx["ok"] = result.ok
            return result

    def spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_approval": self.requires_approval,
        }


def _safe_args(args: Mapping[str, Any]) -> dict[str, Any]:
    """Truncate long values so the log stays compact."""

    out: dict[str, Any] = {}
    for k, v in args.items():
        if isinstance(v, str) and len(v) > 200:
            out[k] = v[:200] + "…"
        else:
            out[k] = v
    return out


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        if not tool.name:
            raise ValueError("Tool must have a name")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def render_for_prompt(self) -> str:
        lines = []
        for tool in self._tools.values():
            params = ", ".join(f"{k}: {v.get('type', 'any')}" for k, v in tool.parameters.items())
            flag = " (requires human approval)" if tool.requires_approval else ""
            lines.append(f"- {tool.name}({params}): {tool.description}{flag}")
        return "\n".join(lines)
