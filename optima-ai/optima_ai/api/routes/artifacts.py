"""Artifacts API — CRUD for generated artifacts with version tracking."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from optima_ai.api.middleware.auth import optional_user
from optima_ai.artifacts.manager import ArtifactManager, ArtifactType
from optima_ai.core.exceptions import ArtifactNotFoundError
from optima_ai.services.auth import TokenPayload

router = APIRouter(prefix="/artifacts", tags=["artifacts"])
_artifact_manager = ArtifactManager()


class CreateArtifactRequest(BaseModel):
    session_id: str
    artifact_type: ArtifactType = ArtifactType.CODE
    title: str
    content: str
    language: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateArtifactRequest(BaseModel):
    content: str
    title: str | None = None
    metadata: dict[str, Any] | None = None


@router.post("")
async def create_artifact(
    req: CreateArtifactRequest,
    user: Any = Depends(optional_user),
):
    record = await _artifact_manager.create(
        session_id=req.session_id,
        artifact_type=req.artifact_type,
        title=req.title,
        content=req.content,
        language=req.language,
        metadata=req.metadata,
    )
    return record.model_dump(mode="json")


@router.get("/{artifact_id}")
async def get_artifact(artifact_id: str):
    try:
        record = await _artifact_manager.get(artifact_id)
        return record.model_dump(mode="json")
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.put("/{artifact_id}")
async def update_artifact(artifact_id: str, req: UpdateArtifactRequest):
    try:
        record = await _artifact_manager.update(
            artifact_id=artifact_id,
            content=req.content,
            title=req.title,
            metadata=req.metadata,
        )
        return record.model_dump(mode="json")
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("/{artifact_id}/versions/{version}")
async def get_artifact_version(artifact_id: str, version: int):
    try:
        record = await _artifact_manager.get_version(artifact_id, version)
        return record.model_dump(mode="json")
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("/{artifact_id}/diff")
async def diff_artifact(artifact_id: str, version_a: int, version_b: int):
    try:
        result = await _artifact_manager.diff(artifact_id, version_a, version_b)
        return result
    except ArtifactNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("/session/{session_id}")
async def list_session_artifacts(
    session_id: str,
    artifact_type: ArtifactType | None = None,
):
    records = await _artifact_manager.list_session_artifacts(session_id, artifact_type)
    return [r.model_dump(mode="json") for r in records]


@router.delete("/{artifact_id}")
async def delete_artifact(artifact_id: str):
    deleted = await _artifact_manager.delete(artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"deleted": True}
