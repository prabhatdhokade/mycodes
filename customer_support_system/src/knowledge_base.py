"""In-memory knowledge base for product docs, FAQs, and policies.

Small TF-IDF-ish keyword search is used so the system works with zero
external dependencies. The retrieval interface is kept compatible with a
vector-store replacement (FAISS/Chroma/etc.).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


@dataclass
class Document:
    doc_id: str
    category: str  # "product" | "faq" | "policy"
    title: str
    content: str


DEFAULT_DOCS: List[Document] = [
    Document(
        "policy.refund",
        "policy",
        "Refund Policy",
        "Refunds are available within 30 days of purchase. Orders over $50 "
        "require manager approval. Digital goods are non-refundable after "
        "activation. Partial refunds available for damaged items.",
    ),
    Document(
        "policy.privacy",
        "policy",
        "Privacy Policy",
        "We never share personal data without consent. PII is encrypted at "
        "rest. Customers may request deletion of their data at any time.",
    ),
    Document(
        "faq.payment",
        "faq",
        "Payment Methods",
        "We accept Visa, Mastercard, Amex, PayPal, and bank transfer. "
        "Update your payment method in Account > Billing.",
    ),
    Document(
        "faq.plans",
        "faq",
        "Plan Tiers",
        "Basic: $9/mo, Pro: $29/mo, Enterprise: contact sales. Plan changes "
        "take effect on the next billing cycle.",
    ),
    Document(
        "faq.invoice",
        "faq",
        "Invoices",
        "Invoices are emailed on the 1st of each month and available in "
        "Account > Billing > Invoices. PDF downloads supported.",
    ),
    Document(
        "product.troubleshoot",
        "product",
        "Troubleshooting Guide",
        "If the app is slow, try clearing cache and restarting. If login "
        "fails, check network and reset password. For crashes, send logs "
        "via Help > Report issue.",
    ),
    Document(
        "product.diagnostics",
        "product",
        "Diagnostics",
        "Run system diagnostics from Settings > Advanced > Run diagnostic. "
        "This reports CPU, memory, and network health.",
    ),
    Document(
        "product.status",
        "product",
        "Service Status",
        "Check https://status.example.com for live service health. Known "
        "incidents are posted within 5 minutes of detection.",
    ),
]


class KnowledgeBase:
    def __init__(self, docs: List[Document] | None = None):
        self.docs: List[Document] = docs or DEFAULT_DOCS
        self._index: Dict[str, Dict[int, int]] = {}
        self._build_index()

    def _build_index(self) -> None:
        self._index.clear()
        for i, doc in enumerate(self.docs):
            for tok in _tokenize(doc.title + " " + doc.content):
                self._index.setdefault(tok, {}).setdefault(i, 0)
                self._index[tok][i] += 1

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scores: Dict[int, float] = {}
        n_docs = len(self.docs)
        for tok in query_tokens:
            postings = self._index.get(tok, {})
            if not postings:
                continue
            idf = math.log((n_docs + 1) / (len(postings) + 1)) + 1
            for doc_idx, tf in postings.items():
                scores[doc_idx] = scores.get(doc_idx, 0.0) + tf * idf
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [(self.docs[i], s) for i, s in ranked]

    def lookup(self, doc_id: str) -> Document | None:
        for d in self.docs:
            if d.doc_id == doc_id:
                return d
        return None
