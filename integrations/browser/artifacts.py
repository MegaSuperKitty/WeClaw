# -*- coding: utf-8 -*-
"""Artifact persistence for browser screenshots and snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Dict, List

from .session_store import BrowserSessionStore


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip())
    return text.strip("-") or "default"


class BrowserArtifacts:
    """Store and list browser artifacts under layout.browser_root."""

    def __init__(self, store: BrowserSessionStore):
        self.store = store
        self.root = Path(store.browser_root) / "artifacts"
        self.screenshots_dir = self.root / "screenshots"
        self.snapshots_dir = self.root / "snapshots"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path in (self.root, self.screenshots_dir, self.snapshots_dir):
            path.mkdir(parents=True, exist_ok=True)

    def save_screenshot(self, *, profile_id: str, tab_id: str, content: bytes) -> Dict[str, object]:
        stamp = _utc_stamp()
        filename = f"{stamp}_{_safe(profile_id)}_{_safe(tab_id)}.png"
        path = self.screenshots_dir / filename
        path.write_bytes(content)
        return {
            "kind": "screenshot",
            "profile_id": profile_id,
            "tab_id": tab_id,
            "path": str(path.resolve()),
            "created_at": stamp,
        }

    def save_snapshot(self, *, profile_id: str, tab_id: str, payload: Dict[str, object]) -> Dict[str, object]:
        stamp = _utc_stamp()
        filename = f"{stamp}_{_safe(profile_id)}_{_safe(tab_id)}.json"
        path = self.snapshots_dir / filename
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "kind": "snapshot",
            "profile_id": profile_id,
            "tab_id": tab_id,
            "path": str(path.resolve()),
            "created_at": stamp,
        }

    def list_recent(self, limit: int = 10, *, kind: str = "", profile_id: str = "") -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        safe_profile = _safe(profile_id) if str(profile_id or "").strip() else ""
        for directory, row_kind in (
            (self.screenshots_dir, "screenshot"),
            (self.snapshots_dir, "snapshot"),
        ):
            if kind and row_kind != kind:
                continue
            for path in directory.glob("*"):
                if not path.is_file():
                    continue
                if safe_profile and f"_{safe_profile}_" not in path.name:
                    continue
                rows.append(
                    {
                        "kind": row_kind,
                        "path": str(path.resolve()),
                        "name": path.name,
                        "updated_at": path.stat().st_mtime,
                    }
                )
        rows.sort(key=lambda item: float(item.get("updated_at") or 0.0), reverse=True)
        return rows[: max(1, int(limit or 10))]
