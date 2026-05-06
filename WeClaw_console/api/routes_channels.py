# -*- coding: utf-8 -*-
"""Channel configuration and runtime routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import ChannelUpdateRequest
from WeClaw_console.core.channel_service import ChannelConflictError, ChannelNotFoundError


router = APIRouter(prefix="/api/v1/channels", tags=["channels"])


def _service(request: Request):
    service = getattr(request.app.state, "channel_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="channel_service_not_ready")
    return service


@router.get("")
def get_channels(request: Request):
    return _service(request).get_state()


@router.put("/{channel_name}")
def update_channel(channel_name: str, body: ChannelUpdateRequest, request: Request):
    service = _service(request)
    try:
        return service.update_channel(
            channel_name=channel_name,
            enabled=body.enabled,
            bot_prefix=body.bot_prefix,
            settings=body.settings,
        )
    except ChannelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{channel_name}/start")
def start_channel(channel_name: str, request: Request):
    service = _service(request)
    try:
        return service.start_channel(channel_name)
    except ChannelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChannelConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{channel_name}/stop")
def stop_channel(channel_name: str, request: Request):
    service = _service(request)
    try:
        return service.stop_channel(channel_name)
    except ChannelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChannelConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{channel_name}/restart")
def restart_channel(channel_name: str, request: Request):
    service = _service(request)
    try:
        return service.restart_channel(channel_name)
    except ChannelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChannelConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
