# -*- coding: utf-8 -*-
"""Task board routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


def _raise_task_error(exc: ValueError) -> None:
    detail = str(exc) or "invalid_task_request"
    status_code = 404 if detail in {"session_not_found"} or detail.startswith("invalid_task_state:") else 400
    raise HTTPException(status_code=status_code, detail=detail) from exc


@router.get("")
def list_tasks(
    request: Request,
    user_id: str = Query(...),
    session_name: str = Query(...),
):
    runtime = _runtime(request)
    try:
        return runtime.list_tasks(user_id, session_name)
    except ValueError as exc:
        _raise_task_error(exc)


@router.get("/{task_id}")
def get_task(
    task_id: str,
    request: Request,
    user_id: str = Query(...),
    session_name: str = Query(...),
):
    runtime = _runtime(request)
    try:
        return runtime.get_task_detail(user_id, session_name, task_id)
    except ValueError as exc:
        _raise_task_error(exc)


@router.get("/{task_id}/messages")
def get_task_messages(
    task_id: str,
    request: Request,
    user_id: str = Query(...),
    session_name: str = Query(...),
):
    runtime = _runtime(request)
    try:
        return runtime.get_task_messages(user_id, session_name, task_id)
    except ValueError as exc:
        _raise_task_error(exc)
