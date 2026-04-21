from __future__ import annotations

import re

PII_PATTERNS = [
    re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    re.compile(r"\+?\d[\d -]{8,}\d"),
]
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass guardrails",
    "pretend you are the system",
    "drop all safety rules",
]


def _mask(match: re.Match[str]) -> str:
    text = match.group(0)
    digits = [char for char in text if char.isdigit()]
    if len(digits) <= 4:
        return "[REDACTED]"
    return f"[REDACTED:{''.join(digits[-4:])}]"


def apply_input_guardrails(user_input: str) -> dict[str, object]:
    lowered = user_input.lower()
    blocked = any(pattern in lowered for pattern in INJECTION_PATTERNS)
    flags: list[str] = []
    sanitized = user_input
    if blocked:
        flags.append("prompt_injection")
    for pattern in PII_PATTERNS:
        if pattern.search(sanitized):
            flags.append("pii_masked")
            sanitized = pattern.sub(_mask, sanitized)
    return {
        "blocked": blocked,
        "sanitized_input": sanitized,
        "guardrail_flags": sorted(set(flags)),
    }
