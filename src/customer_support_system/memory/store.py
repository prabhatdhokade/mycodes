from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from customer_support_system.data import CUSTOMERS


@dataclass
class MemoryStore:
    _store: dict[str, dict[str, Any]] = field(default_factory=dict)

    def load(self, customer_id: str) -> dict[str, Any]:
        if customer_id not in self._store:
            customer = CUSTOMERS.get(customer_id, {})
            self._store[customer_id] = {
                "history": [],
                "summary": "",
                "preferences": {
                    "plan": customer.get("plan"),
                    "preferred_contact": customer.get("preferred_contact"),
                },
                "last_ticket_id": None,
                "last_order_id": None,
            }
        return self._store[customer_id]

    def save_turn(self, customer_id: str, user_input: str, response: str, route: str, ticket_id: str | None, summary: str, order_id: str | None = None) -> dict[str, Any]:
        memory = self.load(customer_id)
        memory["history"].append(
            {
                "user_input": user_input,
                "response": response,
                "route": route,
            }
        )
        memory["history"] = memory["history"][-10:]
        memory["summary"] = summary
        if ticket_id:
            memory["last_ticket_id"] = ticket_id
        if order_id:
            memory["last_order_id"] = order_id
        return memory
