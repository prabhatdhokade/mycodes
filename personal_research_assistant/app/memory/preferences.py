"""User preference store (key/value on disk)."""

from __future__ import annotations

import json
from pathlib import Path

from ..config import settings
from ..observability import get_logger, log_event

logger = get_logger("memory.preferences")


class PreferenceStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (settings.data_dir / "preferences.json")
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning(
                    "preferences_load_failed",
                    extra={"event": "preferences_load_failed", "error": repr(exc)},
                )

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        self._persist()
        log_event(logger, "preference.set", key=key)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def all(self) -> dict[str, str]:
        return dict(self._data)

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            self._persist()
            log_event(logger, "preference.delete", key=key)
            return True
        return False
