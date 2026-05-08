# -*- coding: utf-8 -*-
"""Async stream bus for SSE events."""

from __future__ import annotations

from dataclasses import dataclass
import asyncio
import threading
import time
from typing import Any, Dict, Optional


@dataclass
class SSEEvent:
    """Single event payload delivered to SSE consumers."""

    type: str
    ts: float
    request_id: str
    payload: Dict[str, Any]


class EventStreamBus:
    """Thread-safe bridge from sync workers to async SSE queues."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._streams: Dict[str, tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = {}

    def create_stream(self, request_id: str, loop: asyncio.AbstractEventLoop) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._streams[request_id] = (loop, queue)
        return queue

    def emit(self, request_id: str, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        payload = payload or {}
        with self._lock:
            entry = self._streams.get(request_id)
        if not entry:
            return
        loop, queue = entry
        event = SSEEvent(
            type=event_type,
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
