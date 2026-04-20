"""Structured observability utilities for agent events."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import time
from typing import Any

from .types import LogEvent, utc_now_iso


class StructuredLogger:
    """JSONL logger that records decisions, tools, and latency."""

    def __init__(self, log_dir: str) -> None:
        self.log_path = Path(log_dir) / "agent.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8")

    def log(self, event_type: str, trace_id: str, payload: dict[str, Any], latency_ms: float = 0.0) -> None:
        event = LogEvent(
            event_type=event_type,
            latency_ms=round(latency_ms, 3),
            payload=payload,
            timestamp=utc_now_iso(),
            trace_id=trace_id,
        )
        with self.log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(asdict(event), ensure_ascii=True) + "\n")

    def timed(self, event_type: str, trace_id: str) -> "_TimedEvent":
        return _TimedEvent(self, event_type=event_type, trace_id=trace_id)


class _TimedEvent:
    """Context manager for measuring and logging elapsed milliseconds."""

    def __init__(self, logger: StructuredLogger, event_type: str, trace_id: str) -> None:
        self.logger = logger
        self.event_type = event_type
        self.trace_id = trace_id
        self.payload: dict[str, Any] = {}
        self._start = 0.0

    def __enter__(self) -> "_TimedEvent":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, _tb) -> bool:
        elapsed_ms = (time.perf_counter() - self._start) * 1000.0
        payload = dict(self.payload)
        if exc is not None:
            payload["error"] = str(exc)
        self.logger.log(
            event_type=self.event_type,
            trace_id=self.trace_id,
            payload=payload,
            latency_ms=elapsed_ms,
        )
        return False
