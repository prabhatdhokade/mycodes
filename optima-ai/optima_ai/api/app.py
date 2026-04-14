"""FastAPI application factory — wires together all routes, middleware, and lifecycle hooks."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from optima_ai.api.routes import artifacts, chat, health, prompts, providers
from optima_ai.core.config import get_settings
from optima_ai.core.exceptions import OptimaError
from optima_ai.core.logging import get_logger, setup_logging
from optima_ai.mcp_providers.base import MCPProviderRegistry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("optima_ai.startup", environment=get_settings().environment.value)
    yield
    await MCPProviderRegistry.shutdown_all()
    logger.info("optima_ai.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Optima AI",
        description="Real-Time Code Assistance & Agentic Developer Platform",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(artifacts.router, prefix="/api/v1")
    app.include_router(prompts.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/api/v1")

    @app.exception_handler(OptimaError)
    async def optima_error_handler(request: Request, exc: OptimaError):
        return JSONResponse(
            status_code=exc.status,
            content={"error": exc.code, "message": exc.message},
        )

    return app


app = create_app()
