from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from customer_support_system.tools import billing, refund, technical


@dataclass
class ToolRegistry:
    tools: dict[str, Callable[..., dict[str, Any]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tools:
            self.tools = {
                "get_invoice": billing.get_invoice,
                "get_payment_history": billing.get_payment_history,
                "update_payment_method": billing.update_payment_method,
                "run_diagnostics": technical.run_diagnostics,
                "check_service_status": technical.check_service_status,
                "create_ticket": technical.create_ticket,
                "get_order_details": refund.get_order_details,
                "calculate_refund": refund.calculate_refund,
                "process_refund": refund.process_refund,
            }

    def call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        return self.tools[tool_name](**kwargs)
