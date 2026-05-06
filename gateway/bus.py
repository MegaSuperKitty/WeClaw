# -*- coding: utf-8 -*-
"""Thread-safe event bus used by gateway stream subscribers."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Dict, Optional

from .events import GatewayEvent


class GatewayEventBus:
    """Bridge sync worker threads to async subscribers."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._streams: Dict[str, tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = {}

    def create_stream(self, request_id: str, loop: asyncio.AbstractEventLoop) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._streams[request_id] = (loop, queue)
        return queue

    def emit(self, request_id: str, event_type: str, payload: Optional[dict] = None) -> None:
        payload = dict(payload or {})
        with self._lock:
            entry = self._streams.get(request_id)
        if not entry:
            return
        loop, queue = entry
        event = GatewayEvent(
            type=str(event_type or "").strip() or "unknown",
            ts=time.time(),
            request_id=request_id,
            payload=payload,
        )

        def _push() -> None:
            queue.put_nowait(event)

        loop.call_soon_threadsafe(_push)

    def close_stream(self, request_id: str) -> None:
        with self._lock:
            entry = self._streams.pop(request_id, None)
        if not entry:
            return
        loop, queue = entry

        def _push_end() -> None:
            queue.put_nowait(None)

        loop.call_soon_threadsafe(_push_end)
