"""Health and readiness endpoints for load balancers and orchestration."""

from __future__ import annotations

from fastapi import APIRouter

from optima_ai.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "optima-ai"}


@router.get("/ready")
async def ready():
    settings = get_settings()
    return {
        "status": "ready",
        "environment": settings.environment.value,
        "version": "1.0.0",
    }
