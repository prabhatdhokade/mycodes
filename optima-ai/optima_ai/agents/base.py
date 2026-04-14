"""Base agent built on the Claude Agent SDK with MCP context injection.

The agent loop follows the Claude Agent SDK pattern:
  1. Gather MCP context from configured providers
  2. Build a system prompt enriched with contextual grounding
  3. Execute the Claude tool-use loop (message → tool calls → results → repeat)
  4. Collect artifacts produced during generation
  5. Return a structured AgentResponse with content + artifacts + metadata
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator

import anthropic

from optima_ai.core.config import get_settings
from optima_ai.core.exceptions import AgentExecutionError
from optima_ai.core.logging import get_logger
from optima_ai.mcp_providers.base import MCPContext, MCPProvider

logger = get_logger(__name__)


class AgentRole(str, Enum):
    CODE_ASSISTANT = "code_assistant"
    CODE_REVIEWER = "code_reviewer"
    TEST_GENERATOR = "test_generator"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentConfig:
    role: AgentRole = AgentRole.CODE_ASSISTANT
    model: str = ""
    max_tokens: int = 0
    temperature: float = 0.0
    system_prompt: str = ""
    tools: list[dict[str, Any]] = field(default_factory=list)
    mcp_providers: dict[str, MCPProvider] = field(default_factory=dict)
    max_turns: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        settings = get_settings()
        if not self.model:
            self.model = settings.anthropic.default_model
        if not self.max_tokens:
            self.max_tokens = settings.anthropic.max_tokens


@dataclass
class Artifact:
    id: str
    artifact_type: str  # code, test, document, structured_data
    title: str
    content: str
    language: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    id: str
    content: str
    artifacts: list[Artifact] = field(default_factory=list)
    mcp_contexts_used: list[str] = field(default_factory=list)
    tool_calls_made: int = 0
    turns_used: int = 0
    model: str = ""
    latency_ms: float = 0
    usage: dict[str, int] = field(default_factory=dict)


class BaseAgent:
    """Claude Agent SDK wrapper with MCP context injection and artifact extraction."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = str(uuid.uuid4())
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic.api_key)

    async def gather_context(self, user_message: str) -> list[MCPContext]:
        """Fetch context from all configured MCP providers in parallel."""
        import asyncio

        contexts: list[MCPContext] = []
        tasks = []
        for name, provider in self.config.mcp_providers.items():
            tasks.append(self._safe_fetch(name, provider, user_message))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                contexts.extend(result)
            elif isinstance(result, Exception):
                logger.warning("mcp_context_fetch_failed", error=str(result))

        return contexts

    async def _safe_fetch(
        self, name: str, provider: MCPProvider, query: str
    ) -> list[MCPContext]:
        try:
            return await provider.fetch_context(query)
        except Exception as exc:
            logger.error("provider_fetch_error", provider=name, error=str(exc))
            return []

    def build_system_prompt(self, mcp_contexts: list[MCPContext]) -> str:
        """Build the full system prompt by injecting MCP context blocks."""
        base = self.config.system_prompt or self._default_system_prompt()

        if not mcp_contexts:
            return base

        context_section = "\n\n".join(ctx.to_prompt_block() for ctx in mcp_contexts)
        return (
            f"{base}\n\n"
            f"--- Grounding Context (from MCP providers) ---\n"
            f"{context_section}\n"
            f"--- End Grounding Context ---"
        )

    async def run(self, user_message: str, conversation: list[dict] | None = None) -> AgentResponse:
        """Execute the full agent loop: context → prompt → Claude → artifacts."""
        start = time.monotonic()
        response_id = str(uuid.uuid4())

        mcp_contexts = await self.gather_context(user_message)
        system_prompt = self.build_system_prompt(mcp_contexts)

        messages = list(conversation or [])
        messages.append({"role": "user", "content": user_message})

        total_usage = {"input_tokens": 0, "output_tokens": 0}
        tool_calls = 0
        turns = 0

        try:
            for turn in range(self.config.max_turns):
                turns = turn + 1

                kwargs: dict[str, Any] = {
                    "model": self.config.model,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "system": system_prompt,
                    "messages": messages,
                }
                if self.config.tools:
                    kwargs["tools"] = self.config.tools

                response = await self._client.messages.create(**kwargs)

                total_usage["input_tokens"] += response.usage.input_tokens
                total_usage["output_tokens"] += response.usage.output_tokens

                if response.stop_reason == "end_turn" or response.stop_reason != "tool_use":
                    final_text = self._extract_text(response)
                    artifacts = self._extract_artifacts(final_text)
                    break

                messages.append({"role": "assistant", "content": response.content})
                tool_results = await self._handle_tool_calls(response)
                tool_calls += len(tool_results)
                messages.append({"role": "user", "content": tool_results})
            else:
                final_text = "Agent reached maximum turn limit."
                artifacts = []

        except anthropic.APIError as exc:
            raise AgentExecutionError(f"Claude API error: {exc}") from exc

        elapsed_ms = (time.monotonic() - start) * 1000

        return AgentResponse(
            id=response_id,
            content=final_text,
            artifacts=artifacts,
            mcp_contexts_used=[c.provider_name for c in mcp_contexts],
            tool_calls_made=tool_calls,
            turns_used=turns,
            model=self.config.model,
            latency_ms=elapsed_ms,
            usage=total_usage,
        )

    async def run_stream(
        self, user_message: str, conversation: list[dict] | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream the agent response token-by-token, yielding SSE-compatible dicts."""
        mcp_contexts = await self.gather_context(user_message)
        system_prompt = self.build_system_prompt(mcp_contexts)

        messages = list(conversation or [])
        messages.append({"role": "user", "content": user_message})

        yield {"type": "context", "providers": [c.provider_name for c in mcp_contexts]}

        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system_prompt,
            "messages": messages,
        }
        if self.config.tools:
            kwargs["tools"] = self.config.tools

        async with self._client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield {"type": "text_delta", "text": event.delta.text}
                    elif event.type == "message_stop":
                        yield {"type": "done"}

    async def _handle_tool_calls(self, response: anthropic.types.Message) -> list[dict]:
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = await self._execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        return tool_results

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Override in subclasses to implement custom tool execution."""
        return f"Tool '{tool_name}' not implemented"

    def _extract_text(self, response: anthropic.types.Message) -> str:
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts)

    def _extract_artifacts(self, text: str) -> list[Artifact]:
        """Parse artifact blocks from the agent's output text.

        Artifacts are delimited by markers like:
          ```artifact:code:python:title
          ...content...
          ```
        """
        import re

        artifacts = []
        pattern = r"```artifact:(\w+):(\w*):?(.*?)\n(.*?)```"
        for match in re.finditer(pattern, text, re.DOTALL):
            artifacts.append(
                Artifact(
                    id=str(uuid.uuid4()),
                    artifact_type=match.group(1),
                    language=match.group(2),
                    title=match.group(3).strip() or "Untitled",
                    content=match.group(4).strip(),
                )
            )
        return artifacts

    def _default_system_prompt(self) -> str:
        return (
            "You are an expert AI coding assistant. Provide clear, accurate, "
            "production-quality code and explanations. Use the grounding context "
            "provided to give contextually relevant answers."
        )
