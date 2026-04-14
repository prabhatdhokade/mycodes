"""Tests for MCP context providers."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from optima_ai.mcp_providers.base import MCPContext, MCPProviderRegistry
from optima_ai.mcp_providers.filesystem import FileSystemProvider


class TestMCPContext:
    def test_to_prompt_block_with_metadata(self):
        ctx = MCPContext(
            provider_name="test",
            resource_type="file",
            content="print('hello')",
            metadata={"path": "/app.py", "language": "python"},
        )
        block = ctx.to_prompt_block()
        assert "[test:file]" in block
        assert "path=/app.py" in block
        assert "print('hello')" in block

    def test_to_prompt_block_without_metadata(self):
        ctx = MCPContext(
            provider_name="github",
            resource_type="pr",
            content="PR description",
        )
        block = ctx.to_prompt_block()
        assert "[github:pr]" in block
        assert "PR description" in block


class TestMCPProviderRegistry:
    def test_available_providers(self):
        providers = MCPProviderRegistry.available_providers()
        assert "filesystem" in providers
        assert "database" in providers
        assert "github" in providers
        assert "atlassian" in providers
        assert "datahub" in providers


class TestFileSystemProvider:
    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "main.py").write_text("def hello(): return 'world'")
            (Path(tmpdir) / "utils.py").write_text("import os\nPATH = os.getcwd()")
            sub = Path(tmpdir) / "src"
            sub.mkdir()
            (sub / "app.py").write_text("class App: pass")
            (Path(tmpdir) / "data.csv").write_text("a,b,c")  # unsupported ext
            yield tmpdir

    @pytest.mark.asyncio
    async def test_connect_and_list_resources(self, temp_project):
        provider = FileSystemProvider({"root_path": temp_project})
        await provider.connect()
        assert provider.is_connected

        resources = await provider.list_resources()
        paths = [r["path"] for r in resources]
        assert "main.py" in paths
        assert "utils.py" in paths
        assert "src/app.py" in paths
        assert "data.csv" not in paths  # unsupported extension

        await provider.disconnect()
        assert not provider.is_connected

    @pytest.mark.asyncio
    async def test_fetch_single_file(self, temp_project):
        provider = FileSystemProvider({"root_path": temp_project})
        await provider.connect()

        contexts = await provider.fetch_context("main.py")
        assert len(contexts) == 1
        assert "def hello()" in contexts[0].content
        assert contexts[0].metadata["language"] == "py"

    @pytest.mark.asyncio
    async def test_fetch_directory(self, temp_project):
        provider = FileSystemProvider({"root_path": temp_project})
        await provider.connect()

        contexts = await provider.fetch_context("src")
        assert len(contexts) >= 1
        assert any("class App" in c.content for c in contexts)

    @pytest.mark.asyncio
    async def test_glob_search(self, temp_project):
        provider = FileSystemProvider({"root_path": temp_project})
        await provider.connect()

        contexts = await provider.fetch_context("*.py")
        assert len(contexts) >= 2
