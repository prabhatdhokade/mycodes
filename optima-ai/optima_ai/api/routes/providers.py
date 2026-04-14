"""MCP Provider management routes — configure and query connected providers."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from optima_ai.api.middleware.auth import optional_user
from optima_ai.mcp_providers.base import MCPProviderRegistry
from optima_ai.services.mcp_config import MCPConfigService, SessionMCPConfig

router = APIRouter(prefix="/providers", tags=["providers"])
_mcp_config_service = MCPConfigService()


@router.get("")
async def list_providers():
    """List all registered MCP providers."""
    return {"providers": MCPProviderRegistry.available_providers()}


@router.post("/configure")
async def configure_session(
    config: SessionMCPConfig,
    user: Any = Depends(optional_user),
):
    """Validate and preview a provider configuration."""
    errors = _mcp_config_service.validate_config(config)
    if errors:
        return {"valid": False, "errors": errors}

    user_id = user.sub if user else "anonymous"
    resolved = _mcp_config_service.resolve_config(user_id, config)
    return {
        "valid": True,
        "active_providers": list(resolved.keys()),
    }


@router.get("/{provider_name}/resources")
async def list_provider_resources(provider_name: str):
    """List resources available from a connected provider."""
    try:
        provider = await MCPProviderRegistry.get_or_create(provider_name)
        resources = await provider.list_resources()
        return {"provider": provider_name, "resources": resources}
    except Exception as exc:
        return {"provider": provider_name, "error": str(exc)}
