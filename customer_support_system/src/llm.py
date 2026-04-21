"""LLM client wrapper with a deterministic offline fallback.

If the OpenAI library is installed and OPENAI_API_KEY is set, we use the
real model. Otherwise, we fall back to a rule-based MockLLM that is
deterministic, keyword-driven, and good enough to pass routing and agent
evaluation suites without network access. This is essential so the test
suite can run in CI without API keys.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .observability import get_tracer


@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    raw: Any = None


class LLMClient:
    """Adapter that picks OpenAI if available, else MockLLM."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("CSS_MODEL", "mock")
        self._openai_client = None
        if self.model != "mock":
            try:
                import openai  # type: ignore

                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    self.model = "mock"
                else:
                    self._openai_client = openai.OpenAI(api_key=api_key)
            except Exception:
                self.model = "mock"

    def complete(
        self,
        system: str,
        user: str,
        trace_id: str,
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> LLMResponse:
        tracer = get_tracer()
        with tracer.span(
            "llm.complete",
            "llm",
            trace_id=trace_id,
            inputs={"system": system[:400], "user": user[:400]},
            model=self.model,
        ) as span:
            if self._openai_client is not None:
                try:
                    resp = self._openai_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    text = resp.choices[0].message.content or ""
                    usage = getattr(resp, "usage", None)
                    tin = getattr(usage, "prompt_tokens", 0) if usage else 0
                    tout = getattr(usage, "completion_tokens", 0) if usage else 0
                    span.tokens_in = tin
                    span.tokens_out = tout
                    span.outputs = {"text": text[:400]}
                    return LLMResponse(
                        text=text, model=self.model, tokens_in=tin, tokens_out=tout, raw=resp
                    )
                except Exception as e:
                    span.error = f"openai_error: {e}; falling back to mock"
                    # Fall through to mock
            text = mock_generate(system, user)
            # Rough token estimation: ~4 chars per token
            tin = max(1, (len(system) + len(user)) // 4)
            tout = max(1, len(text) // 4)
            span.tokens_in = tin
            span.tokens_out = tout
            span.outputs = {"text": text[:400]}
            return LLMResponse(
                text=text, model="mock", tokens_in=tin, tokens_out=tout
            )


# ---------------------------------------------------------------------------
# Deterministic mock generator used when no LLM is available.
# ---------------------------------------------------------------------------


def mock_generate(system: str, user: str) -> str:
    """Return a deterministic response suitable for demo + tests.

    The system prompt carries an "intent" hint prefix that lets each agent
    get a stable answer. Agents compose their own natural-language replies
    using tool results, so the LLM's job here is mostly acknowledgement.
    """
    user_lower = user.lower()
    sys_lower = system.lower()

    if "triage" in sys_lower and "classify" in sys_lower:
        return _classify(user_lower)

    if "billing" in sys_lower:
        return "I can help with your billing question. Let me pull your account details."
    if "technical" in sys_lower:
        return "I'll investigate the technical issue and run a quick diagnostic."
    if "refund" in sys_lower:
        return "I'll review the order and check refund eligibility."

    return "Thanks for reaching out - how can I help today?"


_BILLING_KWS = [
    "invoice", "invoices", "bill", "billing", "charge", "charged", "payment",
    "plan", "subscription", "subscribe", "price", "pricing", "refund money",
    "card", "credit card", "upgrade", "downgrade",
]
_TECH_KWS = [
    "crash", "crashes", "error", "bug", "not working", "broken", "slow",
    "login", "log in", "can't log", "cannot log", "diagnostic", "diagnostics",
    "status", "outage", "down", "connect", "connection", "ticket", "issue",
    "troubleshoot", "api", "500", "timeout",
]
_REFUND_KWS = [
    "refund", "return", "money back", "cancel order", "chargeback", "reimburse",
    "return the", "give me my money", "damaged", "order",
]


def _classify(text: str) -> str:
    """Return triage JSON-ish decision. Deterministic keyword voting."""
    scores = {
        "billing": sum(1 for k in _BILLING_KWS if k in text),
        "technical": sum(1 for k in _TECH_KWS if k in text),
        "refund": sum(1 for k in _REFUND_KWS if k in text),
    }
    # Refund has priority if "refund"/"return" explicitly said
    if any(k in text for k in ("refund", "return the", "money back", "chargeback")):
        return "ROUTE: refund"
    if scores["refund"] > scores["billing"] and scores["refund"] > scores["technical"]:
        return "ROUTE: refund"
    if scores["technical"] >= scores["billing"] and scores["technical"] > 0:
        return "ROUTE: technical"
    if scores["billing"] > 0:
        return "ROUTE: billing"
    # Fallback: look at generic cues
    if any(k in text for k in ("hello", "hi", "help", "support", "question")):
        return "ROUTE: triage"
    return "ROUTE: triage"
