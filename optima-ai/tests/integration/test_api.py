"""Integration tests for the FastAPI application."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from optima_ai.api.app import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "optima-ai"

    @pytest.mark.asyncio
    async def test_ready(self, client):
        resp = await client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"


class TestProviderRoutes:
    @pytest.mark.asyncio
    async def test_list_providers(self, client):
        resp = await client.get("/api/v1/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert "filesystem" in data["providers"]
        assert "github" in data["providers"]


class TestPromptRoutes:
    @pytest.mark.asyncio
    async def test_create_and_get_prompt(self, client):
        resp = await client.post(
            "/api/v1/prompts",
            json={
                "name": "test_api_prompt",
                "template": "Hello {{name}}",
                "labels": ["test"],
                "sync_to_langfuse": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "test_api_prompt"
        assert data["version"] == 1

        resp = await client.get("/api/v1/prompts/test_api_prompt")
        assert resp.status_code == 200
        assert resp.json()["template"] == "Hello {{name}}"

    @pytest.mark.asyncio
    async def test_render_prompt(self, client):
        await client.post(
            "/api/v1/prompts",
            json={"name": "render_test", "template": "Hi {{user}}", "sync_to_langfuse": False},
        )
        resp = await client.post(
            "/api/v1/prompts/render",
            json={"name": "render_test", "variables": {"user": "Prabhat"}},
        )
        assert resp.status_code == 200
        assert resp.json()["rendered"] == "Hi Prabhat"

    @pytest.mark.asyncio
    async def test_list_prompts(self, client):
        await client.post(
            "/api/v1/prompts",
            json={"name": "list_test_a", "template": "a", "sync_to_langfuse": False},
        )
        resp = await client.get("/api/v1/prompts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestArtifactRoutes:
    @pytest.mark.asyncio
    async def test_create_and_get_artifact(self, client):
        resp = await client.post(
            "/api/v1/artifacts",
            json={
                "session_id": "test-session",
                "artifact_type": "code",
                "title": "Test Code",
                "content": "print('hello')",
                "language": "python",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        artifact_id = data["id"]
        assert data["title"] == "Test Code"

        resp = await client.get(f"/api/v1/artifacts/{artifact_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "print('hello')"

    @pytest.mark.asyncio
    async def test_update_artifact(self, client):
        create_resp = await client.post(
            "/api/v1/artifacts",
            json={
                "session_id": "test-session",
                "artifact_type": "code",
                "title": "Initial",
                "content": "v1",
            },
        )
        artifact_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/v1/artifacts/{artifact_id}",
            json={"content": "v2"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["version"] == 2

    @pytest.mark.asyncio
    async def test_session_artifacts(self, client):
        await client.post(
            "/api/v1/artifacts",
            json={
                "session_id": "session-list-test",
                "artifact_type": "code",
                "title": "A",
                "content": "a",
            },
        )
        resp = await client.get("/api/v1/artifacts/session/session-list-test")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
