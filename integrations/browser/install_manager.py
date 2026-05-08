# -*- coding: utf-8 -*-
"""Managed Chromium detection and install workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Dict, List

from .models import (
    BrowserInstallState,
    INSTALL_FAILED,
    INSTALL_INSTALLED,
    INSTALL_INSTALLING,
    INSTALL_PENDING,
)
from .session_store import BrowserSessionStore


WINDOWS_BROWSER_CANDIDATES = [
    ("chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    ("chrome", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ("edge", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ("edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ("brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ("chromium", r"C:\Program Files\Chromium\Application\chrome.exe"),
]

MAC_BROWSER_CANDIDATES = [
    ("chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    ("edge", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ("brave", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
    ("chromium", "/Applications/Chromium.app/Contents/MacOS/Chromium"),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BrowserInstallManager:
    """Detect system Chromium browsers and manage Playwright Chromium fallback."""

    def __init__(self, store: BrowserSessionStore, cache_dir: str = ""):
        self.store = store
        self.cache_dir = cache_dir or str((Path(store.installs_dir) / "cache").resolve())
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    def _load_state(self) -> BrowserInstallState:
        raw = self.store.load_install_state()
        return BrowserInstallState(
            status=str(raw.get("status") or INSTALL_PENDING),
            platform=str(raw.get("platform") or platform.system().lower()),
            cache_dir=str(raw.get("cache_dir") or self.cache_dir),
            installed_executable_path=str(raw.get("installed_executable_path") or ""),
            installed_browser_name=str(raw.get("installed_browser_name") or ""),
            installed_at=str(raw.get("installed_at") or ""),
            last_error=str(raw.get("last_error") or ""),
            system_browsers=list(raw.get("system_browsers") or []),
            offer_install=bool(raw.get("offer_install", False)),
            logs=[str(item) for item in (raw.get("logs") or [])],
        )

    def _save_state(self) -> None:
        self.store.save_install_state(self._state.to_dict())

    def get_state(self) -> BrowserInstallState:
        return self._state

    def detect_system_browsers(self) -> List[Dict[str, str]]:
        detected: List[Dict[str, str]] = []
        system_name = platform.system().lower()
        candidates = MAC_BROWSER_CANDIDATES if system_name == "darwin" else WINDOWS_BROWSER_CANDIDATES if system_name == "windows" else []

        seen_paths = set()
        for name, candidate in candidates:
            if os.path.isfile(candidate) and candidate not in seen_paths:
                seen_paths.add(candidate)
                detected.append({"name": name, "path": os.path.abspath(candidate), "source": "well_known"})

        for command, label in (
            ("chrome", "chrome"),
            ("google-chrome", "chrome"),
            ("msedge", "edge"),
            ("brave", "brave"),
            ("chromium", "chromium"),
            ("chromium-browser", "chromium"),
        ):
            resolved = shutil.which(command)
            if resolved and resolved not in seen_paths:
                seen_paths.add(resolved)
                detected.append({"name": label, "path": os.path.abspath(resolved), "source": "path"})

        self._state.platform = system_name
        self._state.system_browsers = detected
        self._state.offer_install = self.should_offer_managed_install()
        self._save_state()
        return detected

    def should_offer_managed_install(self) -> bool:
        if platform.system().lower() not in {"windows", "darwin"}:
            return False
        return not bool(self._state.system_browsers)

    def get_preferred_executable(self) -> str:
        if self._state.system_browsers:
            return str(self._state.system_browsers[0].get("path") or "")
        if self._state.installed_executable_path and os.path.isfile(self._state.installed_executable_path):
            return self._state.installed_executable_path
        return ""

    def install_managed_browser(self) -> BrowserInstallState:
        self._state.status = INSTALL_INSTALLING
        self._state.last_error = ""
        self._state.logs = []
        self._state.cache_dir = self.cache_dir
        self._save_state()
        self.store.append_install_log("install.log", "install managed chromium started")

        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = self.cache_dir
        command = [sys.executable, "-m", "playwright", "install", "chromium"]

        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                env=env,
                timeout=1800,
            )
            stdout = str(result.stdout or "").strip()
            stderr = str(result.stderr or "").strip()
            if stdout:
                self.store.append_install_log("install.log", stdout)
            if stderr:
                self.store.append_install_log("install.log", stderr)
            if result.returncode != 0:
                raise RuntimeError(stderr or stdout or f"playwright install exited with {result.returncode}")

            executable = self._find_playwright_executable()
            if not executable:
                raise RuntimeError("managed chromium executable not found after install")

            self._state.status = INSTALL_INSTALLED
            self._state.installed_executable_path = executable
            self._state.installed_browser_name = "managed-chromium"
            self._state.installed_at = _utc_now()
            self._state.logs = ["install completed"]
            self._save_state()
            return self._state
        except Exception as exc:
            self._state.status = INSTALL_FAILED
            self._state.last_error = str(exc)
            self._state.logs = [str(exc)]
            self._save_state()
            self.store.append_install_log("install.log", f"install failed: {exc}")
            return self._state

    def cancel_install(self) -> BrowserInstallState:
        if self._state.status == INSTALL_INSTALLING:
            self._state.status = INSTALL_PENDING
            self._state.logs = ["install canceled"]
            self.store.append_install_log("install.log", "install canceled")
        self._save_state()
        return self._state

    def remove_managed_browser(self) -> BrowserInstallState:
        cache_root = Path(self.cache_dir)
        if cache_root.exists():
            shutil.rmtree(cache_root, ignore_errors=True)
        cache_root.mkdir(parents=True, exist_ok=True)
        self._state.status = INSTALL_PENDING
        self._state.installed_executable_path = ""
        self._state.installed_browser_name = ""
        self._state.installed_at = ""
        self._state.last_error = ""
        self._state.logs = ["managed browser removed"]
        self._state.offer_install = self.should_offer_managed_install()
        self.store.append_install_log("install.log", "managed browser removed")
        self._save_state()
        return self._state

    def reinstall_managed_browser(self) -> BrowserInstallState:
        self.remove_managed_browser()
        return self.install_managed_browser()

    def _find_playwright_executable(self) -> str:
        root = Path(self.cache_dir)
        candidates = []
        if platform.system().lower() == "windows":
            candidates.extend(root.glob("**/chrome-win/chrome.exe"))
        elif platform.system().lower() == "darwin":
            candidates.extend(root.glob("**/chrome-mac/Chromium.app/Contents/MacOS/Chromium"))
        else:
            candidates.extend(root.glob("**/chrome-linux/chrome"))

        for path in candidates:
            if path.is_file():
                return str(path.resolve())
        return ""
