"""Input guardrails: prompt-injection detection + PII masking.

The detector is intentionally conservative: it blocks only when we see
high-confidence jailbreak patterns. Softer signals emit a flag but the
message is still passed through (PII-masked) to the agent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from .pii import mask_pii, PIIMatch

# High-signal prompt injection patterns observed in the wild.
INJECTION_PATTERNS = [
    # "ignore/disregard [the] (above|all|previous|prior) [anything] (instructions|prompts|messages|rules)"
    r"\b(?:ignore|disregard|forget)\b[^.\n]{0,80}?\b(?:instructions|prompts|messages|rules|system\s+prompt)\b",
    r"\bforget\s+(?:everything|all|prior|previous)\b",
    r"(?:^|\s)(?:act|pretend|roleplay)\s+as\s+(?:a\s+)?(?:dan|admin|root|system|developer)",
    r"\byou\s+are\s+now\s+(?:dan|jailbroken|unrestricted|free)",
    r"\breveal\s+(?:your\s+)?(?:system\s+prompt|instructions|hidden\s+prompt)",
    r"\bprint\s+(?:your\s+)?system\s+prompt",
    r"<\s*\|?\s*(?:system|assistant)\s*\|?\s*>",
    r"\bBEGIN\s+NEW\s+INSTRUCTIONS\b",
    r"\bpretend\s+to\s+be\s+(?:an?\s+)?(?:admin|root|system|developer|dan)\b",
]
# Soft signals: worth flagging but not blocking on their own.
SOFT_PATTERNS = [
    r"\bnew\s+instructions\b",
    r"\boverride\b",
]

_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)
_SOFT_RE = re.compile("|".join(SOFT_PATTERNS), re.IGNORECASE)


@dataclass
class GuardrailDecision:
    allowed: bool
    sanitized_text: str
    flags: List[dict]
    pii_matches: List[PIIMatch]


class InputGuardrails:
    def __init__(self, block_injections: bool = True, mask_pii: bool = True):
        self.block_injections = block_injections
        self.mask_pii = mask_pii

    def check(self, text: str) -> GuardrailDecision:
        flags: List[dict] = []
        if _INJECTION_RE.search(text):
            flags.append(
                {
                    "kind": "injection",
                    "severity": "high",
                    "direction": "input",
                    "detail": "Prompt-injection pattern detected.",
                }
            )
        if _SOFT_RE.search(text) and not _INJECTION_RE.search(text):
            flags.append(
                {
                    "kind": "injection",
                    "severity": "low",
                    "direction": "input",
                    "detail": "Soft injection-like phrase detected.",
                }
            )

        sanitized, matches = (mask_pii(text) if self.mask_pii else (text, []))
        if matches:
            flags.append(
                {
                    "kind": "pii",
                    "severity": "medium",
                    "direction": "input",
                    "detail": f"PII redacted: {', '.join(sorted({m.kind for m in matches}))}",
                }
            )

        allowed = True
        if self.block_injections and any(
            f["kind"] == "injection" and f["severity"] == "high" for f in flags
        ):
            allowed = False

        return GuardrailDecision(
            allowed=allowed, sanitized_text=sanitized, flags=flags, pii_matches=matches
        )


def check_input(text: str) -> GuardrailDecision:
    return InputGuardrails().check(text)
