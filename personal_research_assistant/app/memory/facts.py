"""Long-term fact storage with a lightweight vector-ish retriever.

A real deployment would use Chroma / FAISS / pgvector. To keep this
project dependency-free (and easy to run in evaluation environments),
facts are stored as JSON on disk and retrieved with a tiny token-overlap
similarity score. The interface mirrors a vector store so swapping in a
real backend is a one-file change.
"""

from __future__ import annotations

import json
import math
import re
import uuid
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import time

from ..config import settings
from ..observability import get_logger, log_event

logger = get_logger("memory.facts")


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


@dataclass
class Fact:
    id: str
    content: str
    tags: list[str] = field(default_factory=list)
    source: str = "user"
    importance: int = 3  # 1..5, 5 is most important
    ts: float = field(default_factory=time)

    def as_dict(self) -> dict:
        return asdict(self)


class FactStore:
    """On-disk JSON fact store with token-overlap retrieval."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.data_dir / "facts.json")
        self.facts: list[Fact] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.facts = [Fact(**f) for f in raw]
        except Exception as exc:
            logger.warning(
                "facts_load_failed",
                extra={"event": "facts_load_failed", "error": repr(exc)},
            )

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([f.as_dict() for f in self.facts], indent=2),
            encoding="utf-8",
        )

    def add(
        self,
        content: str,
        *,
        tags: list[str] | None = None,
        source: str = "user",
        importance: int = 3,
    ) -> Fact:
        fact = Fact(
            id=uuid.uuid4().hex[:10],
            content=content.strip(),
            tags=tags or [],
            source=source,
            importance=max(1, min(5, importance)),
        )
        self.facts.append(fact)
        self._persist()
        log_event(
            logger,
            "fact.add",
            fact_id=fact.id,
            importance=fact.importance,
            tags=fact.tags,
            source=fact.source,
        )
        return fact

    def all(self) -> list[Fact]:
        return list(self.facts)

    def delete(self, fact_id: str) -> bool:
        before = len(self.facts)
        self.facts = [f for f in self.facts if f.id != fact_id]
        changed = len(self.facts) != before
        if changed:
            self._persist()
            log_event(logger, "fact.delete", fact_id=fact_id)
        return changed

    def search(self, query: str, *, k: int = 5) -> list[tuple[Fact, float]]:
        """Return the ``k`` most-similar facts to ``query``.

        Uses TF-style cosine similarity on token overlap. Good enough for
        a small personal knowledge base; easy to swap for a real embedder.
        """

        q_tokens = Counter(_tokenize(query))
        if not q_tokens:
            return []
        q_norm = math.sqrt(sum(v * v for v in q_tokens.values()))
        scored: list[tuple[Fact, float]] = []
        for f in self.facts:
            tokens = Counter(_tokenize(f.content + " " + " ".join(f.tags)))
            if not tokens:
                continue
            dot = sum(q_tokens[t] * tokens[t] for t in q_tokens)
            if dot == 0:
                continue
            norm = math.sqrt(sum(v * v for v in tokens.values())) * q_norm
            score = dot / norm if norm else 0.0
            # tilt toward important facts so key notes surface first
            score *= 0.7 + 0.3 * (f.importance / 5)
            scored.append((f, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]
