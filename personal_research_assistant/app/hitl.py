"""Human-in-the-loop approval gate."""

from __future__ import annotations

from typing import Protocol


class ApprovalProvider(Protocol):
    """Abstraction for approval checks."""

    def approve(self, prompt: str) -> bool:
        """Return True if approved."""


class ConsoleApprovalProvider:
    """Interactive approval provider for CLI usage."""

    def approve(self, prompt: str) -> bool:
        while True:
            answer = input(f"{prompt} [y/n]: ").strip().lower()
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False
            print("Please answer with y/n.")


class StaticApprovalProvider:
    """Deterministic provider for tests and automation."""

    def __init__(self, approved: bool) -> None:
        self.approved = approved

    def approve(self, prompt: str) -> bool:
        _ = prompt
        return self.approved


class HITLGate:
    """Gateway wrapper to enforce approval for important saves."""

    def __init__(self, provider: ApprovalProvider) -> None:
        self.provider = provider

    def request_save_approval(self, note_text: str, importance: str = "normal") -> bool:
        prompt = (
            "Approve saving note?\n"
            f"importance={importance}\n"
            f"note={note_text}"
        )
        return self.provider.approve(prompt)
