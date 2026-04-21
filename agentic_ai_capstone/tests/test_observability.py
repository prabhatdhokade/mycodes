from __future__ import annotations

from agentic_ai_capstone.app import build_default_system


def test_trace_and_cost_are_recorded_for_calls() -> None:
    system = build_default_system()
    _ = system.respond("cust-1001", "Show invoice and payment history.")
    summary = system.engine.tracer.summary()

    assert summary["llm_calls"] >= 2
    assert summary["estimated_tokens"] > 0
    assert summary["estimated_cost_usd"] > 0
