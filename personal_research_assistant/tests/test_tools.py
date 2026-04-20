from __future__ import annotations

import json

from personal_research_assistant.app.memory import FactStore
from personal_research_assistant.app.tools import (
    CalendarLookupTool,
    FactLookupTool,
    NoteSaverTool,
    WebSearchTool,
)


def test_web_search_mock_returns_results(isolated_data_dir):
    tool = WebSearchTool()
    result = tool.invoke({"query": "ReAct prompting", "k": 2})
    assert result.ok is True
    payload = json.loads(result.output)
    assert payload["query"] == "ReAct prompting"
    assert 0 < len(payload["results"]) <= 2


def test_note_saver_requires_approval(isolated_data_dir):
    store = FactStore()
    tool = NoteSaverTool(fact_store=store)

    r = tool.invoke({"title": "x", "content": "y", "important": True})
    assert r.ok is False
    assert not store.all()

    r = tool.invoke(
        {"title": "VPN", "content": "Rotate monthly", "important": True},
        approval=lambda _t, _a: False,
    )
    assert r.ok is False
    assert not store.all()

    r = tool.invoke(
        {"title": "VPN", "content": "Rotate monthly", "important": True},
        approval=lambda _t, _a: True,
    )
    assert r.ok is True
    assert len(store.all()) == 1
    assert store.all()[0].importance == 5


def test_calendar_today_and_keyword(isolated_data_dir):
    tool = CalendarLookupTool()
    today = json.loads(tool.invoke({"query": "today"}).output)
    assert today["window"] == "today"
    assert len(today["events"]) >= 1

    dentist = json.loads(tool.invoke({"query": "dentist"}).output)
    assert any("Dentist" in e["title"] for e in dentist["events"])


def test_fact_lookup(isolated_data_dir):
    store = FactStore()
    store.add("The mitochondria is the powerhouse of the cell", importance=4)
    tool = FactLookupTool(fact_store=store)
    payload = json.loads(tool.invoke({"query": "mitochondria"}).output)
    assert payload["results"], "expected recall to find the fact"
    assert "mitochondria" in payload["results"][0]["content"].lower()
