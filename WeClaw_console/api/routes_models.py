# -*- coding: utf-8 -*-
"""Model configuration routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import ModelProfileActivateRequest, ModelProfileUpsertRequest


router = APIRouter(prefix="/api/v1/models", tags=["models"])


def _manager(request: Request):
    manager = getattr(request.app.state, "model_manager", None)
    if manager is None:
        raise HTTPException(status_code=503, detail="model_manager_not_ready")
    return manager


@router.get("/state")
def get_state(request: Request):
    manager = _manager(request)
    return manager.get_state()


@router.post("/profiles")
def upsert_profile(body: ModelProfileUpsertRequest, request: Request):
    manager = _manager(request)
    try:
        state = manager.upsert_profile(
            model_type=body.model_type,
            profile_id=body.profile_id,
            provider=body.provider,
            base_url=body.base_url,
            model=body.model,
            api_key=body.api_key,
            max_tokens=body.max_tokens,
            timeout=body.timeout,
            temperature=body.temperature,
            top_p=body.top_p,
            clear_api_key=body.clear_api_key,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return state


@router.post("/activate")
def activate_profile(body: ModelProfileActivateRequest, request: Request):
    manager = _manager(request)
    try:
        state = manager.activate_profile(body.profile_id, model_type=body.model_type)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return state


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, request: Request, model_type: str = "text_generation"):
    manager = _manager(request)
    try:
        state = manager.delete_profile(profile_id, model_type=model_type)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return state


@router.post("/profiles/{profile_id}/test")
def test_profile(profile_id: str, request: Request, model_type: str = "text_generation"):
    manager = _manager(request)
    try:
        state = manager.test_profile_connectivity(profile_id, model_type=model_type)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return state
