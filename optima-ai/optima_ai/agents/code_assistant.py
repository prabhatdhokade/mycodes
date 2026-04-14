"""Code Assistant Agent — specialized for real-time developer assistance.

Extends BaseAgent with code-specific tools:
  - read_file / write_file / search_codebase (via FS MCP provider)
  - run_tests / lint_check (via shell execution)
  - fetch_documentation (via web search)

The agent uses structured artifact output for code blocks, test cases,
and documentation so the frontend can render them as generative UI.
"""

from __future__ import annotations

import json
from typing import Any

from optima_ai.agents.base import AgentConfig, AgentRole, BaseAgent
from optima_ai.core.logging import get_logger

logger = get_logger(__name__)

CODE_ASSISTANT_TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to project root"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_codebase",
        "description": "Search for files or code patterns in the codebase",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or file pattern"},
                "max_results": {"type": "integer", "description": "Maximum results to return", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at the given path",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path", "default": "."},
            },
        },
    },
    {
        "name": "fetch_context",
        "description": "Fetch additional context from a specific MCP provider (github, database, atlassian, datahub)",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {"type": "string", "description": "Provider name"},
                "query": {"type": "string", "description": "Context query for the provider"},
            },
            "required": ["provider", "query"],
        },
    },
]

SYSTEM_PROMPT = """\
You are Optima AI, an expert real-time code assistant. You help developers write, review, \
debug, and understand code with deep contextual awareness.

Capabilities:
- Read and analyze code files from the project
- Search the codebase for relevant patterns and definitions
- Fetch context from connected systems (GitHub PRs/issues, Jira tickets, databases, data catalogs)
- Generate code, tests, documentation, and structured outputs

Guidelines:
- Always ground your responses in the actual codebase when possible
- Produce production-quality code with proper error handling
- When generating code artifacts, use the artifact format for structured output
- Be concise but thorough in explanations
- Flag potential issues, edge cases, and security concerns proactively
"""


class CodeAssistantAgent(BaseAgent):
    """Production code assistant with file I/O and multi-provider context tools."""

    def __init__(self, config: AgentConfig | None = None):
        if config is None:
            config = AgentConfig(
                role=AgentRole.CODE_ASSISTANT,
                system_prompt=SYSTEM_PROMPT,
                tools=CODE_ASSISTANT_TOOLS,
            )
        else:
            if not config.system_prompt:
                config.system_prompt = SYSTEM_PROMPT
            if not config.tools:
                config.tools = CODE_ASSISTANT_TOOLS
        super().__init__(config)

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        logger.info("tool_execution", tool=tool_name, input_keys=list(tool_input.keys()))

        try:
            if tool_name == "read_file":
                return await self._tool_read_file(tool_input["path"])
            elif tool_name == "search_codebase":
                return await self._tool_search(tool_input["query"], tool_input.get("max_results", 10))
            elif tool_name == "list_directory":
                return await self._tool_list_dir(tool_input.get("path", "."))
            elif tool_name == "fetch_context":
                return await self._tool_fetch_context(tool_input["provider"], tool_input["query"])
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as exc:
            logger.error("tool_execution_error", tool=tool_name, error=str(exc))
            return f"Error executing {tool_name}: {exc}"

    async def _tool_read_file(self, path: str) -> str:
        fs_provider = self.config.mcp_providers.get("filesystem")
        if not fs_provider:
            return "Filesystem provider not configured"

        contexts = await fs_provider.fetch_context(path)
        if not contexts:
            return f"File not found or not readable: {path}"
        return contexts[0].content

    async def _tool_search(self, query: str, max_results: int) -> str:
        fs_provider = self.config.mcp_providers.get("filesystem")
        if not fs_provider:
            return "Filesystem provider not configured"

        contexts = await fs_provider.fetch_context(query, max_files=max_results)
        if not contexts:
            return f"No results found for: {query}"

        results = []
        for ctx in contexts:
            path = ctx.metadata.get("path", "unknown")
            preview = ctx.content[:200] + "..." if len(ctx.content) > 200 else ctx.content
            results.append(f"File: {path}\n{preview}")

        return "\n---\n".join(results)

    async def _tool_list_dir(self, path: str) -> str:
        fs_provider = self.config.mcp_providers.get("filesystem")
        if not fs_provider:
            return "Filesystem provider not configured"

        resources = await fs_provider.list_resources()
        return json.dumps(resources[:50], indent=2)

    async def _tool_fetch_context(self, provider_name: str, query: str) -> str:
        provider = self.config.mcp_providers.get(provider_name)
        if not provider:
            return f"Provider '{provider_name}' not configured for this session"

        contexts = await provider.fetch_context(query)
        return "\n\n".join(ctx.to_prompt_block() for ctx in contexts) or "No context returned"
