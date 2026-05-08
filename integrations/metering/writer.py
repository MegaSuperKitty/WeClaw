# -*- coding: utf-8 -*-
"""Thread-safe JSONL writer with daily partition folders."""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import threading
from typing import Any, Dict

from .utils import compact_json, day_from_ts, ensure_dir, now_ts


class JsonlDailyWriter:
    def __init__(self, base_dir: str):
        self.base_dir = ensure_dir(base_dir)
        self._lock = threading.Lock()
        self._error_count = 0
        self._last_write_at = 0.0

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def last_write_at(self) -> float:
        return self._last_write_at

    def append(self, record: Dict[str, Any]) -> None:
        ts = float(record.get("started_at") or now_ts())
        day = day_from_ts(ts)
        pid = os.getpid()
        line = compact_json(record)

        target_dir = self.base_dir / day
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"calls-{pid}.jsonl"

        with self._lock:
            try:
                with file_path.open("a", encoding="utf-8") as handle:
                    handle.write(line)
                    handle.write("\n")
                self._last_write_at = now_ts()
            except Exception as exc:
                self._error_count += 1
                print(f"[model_metering_core] append failed: {exc}")

    def status(self) -> Dict[str, Any]:
        return {
            "log_dir": str(self.base_dir),
            "writer_errors": self._error_count,
            "last_write_at": self._last_write_at,
        }
