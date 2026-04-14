"""Agent layer — core agents built on the Claude Agent SDK, extended with MCP context."""

from optima_ai.agents.base import BaseAgent, AgentConfig, AgentResponse
from optima_ai.agents.code_assistant import CodeAssistantAgent
from optima_ai.agents.orchestrator import AgentOrchestrator

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    "CodeAssistantAgent",
    "AgentOrchestrator",
]
