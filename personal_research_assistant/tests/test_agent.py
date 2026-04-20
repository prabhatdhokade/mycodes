from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.agent import PersonalResearchAssistant


def build_agent(tmp_dir: Path, auto_approve: bool = True) -> PersonalResearchAssistant:
    return PersonalResearchAssistant.with_defaults(
        base_dir=str(tmp_dir),
        auto_approve_notes=auto_approve,
        enable_streaming=False,
        summarize_after_turns=6,
        interactive_hitl=False,
    )


def _read_log_events(tmp_dir: Path) -> list[dict]:
    log_path = tmp_dir / "logs" / "agent.log"
    if not log_path.exists():
        return []
    events: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def test_routes_search_intent_and_logs_tool() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp_dir = Path(d)
        agent = build_agent(tmp_dir)
        result = agent.handle_turn("search latest ai regulation updates")
        assert "Mock search results" in result.text
        assert "web_search" in result.used_tools

        events = _read_log_events(tmp_dir)
        event_types = {item["event_type"] for item in events}
        assert "agent_decision" in event_types
        assert "tool_invocation" in event_types
        assert "llm_call" in event_types


def test_long_term_memory_persists_across_instances() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp_dir = Path(d)
        agent_one = build_agent(tmp_dir)
        save_result = agent_one.handle_turn("remember this: I prefer MLA citations")
        assert "Saved note" in save_result.text

        agent_two = build_agent(tmp_dir)
        recall_result = agent_two.handle_turn("what do you remember about citations?")
        assert "I prefer MLA citations" in recall_result.text


def test_hitl_blocks_important_note_when_rejected() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp_dir = Path(d)
        agent = build_agent(tmp_dir, auto_approve=False)
        result = agent.handle_turn("save important note: approve contract by monday")
        assert "declined" in result.text.lower()

        facts_path = tmp_dir / "memory" / "facts.json"
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        assert facts == []


def test_conversation_summary_triggers_when_context_grows() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp_dir = Path(d)
        agent = build_agent(tmp_dir, auto_approve=True)
        for i in range(4):
            agent.handle_turn(f"search topic {i}")

        events = _read_log_events(tmp_dir)
        assert any(item["event_type"] == "conversation_summary" for item in events)
