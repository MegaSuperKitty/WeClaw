# -*- coding: utf-8 -*-
"""Workspace file tree and file read/write routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from .schemas import WorkspaceFileSaveRequest


router = APIRouter(prefix="/api/v1/workspace/files", tags=["workspace-files"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


@router.get("/tree")
def list_workspace_files(request: Request, query: str = Query("", description="Optional filename query")):
    runtime = _runtime(request)
    return {"success": True, **runtime.list_workspace_files(query=query)}


@router.get("/file")
def get_workspace_file(
    request: Request,
    path: str = Query(..., description="Relative file path under the workspace root"),
):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.get_workspace_file(path)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/file")
def save_workspace_file(body: WorkspaceFileSaveRequest, request: Request):
    runtime = _runtime(request)
    try:
        return {"success": True, **runtime.save_workspace_file(body.path, body.content)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
