# -*- coding: utf-8 -*-
"""Chat routes and SSE streaming."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from .schemas import CancelRequest, ChatStreamRequest, HumanInputRequest


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _gateway(request: Request):
    gateway = getattr(request.app.state, "gateway", None)
    if gateway is None:
        raise HTTPException(status_code=503, detail="gateway_not_ready")
    return gateway


def _format_sse(event) -> str:
    payload = {
        "type": event.type,
        "ts": event.ts,
        "request_id": event.request_id,
        "payload": event.payload,
    }
    data = json.dumps(payload, ensure_ascii=False)
    return f"event: {event.type}\ndata: {data}\n\n"


@router.post("/stream")
async def chat_stream(body: ChatStreamRequest, request: Request):
    gateway = _gateway(request)
    loop = asyncio.get_running_loop()
    request_id, queue = gateway.start_chat_stream(body, loop)

    async def event_generator() -> AsyncGenerator[str, None]:
        # Initial event so client knows final request_id.
        yield f"event: connected\ndata: {json.dumps({'request_id': request_id})}\n\n"
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield _format_sse(event)
        except asyncio.CancelledError:
            gateway.cancel_request(request_id)
            raise
        finally:
            gateway.cleanup_request(request_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/cancel")
def cancel_chat(body: CancelRequest, request: Request):
    gateway = _gateway(request)
    success = gateway.cancel_request(body.request_id)
    if not success:
        raise HTTPException(status_code=404, detail="request_not_found")
    return {"success": True}


@router.post("/human-input")
def human_input(body: HumanInputRequest, request: Request):
    gateway = _gateway(request)
    success = gateway.provide_human_input(body.user_id, body.content)
    if not success:
        raise HTTPException(status_code=404, detail="no_pending_human_input")
    return {"success": True}
