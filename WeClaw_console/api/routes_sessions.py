# -*- coding: utf-8 -*-
"""Session routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from .schemas import SessionNewRequest, SessionSelectRequest


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


@router.get("")
def list_sessions(request: Request):
    runtime = _runtime(request)
    return {"sessions": runtime.list_sessions()}


@router.post("/new")
def new_session(body: SessionNewRequest, request: Request):
    runtime = _runtime(request)
    user_id = (body.user_id or "").strip() or runtime.web_user_id
    if user_id != runtime.web_user_id:
        # v1 constraint: new sessions from web always use web user prefix.
        user_id = runtime.web_user_id
    created = runtime.create_web_session()
    return {"session": created}


@router.post("/select")
def select_session(body: SessionSelectRequest, request: Request):
    runtime = _runtime(request)
    result = runtime.select_session(body.user_id, body.session_name)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail="session_not_found")
    return result


@router.get("/messages")
def get_messages(
    request: Request,
    user_id: str = Query(...),
    session_name: str = Query(...),
):
    runtime = _runtime(request)
    messages = runtime.get_session_messages(user_id, session_name)
    render_messages = runtime.get_session_render_messages(user_id, session_name)
    return {"messages": messages, "render_messages": render_messages}


@router.get("/task-events")
def get_task_events(
    request: Request,
    user_id: str = Query(...),
    session_name: str = Query(...),
    task_id: str = Query(...),
):
    runtime = _runtime(request)
    try:
        payload = runtime.get_task_events(user_id, session_name, task_id)
    except ValueError as exc:
        detail = str(exc) or "invalid_task_request"
        status_code = 404 if detail in {"session_not_found"} or detail.startswith("invalid_task_state:") else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return payload
