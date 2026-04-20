from __future__ import annotations

from personal_research_assistant.app.memory import (
    ConversationMemory,
    FactStore,
    PreferenceStore,
)


def test_conversation_persists_roundtrip(isolated_data_dir):
    conv = ConversationMemory(session_id="s1")
    conv.add("user", "hello")
    conv.add("assistant", "hi there")

    other = ConversationMemory(session_id="s1")
    assert [m.role for m in other.messages] == ["user", "assistant"]
    assert other.messages[-1].content == "hi there"


def test_facts_search_and_importance_ranking(isolated_data_dir):
    store = FactStore()
    a = store.add("Python prefers duck typing", importance=1)
    b = store.add("I love climbing granite in Yosemite", importance=5)
    c = store.add("Python type hints via typing module", importance=3)

    hits = store.search("python typing", k=3)
    assert hits, "expected at least one hit"
    top_ids = [f.id for f, _ in hits]
    assert c.id in top_ids
    climbing_ids = [f.id for f, _ in store.search("climbing yosemite", k=1)]
    assert climbing_ids == [b.id]
    assert store.delete(a.id) is True


def test_preferences_roundtrip(isolated_data_dir):
    prefs = PreferenceStore()
    prefs.set("name", "Ada")
    assert PreferenceStore().get("name") == "Ada"
    assert PreferenceStore().delete("name") is True
    assert PreferenceStore().get("name") is None
