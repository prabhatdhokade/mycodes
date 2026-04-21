from __future__ import annotations

from dataclasses import dataclass

from customer_support_system.knowledge import retrieve_knowledge
from customer_support_system.tracing import TraceRecorder


@dataclass
class BaseAgent:
    name: str
    recorder: TraceRecorder

    def knowledge(self, query: str) -> list[str]:
        snippets = retrieve_knowledge(self.name, query)
        self.recorder.event("knowledge", self.name, {"query": query, "snippets": snippets})
        return snippets
