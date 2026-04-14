"""Base classes and registry for MCP context providers.

Every provider inherits from MCPProvider and registers itself via
MCPProviderRegistry so the agent layer can discover providers at runtime
based on dynamic per-session configuration.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any

from optima_ai.core.exceptions import ProviderNotFoundError
from optima_ai.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MCPContext:
    """Structured context returned by a provider — fed into the agent prompt."""

    provider_name: str
    resource_type: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 1.0

    def to_prompt_block(self) -> str:
        header = f"[{self.provider_name}:{self.resource_type}]"
        meta = " | ".join(f"{k}={v}" for k, v in self.metadata.items()) if self.metadata else ""
        return f"{header} {meta}\n{self.content}"


class MCPProvider(abc.ABC):
    """Abstract base for all MCP context providers."""

    name: str = "base"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._connected = False

    async def connect(self) -> None:
        logger.info("mcp_provider.connect", provider=self.name)
        await self._do_connect()
        self._connected = True

    async def disconnect(self) -> None:
        logger.info("mcp_provider.disconnect", provider=self.name)
        await self._do_disconnect()
        self._connected = False

    @abc.abstractmethod
    async def _do_connect(self) -> None: ...

    @abc.abstractmethod
    async def _do_disconnect(self) -> None: ...

    @abc.abstractmethod
    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]: ...

    @abc.abstractmethod
    async def list_resources(self) -> list[dict[str, Any]]: ...

    @property
    def is_connected(self) -> bool:
        return self._connected


class MCPProviderRegistry:
    """Singleton registry that maps provider names to provider instances.

    Supports dynamic reconfiguration per-session: providers can be added
    or swapped at runtime based on client-supplied MCP config.
    """

    _providers: dict[str, type[MCPProvider]] = {}
    _instances: dict[str, MCPProvider] = {}

    @classmethod
    def register(cls, provider_cls: type[MCPProvider]) -> type[MCPProvider]:
        cls._providers[provider_cls.name] = provider_cls
        return provider_cls

    @classmethod
    async def get_or_create(
        cls, name: str, config: dict[str, Any] | None = None
    ) -> MCPProvider:
        if name in cls._instances and cls._instances[name].is_connected:
            return cls._instances[name]

        if name not in cls._providers:
            raise ProviderNotFoundError(name)

        instance = cls._providers[name](config)
        await instance.connect()
        cls._instances[name] = instance
        return instance

    @classmethod
    async def configure_session(
        cls, provider_configs: dict[str, dict[str, Any]]
    ) -> dict[str, MCPProvider]:
        """Spin up a set of providers from a dynamic per-session config map."""
        active: dict[str, MCPProvider] = {}
        for name, cfg in provider_configs.items():
            active[name] = await cls.get_or_create(name, cfg)
        return active

    @classmethod
    async def shutdown_all(cls) -> None:
        for inst in cls._instances.values():
            if inst.is_connected:
                await inst.disconnect()
        cls._instances.clear()

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())
