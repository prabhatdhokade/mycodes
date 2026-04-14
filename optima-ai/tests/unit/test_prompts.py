"""Tests for prompt management and versioning."""

from __future__ import annotations

import pytest

from optima_ai.core.exceptions import PromptNotFoundError
from optima_ai.prompts.manager import PromptManager


class TestPromptManager:
    @pytest.fixture
    def manager(self):
        return PromptManager()

    @pytest.mark.asyncio
    async def test_create_prompt(self, manager):
        record = await manager.create(
            name="code_review",
            template="Review this {{language}} code:\n{{code}}",
            labels=["production"],
            sync_to_langfuse=False,
        )
        assert record.name == "code_review"
        assert record.version == 1
        assert "language" in record.variables
        assert "code" in record.variables

    @pytest.mark.asyncio
    async def test_versioning(self, manager):
        await manager.create(
            name="greeting",
            template="Hello {{name}}!",
            sync_to_langfuse=False,
        )
        v2 = await manager.create(
            name="greeting",
            template="Hi {{name}}, welcome to {{app}}!",
            sync_to_langfuse=False,
        )
        assert v2.version == 2
        assert "app" in v2.variables

        v1 = await manager.get("greeting", version=1)
        assert v1.template == "Hello {{name}}!"

        latest = await manager.get("greeting")
        assert latest.version == 2

    @pytest.mark.asyncio
    async def test_render(self, manager):
        await manager.create(
            name="test_prompt",
            template="Fix this {{language}} bug:\n{{code}}",
            sync_to_langfuse=False,
        )
        rendered = await manager.render(
            "test_prompt",
            {"language": "Python", "code": "x = 1/0"},
        )
        assert "Fix this Python bug:" in rendered
        assert "x = 1/0" in rendered

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self, manager):
        with pytest.raises(PromptNotFoundError):
            await manager.get("nonexistent")

    @pytest.mark.asyncio
    async def test_list_prompts(self, manager):
        await manager.create(name="a", template="template a", sync_to_langfuse=False)
        await manager.create(name="b", template="template b", sync_to_langfuse=False)

        prompts = await manager.list_prompts()
        assert len(prompts) == 2
        names = {p["name"] for p in prompts}
        assert "a" in names and "b" in names

    @pytest.mark.asyncio
    async def test_version_history(self, manager):
        await manager.create(name="evolving", template="v1", sync_to_langfuse=False)
        await manager.create(name="evolving", template="v2", sync_to_langfuse=False)
        await manager.create(name="evolving", template="v3", sync_to_langfuse=False)

        history = await manager.get_version_history("evolving")
        assert len(history) == 3
        assert [h.version for h in history] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_delete(self, manager):
        await manager.create(name="temp", template="delete me", sync_to_langfuse=False)
        assert await manager.delete("temp")
        assert not await manager.delete("temp")
        with pytest.raises(PromptNotFoundError):
            await manager.get("temp")
