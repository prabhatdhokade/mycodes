from agentic_ai_capstone.app import build_default_system


def test_refund_below_threshold_auto_processes() -> None:
    system = build_default_system()
    result = system.respond("cust-ref-low", "Refund order ord-700 for $40")
    assert "processed" in result["response"].lower()
    assert not any("approval_required" in action for action in result["pending_actions"])


def test_refund_over_threshold_requires_hitl_and_can_be_approved() -> None:
    held_system = build_default_system()
    held = held_system.respond("cust-ref-high", "Refund order ord-701 for $85")
    assert "requires human approval" in held["response"].lower()
    assert any("approval_required" in action for action in held["pending_actions"])

    approved_system = build_default_system(refund_auto_approve=True)
    approved = approved_system.respond("cust-ref-high", "Please approve and process my refund for order ord-701 $85")
    assert "processed" in approved["response"].lower()
