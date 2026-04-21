from __future__ import annotations

from agentic_ai_capstone.agents.router import TriageRouter


def test_routing_billing() -> None:
    router = TriageRouter()
    result = router.classify("Please show my invoice and payment history.")
    assert result.route == "billing"
    assert result.confidence >= 0.9


def test_routing_technical() -> None:
    router = TriageRouter()
    result = router.classify("My internet has high latency and errors.")
    assert result.route == "technical"


def test_routing_refund() -> None:
    router = TriageRouter()
    result = router.classify("I need a refund for my order.")
    assert result.route == "refund"


def test_routing_default_triage() -> None:
    router = TriageRouter()
    result = router.classify("Hello, can you help me?")
    assert result.route == "triage"
