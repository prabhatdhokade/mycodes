"""PII detection and masking using deterministic regex patterns.

Covers: emails, phone numbers (US + intl-ish), credit card numbers (Luhn
checked), and SSN-like patterns. For a production system this would be
augmented with Microsoft Presidio / spaCy NER.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?:(?<!\d)(?:\+?\d{1,3}[\s\-.])?(?:\(?\d{3}\)?[\s\-.])\d{3}[\s\-.]\d{4}(?!\d))"
)
CREDIT_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _luhn(s: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", s)]
    if not (13 <= len(digits) <= 19):
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@dataclass
class PIIMatch:
    kind: str
    value: str
    start: int
    end: int


def find_pii(text: str) -> List[PIIMatch]:
    """Return all PII matches in the text."""
    matches: List[PIIMatch] = []
    for m in EMAIL_RE.finditer(text):
        matches.append(PIIMatch("email", m.group(), m.start(), m.end()))
    for m in PHONE_RE.finditer(text):
        matches.append(PIIMatch("phone", m.group(), m.start(), m.end()))
    for m in CREDIT_RE.finditer(text):
        val = m.group()
        if _luhn(val):
            matches.append(PIIMatch("credit_card", val, m.start(), m.end()))
    for m in SSN_RE.finditer(text):
        matches.append(PIIMatch("ssn", m.group(), m.start(), m.end()))
    return matches


def mask_pii(text: str) -> Tuple[str, List[PIIMatch]]:
    """Replace PII with typed placeholders, returning masked text and matches."""
    matches = find_pii(text)
    if not matches:
        return text, []
    matches_sorted = sorted(matches, key=lambda m: m.start, reverse=True)
    masked = text
    for m in matches_sorted:
        placeholder = f"[REDACTED_{m.kind.upper()}]"
        masked = masked[: m.start] + placeholder + masked[m.end :]
    return masked, list(reversed(matches_sorted))
