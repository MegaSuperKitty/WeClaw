# -*- coding: utf-8 -*-
"""Persistence for workspace-local browser runtime state."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from core.workspace.layout import WorkspaceLayout


class BrowserSessionStore:
    """Persist browser profiles and runtime state under layout.browser_root."""

    def __init__(self, layout: WorkspaceLayout):
        self.layout = layout
        self.browser_root = Path(layout.browser_root)
        self.profiles_dir = self.browser_root / "profiles"
        self.installs_dir = self.browser_root / "installs"
        self.install_logs_dir = self.installs_dir / "logs"
        self.diagnostics_dir = self.browser_root / "diagnostics"
        self.artifacts_dir = self.browser_root / "artifacts"
        self.screenshots_dir = self.artifacts_dir / "screenshots"
        self.snapshots_dir = self.artifacts_dir / "snapshots"
        self.profiles_path = self.profiles_dir / "profiles.json"
        self.runtime_state_path = self.browser_root / "runtime_state.json"
        self.install_state_path = self.installs_dir / "install_state.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path in (
            self.browser_root,
            self.profiles_dir,
            self.installs_dir,
            self.install_logs_dir,
            self.diagnostics_dir,
            self.artifacts_dir,
            self.screenshots_dir,
            self.snapshots_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
        if not path.is_file():
            return dict(default)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return dict(default)

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_profiles_payload(self) -> Dict[str, Any]:
        return self._read_json(self.profiles_path, default={})

    def save_profiles_payload(self, payload: Dict[str, Any]) -> None:
        self._write_json(self.profiles_path, payload)

    def load_runtime_state(self) -> Dict[str, Any]:
        return self._read_json(self.runtime_state_path, default={"profiles": {}})

    def save_runtime_state(self, payload: Dict[str, Any]) -> None:
        self._write_json(self.runtime_state_path, payload)

    def load_install_state(self) -> Dict[str, Any]:
        return self._read_json(self.install_state_path, default={})

    def save_install_state(self, payload: Dict[str, Any]) -> None:
        self._write_json(self.install_state_path, payload)

    def append_install_log(self, name: str, line: str) -> None:
        path = self.install_logs_dir / name
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{line.rstrip()}\n")

    def profile_runtime_user_dir(self, profile_id: str) -> str:
        safe_id = str(profile_id or "managed-default").strip() or "managed-default"
        path = self.profiles_dir / safe_id / "user-data"
        os.makedirs(path, exist_ok=True)
        return str(path)

    def user_identity_work_dir(self, family: str) -> str:
        safe_family = str(family or "browser").strip() or "browser"
        path = self.profiles_dir / "identity-work" / safe_family / "user-data"
        os.makedirs(path, exist_ok=True)
        return str(path)
