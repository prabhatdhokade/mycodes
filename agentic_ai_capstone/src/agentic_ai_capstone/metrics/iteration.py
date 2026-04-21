"""Iteration and merge metrics capture."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IterationTracker:
    """Track message-level iterations and merge timing."""

    started_at: str = field(default_factory=_utc_iso)
    iterations: int = 0
    successful_iterations: int = 0
    failed_iterations: int = 0
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def start_iteration(self) -> None:
        self.iterations += 1
        self.checkpoints.append(
            {"event": "iteration_started", "iteration": self.iterations, "timestamp": _utc_iso()}
        )

    def complete_iteration(self, success: bool) -> None:
        if success:
            self.successful_iterations += 1
            event = "iteration_succeeded"
        else:
            self.failed_iterations += 1
            event = "iteration_failed"
        self.checkpoints.append(
            {"event": event, "iteration": self.iterations, "timestamp": _utc_iso()}
        )

    def mark(self, label: str, detail: str = "") -> None:
        self.checkpoints.append(
            {
                "event": label,
                "detail": detail,
                "iteration": self.iterations,
                "timestamp": _utc_iso(),
            }
        )

    def time_to_merge_seconds(self) -> float:
        started = datetime.fromisoformat(self.started_at)
        return (datetime.now(timezone.utc) - started).total_seconds()

    def summary(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "iterations": self.iterations,
            "successful_iterations": self.successful_iterations,
            "failed_iterations": self.failed_iterations,
            "time_to_merge_seconds": round(self.time_to_merge_seconds(), 3),
            "checkpoints": list(self.checkpoints),
        }
