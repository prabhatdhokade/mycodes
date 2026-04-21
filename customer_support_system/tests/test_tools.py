"""Unit tests for tool registry and individual tools."""
import pytest

from src.tools.registry import ToolRegistry, Tool, ToolResult, get_default_registry
from src.tools import billing_tools, refund_tools, technical_tools


class TestRegistry:
    def test_register_and_get(self):
        reg = ToolRegistry()
        billing_tools.register(reg)
        assert reg.get("get_invoice").owner_agent == "billing"

    def test_list_for_agent(self):
        reg = get_default_registry()
        billing = [t.name for t in reg.list_for_agent("billing")]
        tech = [t.name for t in reg.list_for_agent("technical")]
        refund = [t.name for t in reg.list_for_agent("refund")]
        assert {"get_invoice", "get_payment_history", "update_payment_method"} <= set(billing)
        assert {"run_diagnostics", "check_service_status", "create_ticket"} <= set(tech)
        assert {"get_order_details", "calculate_refund", "process_refund"} <= set(refund)

    def test_min_two_tools_per_agent(self):
        reg = get_default_registry()
        for agent in ("billing", "technical", "refund"):
            assert len(reg.list_for_agent(agent)) >= 2

    def test_duplicate_register_raises(self):
        reg = ToolRegistry()
        billing_tools.register(reg)
        with pytest.raises(ValueError):
            billing_tools.register(reg)


class TestBillingTools:
    def test_get_invoice_latest(self):
        res = billing_tools.get_invoice("cust_001")
        assert res.ok
        assert "latest" in res.data

    def test_get_invoice_specific(self):
        res = billing_tools.get_invoice("cust_001", "INV-1001")
        assert res.ok
        assert res.data["invoice_id"] == "INV-1001"

    def test_get_invoice_missing(self):
        res = billing_tools.get_invoice("cust_001", "INV-9999")
        assert not res.ok

    def test_payment_history(self):
        res = billing_tools.get_payment_history("cust_001")
        assert res.ok
        assert res.data["count"] >= 1

    def test_update_payment_method(self):
        res = billing_tools.update_payment_method("cust_001", "amex-0007")
        assert res.ok
        assert res.data["new_method"] == "amex-0007"

    def test_update_payment_method_invalid(self):
        res = billing_tools.update_payment_method("cust_001", "")
        assert not res.ok


class TestTechnicalTools:
    def test_diagnostics_is_deterministic(self):
        r1 = technical_tools.run_diagnostics("cust_001", "app")
        r2 = technical_tools.run_diagnostics("cust_001", "app")
        assert r1.data == r2.data

    def test_check_service_all(self):
        res = technical_tools.check_service_status("all")
        assert res.ok
        assert "services" in res.data

    def test_check_service_one(self):
        res = technical_tools.check_service_status("api")
        assert res.ok
        assert res.data["service"] == "api"

    def test_check_service_unknown(self):
        res = technical_tools.check_service_status("nope")
        assert not res.ok

    def test_create_ticket(self):
        res = technical_tools.create_ticket(
            "cust_001", "bug", "description here", "high"
        )
        assert res.ok
        assert res.data["ticket_id"].startswith("TCK-")

    def test_create_ticket_bad_priority(self):
        res = technical_tools.create_ticket("cust_001", "s", "d", "whenever")
        assert not res.ok


class TestRefundTools:
    def test_get_order(self):
        res = refund_tools.get_order_details("ORD-5001")
        assert res.ok

    def test_calculate_refund_small(self):
        res = refund_tools.calculate_refund("ORD-5001")
        assert res.ok
        assert res.data["requires_hitl"] is False

    def test_calculate_refund_large(self):
        res = refund_tools.calculate_refund("ORD-5002")
        assert res.ok
        assert res.data["requires_hitl"] is True

    def test_process_refund_rejects_overage(self):
        res = refund_tools.process_refund("ORD-5001", 1000.0)
        assert not res.ok

    def test_process_refund_happy_path(self):
        res = refund_tools.process_refund("ORD-5003", 9.0)
        assert res.ok
        assert res.data["status"] == "refunded"


class TestHITLGating:
    def test_tool_call_requires_hitl_for_large_amount(self):
        reg = get_default_registry()
        res = reg.call(
            "process_refund",
            {"order_id": "ORD-5002", "amount": 158.0},
            trace_id="trace_test",
        )
        assert res.hitl_required is True
        assert res.ok is False

    def test_tool_call_approved_executes(self):
        reg = get_default_registry()
        res = reg.call(
            "process_refund",
            {"order_id": "ORD-5002", "amount": 158.0},
            trace_id="trace_test",
            hitl_decision="approve",
        )
        assert res.ok is True

    def test_tool_call_denied(self):
        reg = get_default_registry()
        res = reg.call(
            "process_refund",
            {"order_id": "ORD-5002", "amount": 158.0},
            trace_id="trace_test",
            hitl_decision="deny",
        )
        assert not res.ok
