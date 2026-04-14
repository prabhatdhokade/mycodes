"""Tests for configuration management."""

from __future__ import annotations

from optima_ai.core.config import Environment, Settings


class TestSettings:
    def test_defaults(self):
        settings = Settings()
        assert settings.app_name == "Optima AI"
        assert settings.environment == Environment.LOCAL
        assert settings.debug is True  # auto-set for LOCAL
        assert settings.port == 8000

    def test_redis_url(self):
        settings = Settings()
        assert "redis://" in settings.redis.url
        assert "localhost" in settings.redis.url

    def test_redis_url_with_password(self):
        settings = Settings()
        settings.redis.password = "secret"
        assert ":secret@" in settings.redis.url

    def test_database_url(self):
        settings = Settings()
        url = settings.database.async_url
        assert "postgresql+asyncpg://" in url
        assert "optima" in url
