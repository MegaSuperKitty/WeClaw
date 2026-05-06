# -*- coding: utf-8 -*-
"""Asyncio compatibility helpers for entry scripts."""

from __future__ import annotations

import asyncio


def ensure_main_thread_event_loop() -> asyncio.AbstractEventLoop:
    """Return a current event loop, creating one when Python no longer does."""

    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
