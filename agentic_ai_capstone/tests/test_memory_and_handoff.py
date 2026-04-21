from agentic_ai_capstone import build_default_system


def test_memory_persistence_over_five_turns() -> None:
    system = build_default_system()
    customer_id = "cust-1001"
    prompts = [
        "Show my invoice inv-500",
        "Any payment history?",
        "My internet has an outage",
        "Please escalate and open a ticket",
        "I changed card, update payment method",
        "Can I get a refund for order ord-121 for $45?",
    ]
    result = None
    for prompt in prompts:
        result = system.respond(customer_id, prompt)

    assert result is not None
    history = system.memory.get_recent_messages(customer_id, limit=20)
    assert len(history) >= 6
    assert any("invoice" in item.lower() for item in history)


def test_agent_handoff_state_preserved() -> None:
    system = build_default_system()
    customer_id = "cust-1002"
    first = system.respond(customer_id, "My internet has outage, run diagnostics.")
    assert first["state"]["current_agent"] == "technical"
    second = system.respond(customer_id, "Also, I need invoice inv-501 details.")
    assert second["state"]["current_agent"] == "billing"
    assert second["state"]["customer_id"] == customer_id
    assert second["state"]["conversation_summary"]
