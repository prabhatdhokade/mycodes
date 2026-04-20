"""Structured JSON logging with latency tracking.

Every log record is emitted as one JSON object per line so the logs can be
ingested by any observability backend (ELK, Loki, Datadog, etc.).  A
``timed`` context manager is provided for measuring the latency of LLM
calls and tool invocations.
"""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Iterator

from ..config import settings


class _JsonFormatter(logging.Formatter):
    """Format log records as compact JSON lines."""

    _RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "asctime", "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k in self._RESERVED or k.startswith("_"):
                continue
            try:
                json.dumps(v)
                payload[k] = v
            except TypeError:
                payload[k] = repr(v)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def _configure_root() -> None:
    """Wire up handlers on the ``pra`` logger, once per (pid, log_file)."""

    root = logging.getLogger("pra")
    root.setLevel(settings.log_level.upper())
    root.propagate = False

    existing_files = {
        getattr(h, "baseFilename", None)
        for h in root.handlers
        if isinstance(h, RotatingFileHandler)
    }
    has_stream = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
        for h in root.handlers
    )

    formatter = _JsonFormatter()

    if not has_stream:
        stream = logging.StreamHandler(stream=sys.stdout)
        stream.setFormatter(formatter)
        root.addHandler(stream)

    target = str(Path(settings.log_file).resolve())
    if target not in {str(Path(p).resolve()) if p else "" for p in existing_files}:
        try:
            file_handler = RotatingFileHandler(
                settings.log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except Exception as exc:
            root.warning("could_not_attach_file_handler", extra={"error": repr(exc)})


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger (e.g. ``pra.agent``)."""

    _configure_root()
    if not name.startswith("pra"):
        name = f"pra.{name}"
    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a structured event with arbitrary extra fields."""

    logger.info(event, extra={"event": event, **fields})


@contextmanager
def timed(logger: logging.Logger, event: str, **fields: Any) -> Iterator[dict[str, Any]]:
    """Context manager that logs a start/end pair with latency in ms.

    The caller can mutate the yielded dict to attach output-shape metadata
    (e.g. ``ctx["tokens"] = 123``) which will be included in the final
    event record.
    """

    trace_id = fields.pop("trace_id", None) or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    ctx: dict[str, Any] = {"trace_id": trace_id}
    logger.info(
        f"{event}.start",
        extra={"event": f"{event}.start", "trace_id": trace_id, **fields},
    )
    try:
        yield ctx
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            f"{event}.error",
            extra={
                "event": f"{event}.error",
                "trace_id": trace_id,
                "latency_ms": elapsed_ms,
                "error": repr(exc),
                **fields,
                **ctx,
            },
        )
        raise
    else:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"{event}.end",
            extra={
                "event": f"{event}.end",
                "trace_id": trace_id,
                "latency_ms": elapsed_ms,
                **fields,
                **ctx,
            },
        )
