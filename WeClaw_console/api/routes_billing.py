# -*- coding: utf-8 -*-
"""Billing routes backed by model_metering_core."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from integrations.metering import get_default_engine


router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


def _engine(request: Request):
    engine = getattr(request.app.state, "metering_engine", None)
    if engine is None:
        try:
            engine = get_default_engine()
        except Exception:
            engine = None
    if engine is None:
        raise HTTPException(status_code=503, detail="metering_engine_not_ready")
    return engine


@router.get("/status")
def billing_status(request: Request):
    engine = _engine(request)
    return {"success": True, "status": engine.status()}


@router.get("/overview")
def billing_overview(
    request: Request,
    from_ts: int | None = Query(default=None),
    to_ts: int | None = Query(default=None),
    bucket: str = Query(default=""),
    provider: str = Query(default=""),
    model: str = Query(default=""),
    profile_id: str = Query(default=""),
    status: str = Query(default="all"),
):
    engine = _engine(request)
    try:
        result = engine.get_overview(
            from_ts=from_ts,
            to_ts=to_ts,
            bucket=bucket,
            provider=provider,
            model=model,
            profile_id=profile_id,
            status=status,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "result": result}


@router.get("/calls")
def billing_calls(
    request: Request,
    from_ts: int | None = Query(default=None),
    to_ts: int | None = Query(default=None),
    provider: str = Query(default=""),
    model: str = Query(default=""),
    profile_id: str = Query(default=""),
    status: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    q: str = Query(default=""),
):
    engine = _engine(request)
    try:
        result = engine.list_calls(
            from_ts=from_ts,
            to_ts=to_ts,
            provider=provider,
            model=model,
            profile_id=profile_id,
            status=status,
            page=page,
            page_size=20,
            q=q,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "result": result}


@router.get("/calls/{call_id}")
def billing_call_detail(call_id: str, request: Request):
    engine = _engine(request)
    try:
        detail = engine.get_call_detail(call_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "detail": detail}
