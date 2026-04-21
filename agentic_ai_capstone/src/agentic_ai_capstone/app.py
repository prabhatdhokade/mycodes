"""High-level wrapper around the support engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .engine import CustomerSupportEngine


@dataclass
class CustomerSupportSystem:
    """Convenience facade for app/demo/test use."""

    engine: CustomerSupportEngine
    _session_states: dict[str, dict] = None

    def __post_init__(self) -> None:
        if self._session_states is None:
            self._session_states = {}

    def respond(
        self,
        customer_id: str,
        user_message: str,
        human_approval: bool = False,
    ) -> dict[str, Any]:
        prior_state = self._session_states.get(customer_id)
        result = self.engine.respond(
            customer_id=customer_id,
            user_message=user_message,
            human_approval=human_approval,
            prior_state=prior_state,
        )
        self._session_states[customer_id] = result["state"]
        return result

    def handle(
        self,
        customer_id: str,
        message: str,
        human_approval: bool = False,
    ) -> dict[str, Any]:
        return self.respond(customer_id=customer_id, user_message=message, human_approval=human_approval)

    @property
    def memory(self):
        return self.engine.memory_store


def build_default_system(
    refund_auto_approve: bool = False,
    refund_approver: Callable[[str, float], bool] | None = None,
) -> CustomerSupportSystem:
    approver = refund_approver or (lambda _cid, amount: refund_auto_approve and amount > 50.0)
    return CustomerSupportSystem(engine=CustomerSupportEngine(refund_approver=approver))
