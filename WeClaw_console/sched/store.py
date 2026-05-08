# -*- coding: utf-8 -*-
"""Thread-safe JSON persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any, Dict


class JsonStore:
    """Simple atomic JSON file store."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self, default: Any) -> Any:
        with self._lock:
            if not self.path.exists():
                return default
            try:
                with open(self.path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                return data
            except Exception:
                return default

    def write(self, payload: Any) -> None:
        with self._lock:
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            tmp.replace(self.path)


def now_iso() -> str:
    from datetime import datetime

    return datetime.now().isoformat(timespec="seconds")


def deep_copy_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(data, ensure_ascii=False))
