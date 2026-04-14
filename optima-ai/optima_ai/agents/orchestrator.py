"""Agent Orchestrator — routes requests to the right agent and manages multi-agent flows.

Handles:
  - Dynamic agent instantiation with per-session MCP provider configs
  - Routing based on task classification (code assist, review, test gen, etc.)
  - Multi-agent pipelines (e.g., generate code → review → test)
"""

from __future__ import annotations

import asyncio
from typing import Any

from optima_ai.agents.base import AgentConfig, AgentResponse, AgentRole, BaseAgent
from optima_ai.agents.code_assistant import CodeAssistantAgent
from optima_ai.core.logging import get_logger
from optima_ai.mcp_providers.base import MCPProvider, MCPProviderRegistry

logger = get_logger(__name__)

ROLE_SYSTEM_PROMPTS: dict[AgentRole, str] = {
    AgentRole.CODE_REVIEWER: (
        "You are an expert code reviewer. Analyze code for bugs, performance issues, "
        "security vulnerabilities, and adherence to best practices. Provide specific, "
        "actionable feedback with line-level suggestions."
    ),
    AgentRole.TEST_GENERATOR: (
        "You are a test generation expert. Write comprehensive test suites with edge "
        "cases, mocks, and assertions. Use the project's existing test framework."
    ),
    AgentRole.DOCUMENTATION: (
        "You are a technical documentation specialist. Write clear API docs, inline "
        "comments, and README sections based on the codebase context."
    ),
    AgentRole.DEBUGGING: (
        "You are a debugging expert. Analyze error traces, reproduce issues, identify "
        "root causes, and suggest targeted fixes with explanations."
    ),
}


class AgentOrchestrator:
    """Creates, routes, and orchestrates agents with dynamic MCP configurations."""

    def __init__(self):
        self._active_sessions: dict[str, dict[str, Any]] = {}

    async def create_session(
        self,
        session_id: str,
        provider_configs: dict[str, dict[str, Any]],
        default_role: AgentRole = AgentRole.CODE_ASSISTANT,
    ) -> dict[str, MCPProvider]:
        """Initialize a session: spin up MCP providers and prepare agent configs."""
        providers = await MCPProviderRegistry.configure_session(provider_configs)

        self._active_sessions[session_id] = {
            "providers": providers,
            "default_role": default_role,
            "conversation": [],
        }

        logger.info(
            "session_created",
            session_id=session_id,
            providers=list(providers.keys()),
        )
        return providers

    async def route_and_execute(
        self,
        session_id: str,
        user_message: str,
        role: AgentRole | None = None,
    ) -> AgentResponse:
        """Route the user's message to the appropriate agent and execute."""
        session = self._active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        effective_role = role or session["default_role"]
        if effective_role == AgentRole.CODE_ASSISTANT:
            effective_role = await self._classify_intent(user_message, effective_role)

        agent = self._build_agent(effective_role, session["providers"])

        response = await agent.run(user_message, session["conversation"])

        session["conversation"].append({"role": "user", "content": user_message})
        session["conversation"].append({"role": "assistant", "content": response.content})

        return response

    async def run_pipeline(
        self,
        session_id: str,
        user_message: str,
        pipeline: list[AgentRole],
    ) -> list[AgentResponse]:
        """Execute a multi-agent pipeline sequentially, feeding each output to the next."""
        session = self._active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        responses: list[AgentResponse] = []
        current_input = user_message

        for step_role in pipeline:
            agent = self._build_agent(step_role, session["providers"])
            response = await agent.run(current_input)
            responses.append(response)
            current_input = (
                f"Previous step ({step_role.value}) output:\n{response.content}\n\n"
                f"Original request:\n{user_message}"
            )

        return responses

    async def teardown_session(self, session_id: str) -> None:
        session = self._active_sessions.pop(session_id, None)
        if session:
            for provider in session["providers"].values():
                if provider.is_connected:
                    await provider.disconnect()
            logger.info("session_teardown", session_id=session_id)

    def _build_agent(
        self, role: AgentRole, providers: dict[str, MCPProvider]
    ) -> BaseAgent:
        if role == AgentRole.CODE_ASSISTANT:
            config = AgentConfig(role=role, mcp_providers=providers)
            return CodeAssistantAgent(config)

        system_prompt = ROLE_SYSTEM_PROMPTS.get(role, "")
        config = AgentConfig(
            role=role,
            system_prompt=system_prompt,
            mcp_providers=providers,
        )
        return BaseAgent(config)

    async def _classify_intent(
        self, message: str, default: AgentRole
    ) -> AgentRole:
        """Simple keyword-based intent classification. In production, this would
        use a lightweight classifier or Claude itself for routing."""
        lower = message.lower()
        if any(kw in lower for kw in ["review", "pr review", "code review"]):
            return AgentRole.CODE_REVIEWER
        if any(kw in lower for kw in ["test", "unit test", "write tests"]):
            return AgentRole.TEST_GENERATOR
        if any(kw in lower for kw in ["document", "readme", "docstring", "api doc"]):
            return AgentRole.DOCUMENTATION
        if any(kw in lower for kw in ["debug", "error", "traceback", "fix bug"]):
            return AgentRole.DEBUGGING
        return default
