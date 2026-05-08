# -*- coding: utf-8 -*-
"""MCP management routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


@router.get("/discovered")
def list_discovered(request: Request):
    runtime = _runtime(request)
    return {"success": True, "servers": runtime.list_mcp_discovered()}


@router.get("/clients")
def list_clients(request: Request):
    runtime = _runtime(request)
    return {"success": True, "clients": runtime.list_mcp_clients()}


@router.post("/sync")
def sync_clients(request: Request):
    runtime = _runtime(request)
    try:
        payload = runtime.sync_mcp()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"success": True, **payload}


@router.post("/clients")
def upsert_client(request: Request, body: Dict[str, Any]):
    runtime = _runtime(request)
    try:
        payload = runtime.upsert_mcp_client(body or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"success": True, **payload}


@router.patch("/clients/{client_id}/toggle")
def toggle_client(client_id: str, request: Request, body: Dict[str, Any]):
    runtime = _runtime(request)
    enabled = bool((body or {}).get("enabled", True))
    try:
        payload = runtime.toggle_mcp_client(client_id, enabled=enabled)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"success": True, **payload}


@router.delete("/clients/{client_id}")
def delete_client(client_id: str, request: Request):
    runtime = _runtime(request)
    try:
        payload = runtime.delete_mcp_client(client_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"success": True, **payload}
