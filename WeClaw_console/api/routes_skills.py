# -*- coding: utf-8 -*-
"""Skills routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


def _catalog(request: Request):
    catalog = getattr(request.app.state, "skills_catalog", None)
    if catalog is None:
        raise HTTPException(status_code=503, detail="skills_not_ready")
    return catalog


def _refresh_runtime(request: Request) -> None:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is not None:
        runtime.bot.refresh_skills()


@router.get("")
def list_skills(request: Request):
    catalog = _catalog(request)
    return {"success": True, "skills": catalog.list_skills()}


@router.post("/{skill_id}/enable")
def enable_skill(skill_id: str, request: Request):
    catalog = _catalog(request)
    catalog.registry.set_enabled(skill_id, True)
    _refresh_runtime(request)
    return {"success": True, "skills": catalog.list_skills()}


@router.post("/{skill_id}/disable")
def disable_skill(skill_id: str, request: Request):
    catalog = _catalog(request)
    catalog.registry.set_enabled(skill_id, False)
    _refresh_runtime(request)
    return {"success": True, "skills": catalog.list_skills()}
