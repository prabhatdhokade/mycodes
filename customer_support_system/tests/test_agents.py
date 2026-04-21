"""Agent-level tests covering routing, handoff and response shape."""
import pytest

from src.agents.triage import TriageAgent
from src.agents.billing import BillingAgent
from src.agents.refund import RefundAgent
from src.agents.technical import TechnicalAgent
from src.llm import LLMClient
from src.observability import Tracer, set_tracer
from src.state import new_state
from src.tools.registry import get_default_registry


@pytest.fixture(autouse=True)
def _reset_tracer():
    set_tracer(Tracer())
    yield


def _state(agent="triage"):
    return new_state(customer_id="cust_001", trace_id="trace_t", initial_agent=agent)


class TestTriage:
    @pytest.mark.parametrize("text,expected", [
        ("I want to see my invoice", "billing"),
        ("My app keeps crashing", "technical"),
        ("I want a refund for my order", "refund"),
        ("Can you update my payment method?", "billing"),
        ("Is the auth service down?", "technical"),
    ])
    def test_classify(self, text, expected):
        agent = TriageAgent(get_default_registry(), LLMClient())
        result = agent.classify(text, trace_id="trace_t")
        assert result == expected

    def test_handoff_response(self):
        agent = TriageAgent(get_default_registry(), LLMClient())
        state = _state()
        resp = agent.handle(state, "refund order ORD-5001")
        assert resp.handoff_to == "refund"


class TestBilling:
    def test_invoice_response(self):
        a = BillingAgent(get_default_registry(), LLMClient())
        state = _state("billing")
        resp = a.handle(state, "Show me invoice INV-1001")
        assert "INV-1001" in resp.text
        assert any(tc["name"] == "get_invoice" for tc in resp.tool_calls)

    def test_payment_history(self):
        a = BillingAgent(get_default_registry(), LLMClient())
        state = _state("billing")
        resp = a.handle(state, "What's my payment history?")
        assert any(tc["name"] == "get_payment_history" for tc in resp.tool_calls)

    def test_plan_question_no_tool(self):
        a = BillingAgent(get_default_registry(), LLMClient())
        state = _state("billing")
        resp = a.handle(state, "What plans do you offer?")
        assert "Pro" in resp.text


class TestTechnical:
    def test_diagnostics(self):
        a = TechnicalAgent(get_default_registry(), LLMClient())
        state = _state("technical")
        resp = a.handle(state, "Run diagnostics please")
        assert any(tc["name"] == "run_diagnostics" for tc in resp.tool_calls)

    def test_status_single(self):
        a = TechnicalAgent(get_default_registry(), LLMClient())
        state = _state("technical")
        resp = a.handle(state, "Is the api service down?")
        assert any(tc["name"] == "check_service_status" for tc in resp.tool_calls)
        assert "api" in resp.text.lower()

    def test_create_ticket(self):
        a = TechnicalAgent(get_default_registry(), LLMClient())
        state = _state("technical")
        resp = a.handle(state, "Please create a ticket for my login issue")
        assert any(tc["name"] == "create_ticket" for tc in resp.tool_calls)
        assert "TCK-" in resp.text


class TestRefund:
    def test_small_refund_auto(self):
        a = RefundAgent(get_default_registry(), LLMClient())
        state = _state("refund")
        resp = a.handle(state, "Refund order ORD-5001")
        assert "processed" in resp.text.lower() or "refund" in resp.text.lower()
        assert not resp.hitl_required

    def test_large_refund_requires_hitl(self):
        a = RefundAgent(get_default_registry(), LLMClient())
        state = _state("refund")
        resp = a.handle(state, "Please refund ORD-5002")
        assert resp.hitl_required is True
        assert resp.pending_action is not None

    def test_policy_response(self):
        a = RefundAgent(get_default_registry(), LLMClient())
        state = _state("refund")
        resp = a.handle(state, "What is your refund policy?")
        assert "30 days" in resp.text

    def test_missing_order_asks(self):
        a = RefundAgent(get_default_registry(), LLMClient())
        state = _state("refund")
        resp = a.handle(state, "I need a refund")
        assert "order" in resp.text.lower()
