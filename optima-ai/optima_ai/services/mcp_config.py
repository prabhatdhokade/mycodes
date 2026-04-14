"""Dynamic MCP configuration service.

Manages per-user and per-session MCP provider configurations.
Configs can be stored in the database or passed inline with requests.
Supports validation, merging defaults, and secure token injection.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from optima_ai.core.logging import get_logger
from optima_ai.mcp_providers.base import MCPProviderRegistry

logger = get_logger(__name__)


class ProviderConfig(BaseModel):
    """Configuration for a single MCP provider instance."""

    name: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class SessionMCPConfig(BaseModel):
    """Full MCP configuration for a session — a list of provider configs."""

    providers: list[ProviderConfig] = Field(default_factory=list)


DEFAULT_PROVIDER_CONFIGS: dict[str, dict[str, Any]] = {
    "filesystem": {"root_path": ".", "max_depth": 5},
}


class MCPConfigService:
    """Resolves, validates, and applies MCP configurations for sessions."""

    def __init__(self):
        self._user_configs: dict[str, SessionMCPConfig] = {}

    def get_available_providers(self) -> list[str]:
        return MCPProviderRegistry.available_providers()

    def resolve_config(
        self,
        user_id: str,
        session_overrides: SessionMCPConfig | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Merge default configs → user configs → session overrides."""
        resolved: dict[str, dict[str, Any]] = dict(DEFAULT_PROVIDER_CONFIGS)

        user_cfg = self._user_configs.get(user_id)
        if user_cfg:
            for p in user_cfg.providers:
                if p.enabled:
                    resolved[p.name] = {**resolved.get(p.name, {}), **p.config}

        if session_overrides:
            for p in session_overrides.providers:
                if p.enabled:
                    resolved[p.name] = {**resolved.get(p.name, {}), **p.config}
                elif p.name in resolved:
                    del resolved[p.name]

        logger.info(
            "mcp_config_resolved",
            user_id=user_id,
            active_providers=list(resolved.keys()),
        )
        return resolved

    def save_user_config(self, user_id: str, config: SessionMCPConfig) -> None:
        self._user_configs[user_id] = config

    def get_user_config(self, user_id: str) -> SessionMCPConfig | None:
        return self._user_configs.get(user_id)

    def validate_config(self, config: SessionMCPConfig) -> list[str]:
        """Return a list of validation errors (empty = valid)."""
        errors: list[str] = []
        available = set(self.get_available_providers())
        for p in config.providers:
            if p.name not in available:
                errors.append(f"Unknown provider: '{p.name}'. Available: {sorted(available)}")
        return errors

    def inject_tokens(
        self,
        config: dict[str, dict[str, Any]],
        token_map: dict[str, str],
    ) -> dict[str, dict[str, Any]]:
        """Inject user-specific API tokens into provider configs securely.

        token_map maps provider names to their auth tokens, e.g.:
          {"github": "ghp_xxx", "atlassian": "xoxb-xxx"}
        """
        for provider_name, token in token_map.items():
            if provider_name in config:
                config[provider_name]["token"] = token
                config[provider_name]["api_token"] = token
        return config
