"""Tests for artifact management system."""

from __future__ import annotations

import pytest

from optima_ai.artifacts.manager import ArtifactManager, ArtifactType
from optima_ai.artifacts.store import ArtifactStore
from optima_ai.core.exceptions import ArtifactNotFoundError


class TestArtifactStore:
    @pytest.fixture
    def store(self):
        return ArtifactStore()

    @pytest.mark.asyncio
    async def test_save_and_get(self, store):
        artifact = {"id": "a1", "content": "hello", "session_id": "s1"}
        await store.save(artifact)
        result = await store.get("a1")
        assert result is not None
        assert result["content"] == "hello"

    @pytest.mark.asyncio
    async def test_versioning(self, store):
        await store.save({"id": "a1", "content": "v1", "session_id": "s1"})
        await store.save({"id": "a1", "content": "v2", "session_id": "s1"})

        current = await store.get("a1")
        assert current["content"] == "v2"

        v1 = await store.get_version("a1", 1)
        assert v1["content"] == "v1"

        v2 = await store.get_version("a1", 2)
        assert v2["content"] == "v2"

        count = await store.get_version_count("a1")
        assert count == 2

    @pytest.mark.asyncio
    async def test_list_by_session(self, store):
        await store.save({"id": "a1", "content": "x", "session_id": "s1"})
        await store.save({"id": "a2", "content": "y", "session_id": "s1"})
        await store.save({"id": "a3", "content": "z", "session_id": "s2"})

        s1_artifacts = await store.list_by_session("s1")
        assert len(s1_artifacts) == 2

        s2_artifacts = await store.list_by_session("s2")
        assert len(s2_artifacts) == 1

    @pytest.mark.asyncio
    async def test_delete(self, store):
        await store.save({"id": "a1", "content": "x", "session_id": "s1"})
        assert await store.delete("a1")
        assert await store.get("a1") is None
        assert not await store.delete("a1")

    @pytest.mark.asyncio
    async def test_search(self, store):
        await store.save({"id": "a1", "artifact_type": "code", "language": "python", "session_id": "s1"})
        await store.save({"id": "a2", "artifact_type": "test", "language": "python", "session_id": "s1"})
        await store.save({"id": "a3", "artifact_type": "code", "language": "javascript", "session_id": "s1"})

        code_artifacts = await store.search(artifact_type="code")
        assert len(code_artifacts) == 2

        python_artifacts = await store.search(language="python")
        assert len(python_artifacts) == 2


class TestArtifactManager:
    @pytest.fixture
    def manager(self):
        return ArtifactManager()

    @pytest.mark.asyncio
    async def test_create_artifact(self, manager):
        record = await manager.create(
            session_id="s1",
            artifact_type=ArtifactType.CODE,
            title="Hello World",
            content="print('hello')",
            language="python",
        )
        assert record.id
        assert record.title == "Hello World"
        assert record.artifact_type == ArtifactType.CODE
        assert record.version == 1

    @pytest.mark.asyncio
    async def test_update_creates_new_version(self, manager):
        record = await manager.create(
            session_id="s1",
            artifact_type=ArtifactType.CODE,
            title="v1",
            content="version 1",
        )

        updated = await manager.update(record.id, content="version 2")
        assert updated.version == 2

    @pytest.mark.asyncio
    async def test_update_same_content_no_version(self, manager):
        record = await manager.create(
            session_id="s1",
            artifact_type=ArtifactType.CODE,
            title="test",
            content="same content",
        )

        updated = await manager.update(record.id, content="same content")
        assert updated.version == record.version

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self, manager):
        with pytest.raises(ArtifactNotFoundError):
            await manager.get("nonexistent")

    @pytest.mark.asyncio
    async def test_diff(self, manager):
        record = await manager.create(
            session_id="s1",
            artifact_type=ArtifactType.CODE,
            title="test",
            content="line1\nline2\nline3",
        )
        await manager.update(record.id, content="line1\nmodified\nline3\nline4")

        diff_result = await manager.diff(record.id, 1, 2)
        assert diff_result["artifact_id"] == record.id
        assert "modified" in diff_result["diff"]
