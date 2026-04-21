"""Tracing and cost-tracking layer.

Provides a lightweight, dependency-free tracer that records every span
(LLM call, tool call, guardrail decision, routing decision). The tracer is
compatible with Langfuse/LangSmith conceptually - each span has a trace_id,
span_id, parent_id, name, inputs, outputs, latency and cost. A JSONL export
is produced so it can be shipped to any observability backend.
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterator, List, Optional


# Approximate per-1K-token pricing used for cost tracking. Kept conservative.
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
    "gpt-4o": {"input": 0.00500, "output": 0.01500},
    "gpt-3.5-turbo": {"input": 0.00050, "output": 0.00150},
    "mock": {"input": 0.0, "output": 0.0},
}


@dataclass
class Span:
    span_id: str
    trace_id: str
    name: str
    kind: str  # "llm" | "tool" | "agent" | "guardrail" | "router" | "hitl"
    parent_id: Optional[str] = None
    start_ts: float = 0.0
    end_ts: float = 0.0
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    tokens_in: int = 0
    tokens_out: int = 0
    model: Optional[str] = None
    cost_usd: float = 0.0
    status: str = "ok"
    error: Optional[str] = None

    @property
    def latency_ms(self) -> float:
        return round((self.end_ts - self.start_ts) * 1000, 2)


class Tracer:
    """Thread-safe in-memory tracer with JSONL export."""

    def __init__(self, export_path: Optional[str] = None):
        self._spans: List[Span] = []
        self._lock = threading.Lock()
        self._active: List[Span] = []
        self.export_path = export_path

    def new_trace_id(self) -> str:
        return f"trace_{uuid.uuid4().hex[:12]}"

    @contextmanager
    def span(
        self,
        name: str,
        kind: str,
        trace_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> Iterator[Span]:
        parent_id = self._active[-1].span_id if self._active else None
        span = Span(
            span_id=f"span_{uuid.uuid4().hex[:10]}",
            trace_id=trace_id,
            name=name,
            kind=kind,
            parent_id=parent_id,
            start_ts=time.time(),
            inputs=inputs or {},
            model=model,
        )
        self._active.append(span)
        try:
            yield span
            span.status = "ok"
        except Exception as e:  # pragma: no cover - defensive
            span.status = "error"
            span.error = f"{type(e).__name__}: {e}"
            raise
        finally:
            span.end_ts = time.time()
            # Compute cost if model is known and token counts are set
            if span.model and span.model in MODEL_PRICING:
                price = MODEL_PRICING[span.model]
                span.cost_usd = round(
                    (span.tokens_in / 1000.0) * price["input"]
                    + (span.tokens_out / 1000.0) * price["output"],
                    6,
                )
            self._active.pop()
            with self._lock:
                self._spans.append(span)
                if self.export_path:
                    self._append_jsonl(span)

    def _append_jsonl(self, span: Span) -> None:
        os.makedirs(os.path.dirname(self.export_path) or ".", exist_ok=True)
        with open(self.export_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(span), default=str) + "\n")

    def spans(self) -> List[Span]:
        with self._lock:
            return list(self._spans)

    def total_cost(self) -> float:
        return round(sum(s.cost_usd for s in self._spans), 6)

    def summary(self) -> Dict[str, Any]:
        by_kind: Dict[str, int] = {}
        for s in self._spans:
            by_kind[s.kind] = by_kind.get(s.kind, 0) + 1
        return {
            "total_spans": len(self._spans),
            "by_kind": by_kind,
            "total_cost_usd": self.total_cost(),
            "total_tokens_in": sum(s.tokens_in for s in self._spans),
            "total_tokens_out": sum(s.tokens_out for s in self._spans),
        }

    def reset(self) -> None:
        with self._lock:
            self._spans.clear()


_GLOBAL_TRACER: Optional[Tracer] = None


def get_tracer() -> Tracer:
    global _GLOBAL_TRACER
    if _GLOBAL_TRACER is None:
        export = os.environ.get("CSS_TRACE_FILE")
        _GLOBAL_TRACER = Tracer(export_path=export)
    return _GLOBAL_TRACER


def set_tracer(tracer: Tracer) -> None:
    global _GLOBAL_TRACER
    _GLOBAL_TRACER = tracer
