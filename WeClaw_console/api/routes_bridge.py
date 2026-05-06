# -*- coding: utf-8 -*-
"""Bridge routes for external channel services."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/api/v1/bridge", tags=["bridge"])


def _gateway(request: Request):
    gateway = getattr(request.app.state, "gateway", None)
    if gateway is None:
        raise HTTPException(status_code=503, detail="gateway_not_ready")
    return gateway


@router.post("/inbound")
def bridge_inbound(payload: Dict[str, Any], request: Request):
    gateway = _gateway(request)
    return gateway.ingest_bridge_inbound(payload)


@router.get("/outbound/pull")
def bridge_outbound_pull(request: Request, channel: str = "", account_id: str = ""):
    gateway = _gateway(request)
    return gateway.pull_bridge_outbound(channel=channel, account_id=account_id)
