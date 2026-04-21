"""Memory store tests."""
import json
import os

from src.memory.store import CustomerProfile, MemoryStore


def test_upsert_and_get(tmp_path):
    store = MemoryStore(path=str(tmp_path / "m.json"))
    store.upsert(CustomerProfile(customer_id="c1", name="Alice", plan="pro"))
    got = store.get("c1")
    assert got.name == "Alice"
    assert got.plan == "pro"


def test_append_message_rolls_window(tmp_path):
    store = MemoryStore(path=str(tmp_path / "m.json"))
    for i in range(250):
        store.append_message("c1", {"role": "user", "content": f"msg{i}"})
    profile = store.get("c1")
    assert len(profile.conversation_log) == 200
    assert profile.conversation_log[0]["content"] == "msg50"


def test_persistence_round_trip(tmp_path):
    p = tmp_path / "m.json"
    s1 = MemoryStore(path=str(p))
    s1.upsert(CustomerProfile(customer_id="c1", name="A"))
    s1.set_preference("c1", "notify", "email")
    s1.add_ticket("c1", {"ticket_id": "TCK-1", "subject": "hi"})

    s2 = MemoryStore(path=str(p))
    prof = s2.get("c1")
    assert prof.name == "A"
    assert prof.preferences["notify"] == "email"
    assert prof.past_tickets[0]["ticket_id"] == "TCK-1"


def test_summary_updated(tmp_path):
    store = MemoryStore(path=str(tmp_path / "m.json"))
    store.update_summary("c1", "billing, refund")
    assert store.get("c1").summary == "billing, refund"
