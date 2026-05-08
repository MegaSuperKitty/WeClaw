# -*- coding: utf-8 -*-
"""Search routes backed by retrieval integration."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, Request


router = APIRouter(prefix="/api/v1/search", tags=["search"])


def _engine(request: Request):
    engine = getattr(request.app.state, "search_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="search_engine_not_ready")
    return engine


@router.get("/status")
def search_status(request: Request):
    engine = _engine(request)
    return {"success": True, "status": engine.status_dict()}


@router.post("/reindex")
def search_reindex(request: Request):
    engine = _engine(request)
    stats = engine.reindex_now(force=True)
    return {"success": True, "stats": stats, "status": engine.status_dict()}


@router.get("/sessions")
def search_sessions(
    request: Request,
    q: str = Query(..., min_length=1, max_length=600),
    limit: int = Query(20, ge=1, le=100),
    channel: str = Query(""),
    user_id: str = Query(""),
):
    engine = _engine(request)
    result = engine.search_sessions(query=q, limit=limit, channel_prefix=channel, user_id=user_id)
    return {"success": True, "result": asdict(result)}
