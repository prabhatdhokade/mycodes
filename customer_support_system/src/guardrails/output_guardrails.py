"""Output guardrails: toxicity + PII leakage + policy checks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .pii import mask_pii, PIIMatch

# Lightweight toxicity lexicon. In production swap for Perspective API /
# openai moderation. This is kept conservative and focused on the most
# common abusive categories a support bot must never output.
TOXIC_TERMS = [
    r"\b(?:kill|die|hate|stupid|idiot|moron|dumb|loser)\b",
    r"\b(?:shut\s+up|screw\s+you|go\s+away)\b",
]
_TOXIC_RE = re.compile("|".join(TOXIC_TERMS), re.IGNORECASE)

# Refuse to echo back secrets.
SECRET_LEAK = re.compile(
    r"(api[_\s-]?key|secret[_\s-]?key|password|bearer\s+[A-Za-z0-9_\-\.]+)",
    re.IGNORECASE,
)


@dataclass
class OutputDecision:
    allowed: bool
    sanitized_text: str
    flags: List[dict]


class OutputGuardrails:
    def __init__(self, mask_pii: bool = True):
        self.mask_pii = mask_pii

    def check(self, text: str) -> OutputDecision:
        flags: List[dict] = []
        if _TOXIC_RE.search(text):
            flags.append(
                {
                    "kind": "toxicity",
                    "severity": "high",
                    "direction": "output",
                    "detail": "Toxic language detected in model output.",
                }
            )
        if SECRET_LEAK.search(text):
            flags.append(
                {
                    "kind": "policy",
                    "severity": "high",
                    "direction": "output",
                    "detail": "Possible secret/credential leak in output.",
                }
            )

        sanitized, matches = (mask_pii(text) if self.mask_pii else (text, []))
        if matches:
            flags.append(
                {
                    "kind": "pii",
                    "severity": "medium",
                    "direction": "output",
                    "detail": f"PII redacted in output: {', '.join(sorted({m.kind for m in matches}))}",
                }
            )

        allowed = not any(f["severity"] == "high" for f in flags)
        if not allowed:
            sanitized = (
                "I'm not able to share that response. A human agent has been "
                "notified to follow up."
            )
        return OutputDecision(allowed=allowed, sanitized_text=sanitized, flags=flags)


def check_output(text: str) -> OutputDecision:
    return OutputGuardrails().check(text)
