"""Tool registry and default wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .billing import get_invoice, get_payment_history, update_payment_method
from .context import ToolContext
from .refund import calculate_refund, get_order_details, process_refund
from .technical import check_service_status, create_ticket, run_diagnostics

ToolHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: ToolHandler
    agent: str
    description: str


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        self._tools[tool.name] = tool

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name].handler(**kwargs)

    def list_tools(self, agent: str | None = None) -> list[str]:
        if agent is None:
            return sorted(self._tools.keys())
        return sorted([tool.name for tool in self._tools.values() if tool.agent == agent])

    def list_for_agent(self, agent: str) -> list[str]:
        return self.list_tools(agent=agent)


def build_default_registry(context: ToolContext) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="get_invoice",
            handler=lambda **kwargs: get_invoice(context=context, **kwargs),
            agent="billing",
            description="Return invoice details for a customer.",
        )
    )
    registry.register(
        ToolSpec(
            name="get_payment_history",
            handler=lambda **kwargs: get_payment_history(context=context, **kwargs),
            agent="billing",
            description="Return payment history for a customer.",
        )
    )
    registry.register(
        ToolSpec(
            name="update_payment_method",
            handler=lambda **kwargs: update_payment_method(context=context, **kwargs),
            agent="billing",
            description="Update the customer's payment method token.",
        )
    )

    registry.register(
        ToolSpec(
            name="run_diagnostics",
            handler=lambda **kwargs: run_diagnostics(context=context, **kwargs),
            agent="technical",
            description="Run diagnostics for a customer account.",
        )
    )
    registry.register(
        ToolSpec(
            name="check_service_status",
            handler=lambda **kwargs: check_service_status(context=context, **kwargs),
            agent="technical",
            description="Check service status for a specific service.",
        )
    )
    registry.register(
        ToolSpec(
            name="create_ticket",
            handler=lambda **kwargs: create_ticket(context=context, **kwargs),
            agent="technical",
            description="Create an escalation ticket.",
        )
    )

    registry.register(
        ToolSpec(
            name="get_order_details",
            handler=lambda **kwargs: get_order_details(context=context, **kwargs),
            agent="refund",
            description="Get order details for refund validation.",
        )
    )
    registry.register(
        ToolSpec(
            name="calculate_refund",
            handler=lambda **kwargs: calculate_refund(**kwargs),
            agent="refund",
            description="Calculate eligible refund amount.",
        )
    )
    registry.register(
        ToolSpec(
            name="process_refund",
            handler=lambda **kwargs: process_refund(context=context, **kwargs),
            agent="refund",
            description="Process an approved refund.",
        )
    )
    return registry
