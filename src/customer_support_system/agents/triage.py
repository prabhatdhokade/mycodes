from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.model import DeterministicSupportModel


@dataclass
class TriageAgent:
    model: DeterministicSupportModel

    def route(self, user_input: str) -> str:
        return self.model.route(user_input)
