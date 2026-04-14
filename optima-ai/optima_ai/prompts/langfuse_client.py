"""Langfuse integration for prompt versioning, evaluation tracking, and observability.

Provides:
  - Prompt template CRUD backed by Langfuse's prompt management API
  - Cached prompt retrieval to minimize API calls
  - Trace/span creation for generation tracking and evaluation
  - Generation scoring for continuous improvement feedback loops
"""

from __future__ import annotations

import hashlib
from typing import Any

from optima_ai.core.config import get_settings
from optima_ai.core.logging import get_logger
from optima_ai.services.cache import CacheService

logger = get_logger(__name__)


class LangfusePromptClient:
    """Wrapper around the Langfuse SDK for prompt management with caching."""

    def __init__(self, cache: CacheService | None = None):
        self.settings = get_settings().langfuse
        self.cache = cache
        self._client = None

    async def connect(self) -> None:
        if not self.settings.enabled or not self.settings.public_key:
            logger.warning("langfuse_disabled", reason="missing credentials or disabled")
            return

        from langfuse import Langfuse

        self._client = Langfuse(
            public_key=self.settings.public_key,
            secret_key=self.settings.secret_key,
            host=self.settings.host,
        )
        logger.info("langfuse_connected", host=self.settings.host)

    async def disconnect(self) -> None:
        if self._client:
            self._client.flush()
            self._client.shutdown()
            self._client = None

    async def get_prompt(
        self,
        name: str,
        version: int | None = None,
        label: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> str:
        """Fetch a prompt template from Langfuse with caching.

        Cache key includes name + version/label for reproducibility.
        """
        cache_key = f"prompt:{name}:{version or 'latest'}:{label or 'none'}"

        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug("prompt_cache_hit", name=name)
                template = cached
                if variables:
                    return self._render(template, variables)
                return template

        if not self._client:
            raise RuntimeError("Langfuse client not connected")

        kwargs: dict[str, Any] = {}
        if version is not None:
            kwargs["version"] = version
        if label:
            kwargs["label"] = label

        prompt_obj = self._client.get_prompt(name, **kwargs)
        template = prompt_obj.prompt

        if self.cache:
            await self.cache.set(cache_key, template, ttl=self.settings.cache_ttl_seconds)

        if variables:
            return self._render(template, variables)
        return template

    async def create_prompt(
        self,
        name: str,
        prompt: str,
        labels: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create or update a prompt in Langfuse."""
        if not self._client:
            raise RuntimeError("Langfuse client not connected")

        result = self._client.create_prompt(
            name=name,
            prompt=prompt,
            labels=labels or [],
            config=config or {},
        )

        if self.cache:
            await self.cache.invalidate_pattern(f"prompt:{name}:*")

        return {"name": name, "version": getattr(result, "version", 0)}

    async def create_trace(
        self,
        name: str,
        input_data: dict[str, Any],
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Create a Langfuse trace for generation tracking."""
        if not self._client:
            return None

        trace = self._client.trace(
            name=name,
            input=input_data,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
        )
        return trace

    async def create_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_messages: list[dict],
        output: str,
        usage: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Log a generation event (Claude API call) under a trace."""
        if not self._client:
            return None

        generation = self._client.generation(
            trace_id=trace_id,
            name=name,
            model=model,
            input=input_messages,
            output=output,
            usage=usage,
            metadata=metadata or {},
        )
        return generation

    async def score_generation(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: str = "",
    ) -> None:
        """Score a generation for evaluation and continuous improvement."""
        if not self._client:
            return

        self._client.score(
            trace_id=trace_id,
            name=name,
            value=value,
            comment=comment,
        )

    @staticmethod
    def _render(template: str, variables: dict[str, str]) -> str:
        """Render a Langfuse prompt template with double-brace variable substitution."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result
