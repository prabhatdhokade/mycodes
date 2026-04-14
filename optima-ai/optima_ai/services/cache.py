"""Redis caching service with typed get/set and namespace support.

Used for:
  - Prompt template caching (avoid repeated Langfuse lookups)
  - MCP context caching (reuse recent fetches across turns)
  - Session state caching
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from optima_ai.core.config import get_settings
from optima_ai.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Async Redis cache with namespace isolation and TTL management."""

    def __init__(self, namespace: str = "optima"):
        self.settings = get_settings()
        self.namespace = namespace
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._redis = aioredis.from_url(
            self.settings.redis.url,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        logger.info("redis_connected", url=self.settings.redis.host)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Any | None:
        if not self._redis:
            return None
        raw = await self._redis.get(self._key(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> None:
        if not self._redis:
            return
        ttl = ttl or self.settings.redis.ttl_seconds
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await self._redis.set(self._key(key), serialized, ex=ttl)

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        await self._redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        if not self._redis:
            return False
        return bool(await self._redis.exists(self._key(key)))

    async def get_or_set(
        self, key: str, factory, ttl: int | None = None
    ) -> Any:
        """Cache-aside pattern: return cached value or compute + cache."""
        cached = await self.get(key)
        if cached is not None:
            logger.debug("cache_hit", key=key)
            return cached

        logger.debug("cache_miss", key=key)
        value = await factory() if callable(factory) else factory
        await self.set(key, value, ttl)
        return value

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern within the namespace."""
        if not self._redis:
            return 0
        full_pattern = self._key(pattern)
        keys = []
        async for key in self._redis.scan_iter(match=full_pattern):
            keys.append(key)
        if keys:
            await self._redis.delete(*keys)
        return len(keys)

    async def health_check(self) -> bool:
        try:
            if self._redis:
                await self._redis.ping()
                return True
        except Exception:
            pass
        return False
