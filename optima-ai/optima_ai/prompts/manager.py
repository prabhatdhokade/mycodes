"""Prompt manager — local prompt registry with Langfuse sync.

Maintains a local prompt library (versioned, searchable) and optionally
syncs with Langfuse for centralized management. Supports:
  - Named prompt templates with variable substitution
  - Version history with rollback
  - Prompt evaluation metadata (scores, feedback)
  - Cache-through reads for low-latency prompt resolution
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from optima_ai.core.exceptions import PromptNotFoundError
from optima_ai.core.logging import get_logger
from optima_ai.prompts.langfuse_client import LangfusePromptClient
from optima_ai.services.cache import CacheService

logger = get_logger(__name__)


class PromptRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    template: str
    version: int = 1
    labels: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    content_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def render(self, variables: dict[str, str]) -> str:
        result = self.template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result


class PromptManager:
    """Manages prompt lifecycle with local store + optional Langfuse sync."""

    def __init__(
        self,
        langfuse_client: LangfusePromptClient | None = None,
        cache: CacheService | None = None,
    ):
        self.langfuse = langfuse_client
        self.cache = cache
        self._prompts: dict[str, list[PromptRecord]] = {}

    async def create(
        self,
        name: str,
        template: str,
        labels: list[str] | None = None,
        config: dict[str, Any] | None = None,
        sync_to_langfuse: bool = True,
    ) -> PromptRecord:
        """Create a new prompt or a new version of an existing prompt."""
        import re

        variables = re.findall(r"\{\{(\w+)\}\}", template)
        content_hash = hashlib.sha256(template.encode()).hexdigest()[:16]

        existing_versions = self._prompts.get(name, [])
        version = len(existing_versions) + 1

        record = PromptRecord(
            name=name,
            template=template,
            version=version,
            labels=labels or [],
            variables=variables,
            config=config or {},
            content_hash=content_hash,
        )

        if name not in self._prompts:
            self._prompts[name] = []
        self._prompts[name].append(record)

        if self.cache:
            await self.cache.set(f"prompt:{name}:latest", record.model_dump(mode="json"))
            await self.cache.set(
                f"prompt:{name}:v{version}", record.model_dump(mode="json")
            )

        if sync_to_langfuse and self.langfuse:
            try:
                await self.langfuse.create_prompt(name, template, labels, config)
            except Exception as exc:
                logger.warning("langfuse_sync_failed", name=name, error=str(exc))

        logger.info("prompt_created", name=name, version=version)
        return record

    async def get(
        self,
        name: str,
        version: int | None = None,
    ) -> PromptRecord:
        """Get a prompt by name and optional version. Uses cache-through pattern."""
        cache_key = f"prompt:{name}:{'v' + str(version) if version else 'latest'}"

        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return PromptRecord(**cached)

        versions = self._prompts.get(name)
        if not versions:
            raise PromptNotFoundError(name, str(version) if version else None)

        if version:
            if version < 1 or version > len(versions):
                raise PromptNotFoundError(name, str(version))
            record = versions[version - 1]
        else:
            record = versions[-1]

        if self.cache:
            await self.cache.set(cache_key, record.model_dump(mode="json"))

        return record

    async def render(
        self,
        name: str,
        variables: dict[str, str],
        version: int | None = None,
    ) -> str:
        """Resolve and render a prompt template with variables."""
        record = await self.get(name, version)
        return record.render(variables)

    async def list_prompts(self) -> list[dict[str, Any]]:
        """List all prompts with their latest version info."""
        results = []
        for name, versions in self._prompts.items():
            latest = versions[-1]
            results.append({
                "name": name,
                "latest_version": latest.version,
                "labels": latest.labels,
                "variables": latest.variables,
                "total_versions": len(versions),
                "updated_at": latest.updated_at.isoformat(),
            })
        return results

    async def get_version_history(self, name: str) -> list[PromptRecord]:
        versions = self._prompts.get(name)
        if not versions:
            raise PromptNotFoundError(name)
        return list(versions)

    async def delete(self, name: str) -> bool:
        if name not in self._prompts:
            return False
        del self._prompts[name]
        if self.cache:
            await self.cache.invalidate_pattern(f"prompt:{name}:*")
        return True
