# -*- coding: utf-8 -*-
"""Runtime settings routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import RuntimeSettingsRequest


router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def _store(request: Request):
    store = getattr(request.app.state, "runtime_config_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="runtime_config_store_not_ready")
    return store


@router.get("")
def get_settings(request: Request):
    return _store(request).get_state()


@router.put("")
def update_settings(body: RuntimeSettingsRequest, request: Request):
    return _store(request).update_state(body.model_dump())
