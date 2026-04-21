from __future__ import annotations

from agentic_ai_capstone.app import build_default_system


def test_each_agent_has_at_least_two_tools() -> None:
    system = build_default_system()
    registry = system.engine.tool_registry
    assert len(registry.list_tools("billing")) >= 2
    assert len(registry.list_tools("technical")) >= 2
    assert len(registry.list_tools("refund")) >= 2
