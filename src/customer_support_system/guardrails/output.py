from __future__ import annotations

import re

TOXIC_PATTERNS = ["idiot", "stupid", "hate you"]
NUMBER_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
CARD_SUFFIX_PATTERN = re.compile(r"ending\s+\d{4}", re.IGNORECASE)


def apply_output_guardrails(response: str) -> dict[str, object]:
    sanitized = response
    flags: list[str] = []
    if any(pattern in sanitized.lower() for pattern in TOXIC_PATTERNS):
        flags.append("toxicity_filtered")
        for token in TOXIC_PATTERNS:
            sanitized = sanitized.replace(token, "[filtered]")
            sanitized = sanitized.replace(token.title(), "[filtered]")
    if NUMBER_PATTERN.search(sanitized):
        flags.append("pii_masked")
        sanitized = NUMBER_PATTERN.sub("[REDACTED]", sanitized)
    if CARD_SUFFIX_PATTERN.search(sanitized):
        flags.append("pii_masked")
        sanitized = CARD_SUFFIX_PATTERN.sub("ending [REDACTED]", sanitized)
    return {"response": sanitized, "guardrail_flags": sorted(set(flags))}
