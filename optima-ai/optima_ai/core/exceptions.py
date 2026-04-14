"""Domain-specific exceptions used across the platform."""

from __future__ import annotations


class OptimaError(Exception):
    """Base exception for all Optima AI errors."""

    def __init__(self, message: str, *, code: str = "OPTIMA_ERROR", status: int = 500):
        self.message = message
        self.code = code
        self.status = status
        super().__init__(message)


class ProviderConnectionError(OptimaError):
    def __init__(self, provider: str, detail: str = ""):
        super().__init__(
            f"Failed to connect to MCP provider '{provider}': {detail}",
            code="PROVIDER_CONNECTION_ERROR",
            status=502,
        )


class ProviderNotFoundError(OptimaError):
    def __init__(self, provider: str):
        super().__init__(
            f"MCP provider '{provider}' is not registered",
            code="PROVIDER_NOT_FOUND",
            status=404,
        )


class AgentExecutionError(OptimaError):
    def __init__(self, detail: str):
        super().__init__(detail, code="AGENT_EXECUTION_ERROR", status=500)


class ArtifactNotFoundError(OptimaError):
    def __init__(self, artifact_id: str):
        super().__init__(
            f"Artifact '{artifact_id}' not found",
            code="ARTIFACT_NOT_FOUND",
            status=404,
        )


class PromptNotFoundError(OptimaError):
    def __init__(self, prompt_name: str, version: str | None = None):
        v = f" (version {version})" if version else ""
        super().__init__(
            f"Prompt '{prompt_name}'{v} not found",
            code="PROMPT_NOT_FOUND",
            status=404,
        )


class AuthenticationError(OptimaError):
    def __init__(self, detail: str = "Invalid or expired credentials"):
        super().__init__(detail, code="AUTH_ERROR", status=401)
