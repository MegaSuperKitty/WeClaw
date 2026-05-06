# -*- coding: utf-8 -*-
"""Existing-session browser driver backed by local Chromium remote debugging."""

from __future__ import annotations

from datetime import datetime, timezone
import os
import signal
import subprocess
import time
from typing import Dict

from ..cdp import build_cdp_endpoint, get_cdp_version, list_page_tabs
from ..models import BrowserProfile, BrowserProfileStatus
from ..profiles import compute_profile_capabilities


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExistingSessionBrowserDriver:
    """Attach to a user-owned Chromium browser that already exposes CDP."""

    _STARTUP_RETRY_COUNT = 10
    _STARTUP_RETRY_DELAY_SECONDS = 0.6

    def _is_executable_running(self, executable_path: str) -> bool:
        path = str(executable_path or "").strip()
        if not path:
            return False
        image_name = os.path.basename(path)
        if not image_name:
            return False
        try:
            if os.name == "nt":
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {image_name}"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                output = str(result.stdout or "")
                return image_name.lower() in output.lower()
            result = subprocess.run(
                ["pgrep", "-f", image_name],
                check=False,
                capture_output=True,
                text=True,
            )
            return bool(str(result.stdout or "").strip())
        except Exception:
            return False

    def detect(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        row = dict(runtime_state.get(profile.profile_id) or {})
        endpoint = build_cdp_endpoint(profile.cdp_url, profile.cdp_host, profile.cdp_port)
        try:
            version = get_cdp_version(endpoint)
            tabs = list_page_tabs(endpoint)
            last_error = ""
            running = True
            status_name = "attached"
            transport = "cdp-existing-session"
            active_tab_id = str(tabs[0].get("target_id") or "") if tabs else ""
        except Exception as exc:
            version = {}
            tabs = []
            last_error = str(exc)
            running = False
            status_name = "waiting-for-browser"
            transport = "cdp-existing-session"
            active_tab_id = ""

        return BrowserProfileStatus(
            profile_id=profile.profile_id,
            driver=profile.driver,
            running=running,
            status=status_name,
            executable_path=str(row.get("executable_path") or ""),
            cdp_url=endpoint,
            last_error=last_error,
            updated_at=_utc_now(),
            capabilities=compute_profile_capabilities(profile),
            transport=transport,
            tabs=tabs,
            active_tab_id=active_tab_id,
            pid=row.get("pid") if isinstance(row.get("pid"), int) else None,
        )

    def start(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        status = self.detect(profile, runtime_state)
        existing_row = dict(runtime_state.get(profile.profile_id) or {})
        row = status.to_dict()
        row["executable_path"] = profile.executable_path or str(existing_row.get("executable_path") or "")
        row["launched_by_weclaw"] = bool(existing_row.get("launched_by_weclaw", False))
        runtime_state[profile.profile_id] = row
        if status.running:
            runtime_state[profile.profile_id]["launched_by_weclaw"] = False
            return status

        executable_path = str(profile.executable_path or "").strip()
        if executable_path and os.path.isfile(executable_path):
            runtime_state[profile.profile_id]["browser_running_before_launch"] = self._is_executable_running(executable_path)
            process = self._launch_browser_process(profile)
            runtime_state[profile.profile_id]["pid"] = int(process.pid)
            runtime_state[profile.profile_id]["executable_path"] = executable_path
            runtime_state[profile.profile_id]["launched_by_weclaw"] = True
            for _ in range(self._STARTUP_RETRY_COUNT):
                time.sleep(self._STARTUP_RETRY_DELAY_SECONDS)
                retried = self.detect(profile, runtime_state)
                retry_row = retried.to_dict()
                retry_row["pid"] = int(process.pid)
                retry_row["executable_path"] = executable_path
                retry_row["launched_by_weclaw"] = True
                runtime_state[profile.profile_id] = retry_row
                if retried.running:
                    return retried
            raise RuntimeError(
                "could not connect after starting the selected browser. Try closing the browser first, then launch again."
            )

        raise RuntimeError(
            "no browser program is configured yet. Detect a browser or choose a browser program, then launch again."
        )

    def _launch_browser_process(self, profile: BrowserProfile):
        command = [
            str(profile.executable_path),
            f"--remote-debugging-port={profile.cdp_port}",
            "--new-window",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        if str(profile.user_data_dir or "").strip():
            command.append(f"--user-data-dir={profile.user_data_dir}")
        if str(profile.profile_directory or "").strip():
            command.append(f"--profile-directory={profile.profile_directory}")
        command.append("about:blank")
        return subprocess.Popen(command)

    def stop(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        endpoint = build_cdp_endpoint(profile.cdp_url, profile.cdp_host, profile.cdp_port)
        row = dict(runtime_state.get(profile.profile_id) or {})
        pid = row.get("pid")
        if bool(row.get("launched_by_weclaw")) and isinstance(pid, int) and pid > 0:
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
            status="detached",
            cdp_url=endpoint,
            updated_at=_utc_now(),
            capabilities=compute_profile_capabilities(profile),
            transport="cdp-existing-session",
        )
        runtime_state[profile.profile_id] = status.to_dict()
        return status
