"""Prompt management API — CRUD for prompt templates with versioning."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from optima_ai.api.middleware.auth import optional_user
from optima_ai.core.exceptions import PromptNotFoundError
from optima_ai.prompts.manager import PromptManager

router = APIRouter(prefix="/prompts", tags=["prompts"])
_prompt_manager = PromptManager()


class CreatePromptRequest(BaseModel):
    name: str
    template: str
    labels: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    sync_to_langfuse: bool = True


class RenderPromptRequest(BaseModel):
    name: str
    variables: dict[str, str]
    version: int | None = None


@router.post("")
async def create_prompt(
    req: CreatePromptRequest,
    user: Any = Depends(optional_user),
):
    record = await _prompt_manager.create(
        name=req.name,
        template=req.template,
        labels=req.labels,
        config=req.config,
        sync_to_langfuse=req.sync_to_langfuse,
    )
    return record.model_dump(mode="json")


@router.get("/{name}")
async def get_prompt(name: str, version: int | None = None):
    try:
        record = await _prompt_manager.get(name, version)
        return record.model_dump(mode="json")
    except PromptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("")
async def list_prompts():
    return await _prompt_manager.list_prompts()


@router.post("/render")
async def render_prompt(req: RenderPromptRequest):
    try:
        rendered = await _prompt_manager.render(req.name, req.variables, req.version)
        return {"rendered": rendered}
    except PromptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("/{name}/versions")
async def get_version_history(name: str):
    try:
        versions = await _prompt_manager.get_version_history(name)
        return [v.model_dump(mode="json") for v in versions]
    except PromptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.delete("/{name}")
async def delete_prompt(name: str):
    deleted = await _prompt_manager.delete(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"deleted": True}
