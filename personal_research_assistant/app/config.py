"""Runtime configuration for the Personal Research Assistant.

Loads values from environment variables (and optionally a .env file) and
exposes a single ``Settings`` object the rest of the app imports from.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Application settings, loaded once at import time."""

    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))

    log_level: str = field(default_factory=lambda: os.getenv("PRA_LOG_LEVEL", "INFO"))
    log_file: str = field(
        default_factory=lambda: os.getenv(
            "PRA_LOG_FILE", "personal_research_assistant/data/agent.log"
        )
    )
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("PRA_DATA_DIR", "personal_research_assistant/data")
        )
    )

    max_react_steps: int = field(default_factory=lambda: int(os.getenv("PRA_MAX_STEPS", "6")))
    summarize_after_turns: int = field(
        default_factory=lambda: int(os.getenv("PRA_SUMMARIZE_AFTER", "10"))
    )

    auto_approve_notes: bool = field(
        default_factory=lambda: _bool(os.getenv("PRA_AUTO_APPROVE_NOTES"), False)
    )

    @property
    def use_real_llm(self) -> bool:
        return bool(self.openai_api_key)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
