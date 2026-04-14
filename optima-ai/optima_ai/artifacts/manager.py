"""Artifact manager — tracks, versions, and manages generative UI outputs.

Artifacts include:
  - Code snippets and full file generations
  - Test cases (unit, integration, e2e)
  - Structured data (JSON schemas, API specs)
  - Documentation blocks
  - Diagrams and visual assets (as structured descriptions)

Each artifact is versioned — re-generations create new versions, enabling
diff views and rollback in the frontend.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from optima_ai.artifacts.store import ArtifactStore
from optima_ai.core.exceptions import ArtifactNotFoundError
from optima_ai.core.logging import get_logger

logger = get_logger(__name__)


class ArtifactType(str, Enum):
    CODE = "code"
    TEST = "test"
    DOCUMENT = "document"
    STRUCTURED_DATA = "structured_data"
    API_SPEC = "api_spec"
    DIAGRAM = "diagram"
    CONFIG = "config"


class ArtifactRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    artifact_type: ArtifactType = ArtifactType.CODE
    title: str = ""
    content: str = ""
    language: str = ""
    content_hash: str = ""
    version: int = 1
    parent_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactManager:
    """High-level artifact lifecycle management."""

    def __init__(self, store: ArtifactStore | None = None):
        self.store = store or ArtifactStore()

    async def create(
        self,
        session_id: str,
        artifact_type: ArtifactType,
        title: str,
        content: str,
        language: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        record = ArtifactRecord(
            session_id=session_id,
            artifact_type=artifact_type,
            title=title,
            content=content,
            language=language,
            content_hash=self._hash_content(content),
            metadata=metadata or {},
        )
        await self.store.save(record.model_dump(mode="json"))
        logger.info("artifact_created", id=record.id, type=artifact_type.value)
        return record

    async def update(
        self,
        artifact_id: str,
        content: str,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        existing = await self.store.get(artifact_id)
        if not existing:
            raise ArtifactNotFoundError(artifact_id)

        new_hash = self._hash_content(content)
        if new_hash == existing.get("content_hash"):
            return ArtifactRecord(**existing)

        version_count = await self.store.get_version_count(artifact_id)
        updated = {
            **existing,
            "content": content,
            "content_hash": new_hash,
            "version": version_count + 1,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if title:
            updated["title"] = title
        if metadata:
            updated["metadata"] = {**existing.get("metadata", {}), **metadata}

        await self.store.save(updated)
        logger.info("artifact_updated", id=artifact_id, version=updated["version"])
        return ArtifactRecord(**updated)

    async def get(self, artifact_id: str) -> ArtifactRecord:
        data = await self.store.get(artifact_id)
        if not data:
            raise ArtifactNotFoundError(artifact_id)
        return ArtifactRecord(**data)

    async def get_version(self, artifact_id: str, version: int) -> ArtifactRecord:
        data = await self.store.get_version(artifact_id, version)
        if not data:
            raise ArtifactNotFoundError(f"{artifact_id}@v{version}")
        return ArtifactRecord(**data)

    async def list_session_artifacts(
        self,
        session_id: str,
        artifact_type: ArtifactType | None = None,
    ) -> list[ArtifactRecord]:
        results = await self.store.search(
            artifact_type=artifact_type.value if artifact_type else None,
            session_id=session_id,
        )
        return [ArtifactRecord(**r) for r in results]

    async def diff(self, artifact_id: str, version_a: int, version_b: int) -> dict[str, Any]:
        """Compute a diff between two versions of an artifact."""
        a = await self.get_version(artifact_id, version_a)
        b = await self.get_version(artifact_id, version_b)

        import difflib

        diff_lines = list(
            difflib.unified_diff(
                a.content.splitlines(keepends=True),
                b.content.splitlines(keepends=True),
                fromfile=f"v{version_a}",
                tofile=f"v{version_b}",
            )
        )
        return {
            "artifact_id": artifact_id,
            "from_version": version_a,
            "to_version": version_b,
            "diff": "".join(diff_lines),
            "lines_added": sum(1 for l in diff_lines if l.startswith("+")),
            "lines_removed": sum(1 for l in diff_lines if l.startswith("-")),
        }

    async def delete(self, artifact_id: str) -> bool:
        return await self.store.delete(artifact_id)

    @staticmethod
    def _hash_content(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]
