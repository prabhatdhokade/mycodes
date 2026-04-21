"""Safety policies for input and output checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"override system",
    r"reveal .*prompt",
    r"delete .*database",
    r"drop table",
    r"bypass safety",
]

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


@dataclass
class GuardrailResult:
    blocked: bool = False
    reasons: list[str] = field(default_factory=list)
    sanitized_text: str = ""
    flags: list[str] = field(default_factory=list)


def check_input_guardrails(text: str) -> GuardrailResult:
    lowered = text.lower()
    reasons: list[str] = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            reasons.append(f"Possible prompt injection pattern matched: {pattern}")
    if reasons:
        return GuardrailResult(
            blocked=True,
            reasons=reasons,
            sanitized_text=text,
            flags=["input_injection"],
        )
    return GuardrailResult(blocked=False, sanitized_text=text)


def mask_pii(text: str) -> GuardrailResult:
    masked = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    masked = CARD_PATTERN.sub("[CARD_REDACTED]", masked)
    masked = PHONE_PATTERN.sub("[PHONE_REDACTED]", masked)
    changed = masked != text
    return GuardrailResult(
        blocked=False,
        sanitized_text=masked,
        flags=["pii_masked"] if changed else [],
    )
