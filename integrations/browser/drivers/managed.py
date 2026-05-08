# -*- coding: utf-8 -*-
"""Managed browser driver."""

from __future__ import annotations

from datetime import datetime, timezone
import os
import signal
import subprocess
from typing import Dict

from ..install_manager import BrowserInstallManager
from ..models import BrowserProfile, BrowserProfileStatus
from ..profiles import compute_profile_capabilities


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManagedBrowserDriver:
    """Launch and stop a workspace-managed Chromium browser."""

    def __init__(self, install_manager: BrowserInstallManager):
        self.install_manager = install_manager

    def detect(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        row = dict(runtime_state.get(profile.profile_id) or {})
        executable = self._resolve_executable(profile)
        return BrowserProfileStatus(
            profile_id=profile.profile_id,
            driver=profile.driver,
            running=bool(row.get("running", False)),
            status=str(row.get("status") or "idle"),
            pid=row.get("pid") if isinstance(row.get("pid"), int) else None,
            executable_path=executable,
            cdp_url=str(row.get("cdp_url") or f"http://{profile.cdp_host}:{profile.cdp_port}"),
            last_error=str(row.get("last_error") or ""),
            updated_at=str(row.get("updated_at") or ""),
            capabilities=compute_profile_capabilities(profile),
        )

    def start(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        executable = self._resolve_executable(profile)
        if not executable:
            raise RuntimeError("no Chromium executable available for managed profile")

        user_data_dir = profile.user_data_dir or os.getcwd()
        os.makedirs(user_data_dir, exist_ok=True)

        command = [
            executable,
            f"--remote-debugging-port={profile.cdp_port}",
            f"--user-data-dir={user_data_dir}",
            "--new-window",
            "--no-first-run",
            "--no-default-browser-check",
            "about:blank",
        ]
        process = subprocess.Popen(command)
        status = BrowserProfileStatus(
            profile_id=profile.profile_id,
            driver=profile.driver,
            running=True,
            status="running",
            pid=int(process.pid),
            executable_path=executable,
            cdp_url=f"http://{profile.cdp_host}:{profile.cdp_port}",
            updated_at=_utc_now(),
            capabilities=compute_profile_capabilities(profile),
        )
        row = status.to_dict()
        row["launched_by_weclaw"] = True
        runtime_state[profile.profile_id] = row
        return status

    def stop(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        row = dict(runtime_state.get(profile.profile_id) or {})
        pid = row.get("pid")
        if isinstance(pid, int) and pid > 0:
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
                else:
                    os.kill(pid, signal.SIGTERM)
            except Exception:
                pass

        status = BrowserProfileStatus(
            profile_id=profile.profile_id,
            driver=profile.driver,
            running=False,
            status="stopped",
            pid=None,
            executable_path=str(row.get("executable_path") or self._resolve_executable(profile)),
            cdp_url=str(row.get("cdp_url") or f"http://{profile.cdp_host}:{profile.cdp_port}"),
            updated_at=_utc_now(),
            capabilities=compute_profile_capabilities(profile),
        )
        runtime_state[profile.profile_id] = status.to_dict()
        return status

    def _resolve_executable(self, profile: BrowserProfile) -> str:
        if profile.executable_path and os.path.isfile(profile.executable_path):
            return profile.executable_path

        detected = self.install_manager.detect_system_browsers()
        if detected:
            return str(detected[0].get("path") or "")

        install_state = self.install_manager.get_state()
        if install_state.installed_executable_path and os.path.isfile(install_state.installed_executable_path):
            return install_state.installed_executable_path

        return ""
