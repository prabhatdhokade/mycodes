"""Central configuration for the Optima AI platform.

Uses pydantic-settings to load from environment variables / .env files,
with sensible defaults for local development.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    ttl_seconds: int = 3600

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"
    port: int = 5432
    name: str = "optima"
    user: str = "optima"
    password: str = "optima"
    pool_min: int = 2
    pool_max: int = 10

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class LangfuseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LANGFUSE_")

    public_key: str = ""
    secret_key: str = ""
    host: str = "https://cloud.langfuse.com"
    enabled: bool = True
    cache_ttl_seconds: int = 300


class AnthropicSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")

    api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8192
    temperature: float = 0.0


class Settings(BaseSettings):
    """Root application settings — aggregates all sub-configs."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Optima AI"
    environment: Environment = Environment.LOCAL
    debug: bool = False
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    cors_origins: list[str] = ["*"]

    redis: RedisSettings = Field(default_factory=RedisSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)

    @model_validator(mode="after")
    def _set_debug_from_env(self) -> "Settings":
        if self.environment == Environment.LOCAL:
            self.debug = True
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
