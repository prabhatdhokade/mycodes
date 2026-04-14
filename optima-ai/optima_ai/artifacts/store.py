"""Artifact persistence — in-memory store with pluggable backends.

In production this backs to PostgreSQL + S3; the in-memory implementation
enables local development and testing without external deps.
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any

from optima_ai.core.logging import get_logger

logger = get_logger(__name__)


class ArtifactStore:
    """In-memory artifact store with version history tracking."""

    def __init__(self):
        self._artifacts: dict[str, dict[str, Any]] = {}
        self._versions: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._session_index: dict[str, list[str]] = defaultdict(list)

    async def save(self, artifact: dict[str, Any]) -> str:
        artifact_id = artifact["id"]
        existing = self._artifacts.get(artifact_id)

        if existing:
            self._versions[artifact_id].append(copy.deepcopy(existing))

        self._artifacts[artifact_id] = artifact

        session_id = artifact.get("session_id", "default")
        if artifact_id not in self._session_index[session_id]:
            self._session_index[session_id].append(artifact_id)

        logger.info(
            "artifact_saved",
            artifact_id=artifact_id,
            version=len(self._versions[artifact_id]) + 1,
        )
        return artifact_id

    async def get(self, artifact_id: str) -> dict[str, Any] | None:
        return self._artifacts.get(artifact_id)

    async def get_version(self, artifact_id: str, version: int) -> dict[str, Any] | None:
        versions = self._versions.get(artifact_id, [])
        if version == len(versions) + 1:
            return self._artifacts.get(artifact_id)
        if 1 <= version <= len(versions):
            return versions[version - 1]
        return None

    async def get_version_count(self, artifact_id: str) -> int:
        return len(self._versions.get(artifact_id, [])) + (1 if artifact_id in self._artifacts else 0)

    async def list_by_session(self, session_id: str) -> list[dict[str, Any]]:
        ids = self._session_index.get(session_id, [])
        return [self._artifacts[aid] for aid in ids if aid in self._artifacts]

    async def delete(self, artifact_id: str) -> bool:
        if artifact_id not in self._artifacts:
            return False
        artifact = self._artifacts.pop(artifact_id)
        self._versions.pop(artifact_id, None)
        session_id = artifact.get("session_id", "default")
        if artifact_id in self._session_index[session_id]:
            self._session_index[session_id].remove(artifact_id)
        return True

    async def search(
        self,
        artifact_type: str | None = None,
        language: str | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        candidates = (
            await self.list_by_session(session_id)
            if session_id
            else list(self._artifacts.values())
        )
        for artifact in candidates:
            if artifact_type and artifact.get("artifact_type") != artifact_type:
                continue
            if language and artifact.get("language") != language:
                continue
            results.append(artifact)
            if len(results) >= limit:
                break
        return results
