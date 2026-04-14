"""MCP (Model Context Protocol) context providers.

Each provider implements a unified interface to fetch contextual data
from external systems — filesystem, databases, GitHub, Atlassian, Datahub —
and expose it as structured context for the Claude Agent SDK tool loop.
"""

from optima_ai.mcp_providers.base import MCPProvider, MCPProviderRegistry
from optima_ai.mcp_providers.filesystem import FileSystemProvider
from optima_ai.mcp_providers.database import DatabaseProvider
from optima_ai.mcp_providers.github import GitHubProvider
from optima_ai.mcp_providers.atlassian import AtlassianProvider
from optima_ai.mcp_providers.datahub import DatahubProvider

__all__ = [
    "MCPProvider",
    "MCPProviderRegistry",
    "FileSystemProvider",
    "DatabaseProvider",
    "GitHubProvider",
    "AtlassianProvider",
    "DatahubProvider",
]
