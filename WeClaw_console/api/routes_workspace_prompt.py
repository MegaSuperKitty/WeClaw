# -*- coding: utf-8 -*-
"""Workspace prompt and memory file routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from .schemas import WorkspacePromptSaveRequest


router = APIRouter(prefix="/api/v1/workspace/prompt", tags=["workspace-prompt"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


@router.get("/files")
def list_prompt_files(request: Request):
    runtime = _runtime(request)
    return {"success": True, **runtime.list_workspace_prompt_files()}


@router.get("/file")
def get_prompt_file(
    request: Request,
    name: str = Query(..., description="Prompt file name under the workspace prompt root"),
):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.get_workspace_prompt_file(name)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/file")
def save_prompt_file(body: WorkspacePromptSaveRequest, request: Request):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.save_workspace_prompt_file(body.name, body.content)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/current-session")
def get_current_session_prompt(
    request: Request,
    user_id: str = Query("web:local"),
    session_name: str = Query(""),
):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.get_current_session_prompt(user_id=user_id, session_name=session_name)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/refresh")
def refresh_current_session_prompt(
    request: Request,
    user_id: str = Query("web:local"),
    session_name: str = Query(""),
):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.refresh_current_session_prompt(user_id=user_id, session_name=session_name)}
    except ValueError as exc:
        detail = str(exc)
        status_code = 409 if detail == "session_prompt_frozen" else 404
        raise HTTPException(status_code=status_code, detail=detail) from exc
