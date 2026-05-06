# -*- coding: utf-8 -*-
"""Polling file watcher with debounce."""

from __future__ import annotations

from pathlib import Path
import threading
import time
from typing import Callable, Dict, Iterable, Optional


class DebouncedWatcher:
    """Poll file signatures and run callback after debounce."""

    def __init__(
        self,
        list_files: Callable[[], Iterable[Path]],
        on_debounced_change: Callable[[], None],
        poll_interval_seconds: float = 1.0,
        debounce_seconds: float = 1.5,
    ):
        self._list_files = list_files
        self._on_change = on_debounced_change
        self._poll_interval = max(0.2, float(poll_interval_seconds))
        self._debounce = max(0.1, float(debounce_seconds))

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._snapshot: Dict[str, tuple[float, int]] = {}
        self._dirty_since: float = 0.0
        self._running = False

    @property
    def running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="retrieval-watcher")
        self._thread.start()
        self._running = True

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._running = False

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            changed = self._detect_change()
            now = time.time()
            if changed:
                self._dirty_since = now
            elif self._dirty_since and now - self._dirty_since >= self._debounce:
                self._dirty_since = 0.0
                try:
                    self._on_change()
                except Exception:
                    # Keep watcher alive; errors are handled by engine status.
                    pass
            self._stop_event.wait(self._poll_interval)

    def _detect_change(self) -> bool:
        current: Dict[str, tuple[float, int]] = {}
        for path in self._list_files():
            try:
                stat = path.stat()
                current[str(path)] = (float(stat.st_mtime), int(stat.st_size))
            except Exception:
                continue
        changed = current != self._snapshot
        if changed:
            self._snapshot = current
        return changed
