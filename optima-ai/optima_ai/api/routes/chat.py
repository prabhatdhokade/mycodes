"""Chat routes — primary interface for agent interactions.

Supports both request/response and streaming modes.
Protocol negotiation is automatic based on request headers.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from optima_ai.agents.base import AgentConfig, AgentRole
from optima_ai.agents.code_assistant import CodeAssistantAgent
from optima_ai.agents.orchestrator import AgentOrchestrator
from optima_ai.api.middleware.auth import get_current_user, optional_user
from optima_ai.core.logging import get_logger
from optima_ai.mcp_providers.base import MCPProviderRegistry
from optima_ai.services.auth import TokenPayload
from optima_ai.services.mcp_config import MCPConfigService, SessionMCPConfig
from optima_ai.streaming.manager import StreamManager

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

_orchestrator = AgentOrchestrator()
_stream_manager = StreamManager()
_mcp_config_service = MCPConfigService()


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    role: AgentRole | None = None
    conversation: list[dict[str, Any]] = Field(default_factory=list)
    mcp_config: SessionMCPConfig | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    id: str
    content: str
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    mcp_contexts_used: list[str] = Field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = Field(default_factory=dict)
    latency_ms: float = 0


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    request: Request,
    user: TokenPayload | None = Depends(optional_user),
):
    """Non-streaming chat endpoint."""
    user_id = user.sub if user else "anonymous"

    provider_configs = _mcp_config_service.resolve_config(user_id, req.mcp_config)
    providers = await MCPProviderRegistry.configure_session(provider_configs)

    config = AgentConfig(
        role=req.role or AgentRole.CODE_ASSISTANT,
        mcp_providers=providers,
    )
    agent = CodeAssistantAgent(config)

    response = await agent.run(req.message, req.conversation or None)

    return ChatResponse(
        id=response.id,
        content=response.content,
        artifacts=[
            {
                "id": a.id,
                "type": a.artifact_type,
                "title": a.title,
                "language": a.language,
                "content": a.content,
            }
            for a in response.artifacts
        ],
        mcp_contexts_used=response.mcp_contexts_used,
        model=response.model,
        usage=response.usage,
        latency_ms=response.latency_ms,
    )


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    request: Request,
    user: TokenPayload | None = Depends(optional_user),
):
    """Streaming chat endpoint — protocol auto-negotiated from headers."""
    user_id = user.sub if user else "anonymous"

    provider_configs = _mcp_config_service.resolve_config(user_id, req.mcp_config)
    providers = await MCPProviderRegistry.configure_session(provider_configs)

    config = AgentConfig(
        role=req.role or AgentRole.CODE_ASSISTANT,
        mcp_providers=providers,
    )
    agent = CodeAssistantAgent(config)

    return await _stream_manager.create_streaming_response(
        agent=agent,
        user_message=req.message,
        request=request,
        conversation=req.conversation or None,
    )
