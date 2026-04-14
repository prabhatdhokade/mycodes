"""Filesystem MCP provider — reads local/remote file trees for code context."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from optima_ai.mcp_providers.base import MCPContext, MCPProvider, MCPProviderRegistry


@MCPProviderRegistry.register
class FileSystemProvider(MCPProvider):
    name = "filesystem"

    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
        ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt",
        ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".sql",
        ".sh", ".bash", ".dockerfile", ".tf", ".hcl",
    }
    MAX_FILE_SIZE = 512 * 1024  # 512 KB

    async def _do_connect(self) -> None:
        self.root = Path(self.config.get("root_path", ".")).resolve()
        self.max_depth = self.config.get("max_depth", 5)
        self.ignore_patterns = set(self.config.get("ignore_patterns", [
            "__pycache__", "node_modules", ".git", ".venv", "dist", "build",
        ]))

    async def _do_disconnect(self) -> None:
        pass

    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]:
        """Search files matching the query path or pattern and return their contents."""
        target = self.root / query if not Path(query).is_absolute() else Path(query)
        results: list[MCPContext] = []

        if target.is_file():
            ctx = await self._read_file(target)
            if ctx:
                results.append(ctx)
        elif target.is_dir():
            results.extend(await self._scan_directory(target, max_files=kwargs.get("max_files", 20)))
        else:
            results.extend(await self._glob_search(query, max_files=kwargs.get("max_files", 20)))

        return results

    async def list_resources(self) -> list[dict[str, Any]]:
        resources: list[dict[str, Any]] = []
        for item in self.root.rglob("*"):
            if item.is_file() and self._should_include(item):
                resources.append({
                    "path": str(item.relative_to(self.root)),
                    "size": item.stat().st_size,
                    "extension": item.suffix,
                })
                if len(resources) >= 500:
                    break
        return resources

    async def _read_file(self, path: Path) -> MCPContext | None:
        if not self._should_include(path):
            return None
        try:
            content = path.read_text(errors="replace")
            if len(content.encode()) > self.MAX_FILE_SIZE:
                content = content[: self.MAX_FILE_SIZE // 2] + "\n... [truncated] ..."
            return MCPContext(
                provider_name=self.name,
                resource_type="file",
                content=content,
                metadata={
                    "path": str(path),
                    "language": path.suffix.lstrip("."),
                    "size": path.stat().st_size,
                },
            )
        except (OSError, UnicodeDecodeError):
            return None

    async def _scan_directory(self, directory: Path, max_files: int = 20) -> list[MCPContext]:
        results: list[MCPContext] = []
        for item in sorted(directory.rglob("*")):
            if item.is_file() and self._should_include(item):
                ctx = await self._read_file(item)
                if ctx:
                    results.append(ctx)
                if len(results) >= max_files:
                    break
        return results

    async def _glob_search(self, pattern: str, max_files: int = 20) -> list[MCPContext]:
        results: list[MCPContext] = []
        for item in sorted(self.root.glob(f"**/{pattern}")):
            if item.is_file() and self._should_include(item):
                ctx = await self._read_file(item)
                if ctx:
                    results.append(ctx)
                if len(results) >= max_files:
                    break
        return results

    def _should_include(self, path: Path) -> bool:
        if path.suffix not in self.SUPPORTED_EXTENSIONS:
            return False
        for part in path.parts:
            if part in self.ignore_patterns:
                return False
        return True
