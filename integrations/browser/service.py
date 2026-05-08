# -*- coding: utf-8 -*-
"""Browser runtime service exposed to the console."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

from core.workspace.layout import WorkspaceLayout, ensure_workspace_layout

from .artifacts import BrowserArtifacts
from .diagnostics import build_profile_diagnostics
from .drivers import ExistingSessionBrowserDriver, ManagedBrowserDriver, RemoteCdpBrowserDriver, UserIdentityBrowserDriver
from .identity import (
    browser_display_name,
    detect_browser_family,
    infer_user_data_dir,
    list_profile_directories,
    normalize_local_path,
    recommend_profile_directory,
)
from .install_manager import BrowserInstallManager
from .profiles import BrowserProfileManager
from .runtime import BrowserRuntime
from .session_store import BrowserSessionStore


class BrowserService:
    """Coordinate browser profiles, runtime state, and install state."""

    def __init__(self, workspace_root: str, source_root: str):
        self.layout: WorkspaceLayout = ensure_workspace_layout(workspace_root, source_root=source_root)
        self.store = BrowserSessionStore(self.layout)
        self.install_manager = BrowserInstallManager(self.store)
        self.profile_manager = BrowserProfileManager(self.store)
        self.artifacts = BrowserArtifacts(self.store)
        self.runtime = BrowserRuntime(self.artifacts)
        self.runtime_state = self.store.load_runtime_state()
        self.runtime_state.setdefault("profiles", {})
        self.drivers = {
            "managed": ManagedBrowserDriver(self.install_manager),
            "user-identity": UserIdentityBrowserDriver(),
            "existing-session": ExistingSessionBrowserDriver(),
            "remote-cdp": RemoteCdpBrowserDriver(),
        }
        self.refresh_install_detection()

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _profile_runtime_rows(self) -> Dict[str, Dict[str, object]]:
        profiles = self.runtime_state.setdefault("profiles", {})
        return profiles if isinstance(profiles, dict) else {}

    def _persist_runtime_state(self) -> None:
        self.store.save_runtime_state(self.runtime_state)

    def _session_binding_row(self) -> Dict[str, object]:
        row = self.runtime_state.setdefault("session_binding", {})
        return row if isinstance(row, dict) else {}

    def _user_config_row(self) -> Dict[str, object]:
        row = self.runtime_state.setdefault("user_config", {})
        if not isinstance(row, dict):
            row = {}
            self.runtime_state["user_config"] = row
        return row

    def _update_session_binding(self, *, profile_id: str = "", session_id: str | None = None, tab_id: str = "") -> None:
        row = self._session_binding_row()
        if profile_id:
            row["profile_id"] = profile_id
        if session_id is not None:
            row["session_id"] = session_id
        row["tab_id"] = str(tab_id or "")
        self._persist_runtime_state()

    def refresh_install_detection(self) -> Dict[str, object]:
        self.install_manager.detect_system_browsers()
        return self.get_install_status()

    def _mode_to_profile_id(self, mode: str) -> str:
        if mode == "use_existing_browser":
            return "identity-default"
        if mode in {"auto_prepare_browser", "use_fresh_browser"}:
            return "managed-default"
        return self.get_default_profile_id()

    def _profile_to_mode(self, profile_id: str) -> str:
        if profile_id in {"identity-default", "existing-default"}:
            return "use_existing_browser"
        if profile_id == "managed-default":
            return "auto_prepare_browser"
        return "use_existing_browser"

    def _default_user_config(self) -> Dict[str, object]:
        install = self.install_manager.get_state()
        preferred_executable = self.install_manager.get_preferred_executable()
        profile_id = self.get_default_profile_id()
        profile = self.profile_manager.get_profile(profile_id)
        selected_mode = self._profile_to_mode(profile_id)
        browser_family = detect_browser_family(str(profile.executable_path or preferred_executable or ""))
        return {
            "selected_mode": selected_mode,
            "last_connected_mode": "",
            "last_profile_id": profile_id,
            "browser_executable_path": str(profile.executable_path or preferred_executable or ""),
            "browser_family": browser_family,
            "user_data_dir": str(profile.user_data_dir or ""),
            "profile_directory": str(profile.profile_directory or ""),
            "remote_debugging_port": int(profile.cdp_port or (9222 if profile.driver in {"existing-session", "user-identity"} else 18800)),
            "preferred_browser_name": str(browser_display_name(browser_family) or (install.system_browsers[0].get("name") if install.system_browsers else "") or ""),
            "discovered_profiles": [],
            "selected_profile_label": "",
            "launch_profile_source": "",
            "launch_user_data_dir": "",
            "launch_profile_directory": "",
            "launch_window_mode": "",
            "last_launch_strategy": "",
            "last_connected_at": "",
            "status": "configured",
            "last_error": "",
        }

    def _normalized_user_config(self) -> Dict[str, object]:
        raw = self._user_config_row()
        merged = {**self._default_user_config(), **dict(raw)}
        mode = str(merged.get("selected_mode") or "use_existing_browser").strip() or "use_existing_browser"
        if mode not in {"use_existing_browser", "auto_prepare_browser", "use_fresh_browser"}:
            mode = "use_existing_browser"
        merged["selected_mode"] = mode
        merged["last_profile_id"] = str(merged.get("last_profile_id") or self._mode_to_profile_id(mode)).strip() or self._mode_to_profile_id(mode)
        merged["browser_executable_path"] = str(merged.get("browser_executable_path") or "").strip()
        merged["browser_family"] = str(merged.get("browser_family") or "").strip()
        merged["user_data_dir"] = str(merged.get("user_data_dir") or "").strip()
        merged["profile_directory"] = str(merged.get("profile_directory") or "").strip()
        merged["preferred_browser_name"] = str(merged.get("preferred_browser_name") or "").strip()
        discovered_profiles = merged.get("discovered_profiles") or []
        merged["discovered_profiles"] = list(discovered_profiles) if isinstance(discovered_profiles, list) else []
        merged["selected_profile_label"] = str(merged.get("selected_profile_label") or "").strip()
        merged["launch_profile_source"] = str(merged.get("launch_profile_source") or "").strip()
        merged["launch_user_data_dir"] = str(merged.get("launch_user_data_dir") or "").strip()
        merged["launch_profile_directory"] = str(merged.get("launch_profile_directory") or "").strip()
        merged["launch_window_mode"] = str(merged.get("launch_window_mode") or "").strip()
        merged["last_launch_strategy"] = str(merged.get("last_launch_strategy") or "").strip()
        merged["last_connected_mode"] = str(merged.get("last_connected_mode") or "").strip()
        merged["last_connected_at"] = str(merged.get("last_connected_at") or "").strip()
        merged["status"] = str(merged.get("status") or "configured").strip() or "configured"
        merged["last_error"] = str(merged.get("last_error") or "").strip()
        try:
            port = int(merged.get("remote_debugging_port") or 0)
        except Exception:
            port = 0
        if not (1 <= port <= 65535):
            port = 9222 if mode == "use_existing_browser" else 18800
        merged["remote_debugging_port"] = port
        return merged

    def _resolve_browser_identity(self, payload: Dict[str, object]) -> Dict[str, object]:
        executable_path = normalize_local_path(str(payload.get("browser_executable_path") or ""))
        browser_family = detect_browser_family(executable_path)
        preferred_browser_name = str(payload.get("preferred_browser_name") or "").strip() or browser_display_name(browser_family)
        user_data_dir = normalize_local_path(str(payload.get("user_data_dir") or "")) or infer_user_data_dir(browser_family)
        discovered_profiles = list_profile_directories(user_data_dir)
        requested_profile = str(payload.get("profile_directory") or "").strip()
        if requested_profile and any(str(item.get("id") or "") == requested_profile for item in discovered_profiles):
            profile_directory = requested_profile
        else:
            profile_directory = recommend_profile_directory(discovered_profiles) or requested_profile
        selected_profile_label = ""
        for item in discovered_profiles:
            if str(item.get("id") or "") == profile_directory:
                selected_profile_label = str(item.get("label") or profile_directory)
                break
        launch_profile_source = "selected_browser_profile"
        launch_user_data_dir = user_data_dir
        launch_profile_directory = profile_directory
        return {
            **dict(payload),
            "browser_executable_path": executable_path,
            "browser_family": browser_family,
            "preferred_browser_name": preferred_browser_name,
            "user_data_dir": user_data_dir,
            "profile_directory": profile_directory,
            "discovered_profiles": discovered_profiles,
            "selected_profile_label": selected_profile_label,
            "launch_profile_source": launch_profile_source,
            "launch_user_data_dir": launch_user_data_dir,
            "launch_profile_directory": launch_profile_directory,
        }

    def _save_user_config(self, payload: Dict[str, object]) -> Dict[str, object]:
        base = self._normalized_user_config()
        row = self._user_config_row()
        normalized = dict(base)
        if payload:
            normalized.update(dict(payload))
        normalized = self._resolve_browser_identity(normalized)
        row.clear()
        row.update(normalized)
        normalized = self._normalized_user_config()
        row.clear()
        row.update(normalized)
        self._persist_runtime_state()
        return normalized

    def _resolve_launch_window_mode(self, mode: str, profile_id: str) -> str:
        row = dict(self._profile_runtime_rows().get(profile_id) or {})
        if mode == "use_existing_browser":
            if profile_id == "identity-default":
                if bool(row.get("browser_running_before_launch")):
                    return "dedicated_window_requested_with_merge_warning"
                return "dedicated_window_requested"
            if bool(row.get("launched_by_weclaw")):
                if bool(row.get("browser_running_before_launch")):
                    return "dedicated_window_requested_with_merge_warning"
                return "dedicated_window_requested"
            return "attached_existing_window"
        return "dedicated_window_requested"

    def get_user_config(self) -> Dict[str, object]:
        config = self._save_user_config({})
        selected_mode = str(config.get("selected_mode") or "use_existing_browser")
        active_profile_id = str(self._session_binding_row().get("profile_id") or config.get("last_profile_id") or self._mode_to_profile_id(selected_mode))
        active_profile = self.profile_manager.get_profile(active_profile_id)
        active_status = self.get_profile_status(active_profile_id)
        install = self.get_install_status()
        status_name = str(config.get("status") or "configured")
        binding_profile_id = str(self._session_binding_row().get("profile_id") or "").strip()
        has_active_binding = bool(binding_profile_id) and binding_profile_id == active_profile_id
        if status_name not in {"failed", "needs_user_action"} and (status_name == "connected" or (active_status.get("running") and has_active_binding)):
            status_name = "connected"
        summary = {
            "selected_mode": selected_mode,
            "status": status_name,
            "last_connected_mode": str(config.get("last_connected_mode") or ""),
            "last_profile_id": str(config.get("last_profile_id") or active_profile_id),
            "browser_executable_path": str(config.get("browser_executable_path") or active_profile.executable_path or ""),
            "browser_family": str(config.get("browser_family") or ""),
            "user_data_dir": str(config.get("user_data_dir") or active_profile.user_data_dir or ""),
            "profile_directory": str(config.get("profile_directory") or active_profile.profile_directory or ""),
            "remote_debugging_port": int(config.get("remote_debugging_port") or active_profile.cdp_port or 0),
            "preferred_browser_name": str(config.get("preferred_browser_name") or ""),
            "discovered_profiles": list(config.get("discovered_profiles") or []),
            "selected_profile_label": str(config.get("selected_profile_label") or ""),
            "launch_profile_source": str(config.get("launch_profile_source") or ""),
            "launch_user_data_dir": str(config.get("launch_user_data_dir") or ""),
            "launch_profile_directory": str(config.get("launch_profile_directory") or ""),
            "launch_window_mode": str(config.get("launch_window_mode") or ""),
            "last_launch_strategy": str(config.get("last_launch_strategy") or ""),
            "last_connected_at": str(config.get("last_connected_at") or ""),
            "last_error": str(config.get("last_error") or active_status.get("last_error") or ""),
            "active_profile_id": active_profile_id,
            "active_profile_driver": active_profile.driver,
            "connection_status": str(active_status.get("status") or "idle"),
            "connected": bool(active_status.get("running")),
            "binding": dict(self._session_binding_row()),
            "install": install,
        }
        return {"success": True, "config": summary}

    def set_user_config(self, payload: Dict[str, object]) -> Dict[str, object]:
        merged = dict(self._normalized_user_config())
        merged.update(dict(payload or {}))
        mode = str(merged.get("selected_mode") or "use_existing_browser").strip() or "use_existing_browser"
        if mode not in {"use_existing_browser", "auto_prepare_browser", "use_fresh_browser"}:
            raise ValueError(f"unsupported browser user mode: {mode}")
        merged["selected_mode"] = mode
        merged["last_profile_id"] = self._mode_to_profile_id(mode)
        if not str(merged.get("status") or "").strip():
            merged["status"] = "configured"
        if mode == "use_existing_browser" and not merged.get("remote_debugging_port"):
            merged["remote_debugging_port"] = 9222
        if mode != "use_existing_browser" and not merged.get("remote_debugging_port"):
            merged["remote_debugging_port"] = 18800
        self._save_user_config(merged)
        return self.get_user_config()

    def refresh_user_browser_identity(self, payload: Dict[str, object] | None = None) -> Dict[str, object]:
        config = self._normalized_user_config()
        config.update(dict(payload or {}))
        self._save_user_config(config)
        return self.get_user_config()

    def choose_browser_executable(self) -> Dict[str, object]:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception as exc:
            raise RuntimeError(f"native browser picker is unavailable: {exc}") from exc

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            file_path = filedialog.askopenfilename(
                title="Choose Browser Program",
                filetypes=[("Browser Programs", "*.exe"), ("All Files", "*.*")],
            )
        finally:
            root.destroy()
        selected_path = normalize_local_path(file_path)
        if not selected_path:
            raise RuntimeError("browser program selection was canceled")
        return self.refresh_user_browser_identity({"browser_executable_path": selected_path})

    def _apply_mode_profile_config(self, mode: str, config: Dict[str, object]) -> Dict[str, object]:
        profile_id = self._mode_to_profile_id(mode)
        profile = self.profile_manager.get_profile(profile_id)
        install = self.install_manager.get_state()
        preferred_executable = str(config.get("browser_executable_path") or self.install_manager.get_preferred_executable() or "")
        preferred_port = int(config.get("remote_debugging_port") or (9222 if mode == "use_existing_browser" else 18800))
        update_payload: Dict[str, object] = {
            "profile_id": profile.profile_id,
            "driver": profile.driver,
            "channel": profile.channel,
            "executable_path": preferred_executable,
            "user_data_dir": str(config.get("launch_user_data_dir") or config.get("user_data_dir") or profile.user_data_dir or ""),
            "profile_directory": str(config.get("launch_profile_directory") or config.get("profile_directory") or profile.profile_directory or ""),
            "cdp_host": profile.cdp_host,
            "cdp_port": preferred_port,
            "cdp_url": profile.cdp_url,
            "attach_only": profile.attach_only,
        }
        launch_strategy = ""
        if mode == "use_existing_browser":
            update_payload["driver"] = "user-identity"
            update_payload["attach_only"] = False
            launch_strategy = "user-identity-relaunch"
        elif mode == "auto_prepare_browser":
            update_payload["driver"] = "managed"
            update_payload["attach_only"] = False
            if not update_payload["user_data_dir"]:
                update_payload["user_data_dir"] = self.store.profile_runtime_user_dir("managed-default")
            launch_strategy = "system-browser" if install.system_browsers else "managed-install"
        else:
            update_payload["driver"] = "managed"
            update_payload["attach_only"] = False
            update_payload["user_data_dir"] = str(config.get("user_data_dir") or self.store.profile_runtime_user_dir("fresh-browser"))
            launch_strategy = "fresh-managed-profile"
        updated = self.update_profile(profile_id, update_payload)
        return {"profile_id": profile_id, "launch_strategy": launch_strategy, "profile": updated}

    def launch_browser(self, payload: Dict[str, object] | None = None) -> Dict[str, object]:
        next_config = dict(self._normalized_user_config())
        next_config.update(dict(payload or {}))
        mode = str(next_config.get("selected_mode") or "use_existing_browser").strip() or "use_existing_browser"
        next_config["selected_mode"] = mode
        next_config["status"] = "starting"
        next_config["last_error"] = ""
        self._save_user_config(next_config)
        applied = self._apply_mode_profile_config(mode, next_config)
        profile_id = str(applied["profile_id"])
        try:
            status = self.start_profile(profile_id)
            launch_window_mode = self._resolve_launch_window_mode(mode, profile_id)
            final_config = {
                **next_config,
                "last_profile_id": profile_id,
                "last_connected_mode": mode,
                "launch_window_mode": launch_window_mode,
                "last_launch_strategy": str(applied["launch_strategy"] or ""),
                "last_connected_at": self._utc_now(),
                "status": "connected" if status.get("running") else "needs_user_action",
                "last_error": str(status.get("last_error") or ""),
                "browser_executable_path": str(applied["profile"].get("executable_path") or next_config.get("browser_executable_path") or ""),
                "user_data_dir": str(applied["profile"].get("user_data_dir") or next_config.get("user_data_dir") or ""),
                "profile_directory": str(applied["profile"].get("profile_directory") or next_config.get("profile_directory") or ""),
                "remote_debugging_port": int(applied["profile"].get("cdp_port") or next_config.get("remote_debugging_port") or 0),
            }
            self._save_user_config(final_config)
            return {
                "success": True,
                "mode": mode,
                "profile_id": profile_id,
                "launch_strategy": applied["launch_strategy"],
                "status": status,
                "config": self.get_user_config()["config"],
            }
        except Exception as exc:
            self.set_session_binding({})
            failure_config = {
                **next_config,
                "last_profile_id": profile_id,
                "last_connected_mode": "",
                "last_launch_strategy": str(applied["launch_strategy"] or ""),
                "last_connected_at": "",
                "launch_window_mode": "",
                "status": "failed",
                "last_error": str(exc),
            }
            self._save_user_config(failure_config)
            raise

    def disconnect_browser(self) -> Dict[str, object]:
        config = self._normalized_user_config()
        binding = self._session_binding_row()
        profile_id = str(binding.get("profile_id") or config.get("last_profile_id") or self._mode_to_profile_id(str(config.get("selected_mode") or "")))
        status = self.stop_profile(profile_id)
        binding.clear()
        self._save_user_config(
            {
                **config,
                "last_profile_id": profile_id,
                "status": "configured",
                "launch_window_mode": "",
                "last_error": "",
            }
        )
        return {
            "success": True,
            "profile_id": profile_id,
            "status": status,
            "config": self.get_user_config()["config"],
        }

    def list_profiles(self) -> List[Dict[str, object]]:
        rows = []
        runtime_rows = self._profile_runtime_rows()
        install_state = self.install_manager.get_state()
        for profile in self.profile_manager.list_profiles():
            status = self.drivers[profile.driver].detect(profile, runtime_rows)
            status.diagnostics = build_profile_diagnostics(profile, status, install_state)
            rows.append({**profile.to_dict(), "status": status.to_dict()})
        return rows

    def create_profile(self, payload: Dict[str, object]) -> Dict[str, object]:
        profile = self.profile_manager.create_profile(payload)
        return {**profile.to_dict(), "status": self.get_profile_status(profile.profile_id)}

    def update_profile(self, profile_id: str, payload: Dict[str, object]) -> Dict[str, object]:
        profile = self.profile_manager.update_profile(profile_id, payload)
        return {**profile.to_dict(), "status": self.get_profile_status(profile.profile_id)}

    def delete_profile(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        runtime_rows.pop(str(profile_id or "").strip(), None)
        self.profile_manager.delete_profile(profile_id)
        self._persist_runtime_state()
        return {"success": True, "deleted_profile_id": str(profile_id or "").strip()}

    def set_default_profile(self, profile_id: str) -> Dict[str, object]:
        profile = self.profile_manager.set_default_profile(profile_id)
        return {"success": True, "default_profile": profile.profile_id}

    def get_profile_status(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        install_state = self.install_manager.get_state()
        profile = self.profile_manager.get_profile(profile_id)
        status = self.drivers[profile.driver].detect(profile, runtime_rows)
        status.diagnostics = build_profile_diagnostics(profile, status, install_state)
        runtime_rows[profile.profile_id] = status.to_dict()
        self._persist_runtime_state()
        return status.to_dict()

    def _profile(self, profile_id: str):
        return self.profile_manager.get_profile(profile_id)

    def start_profile(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        profile = self._profile(profile_id)
        status = self.drivers[profile.driver].start(profile, runtime_rows)
        install_state = self.install_manager.get_state()
        status.diagnostics = build_profile_diagnostics(profile, status, install_state)
        runtime_rows[profile.profile_id] = status.to_dict()
        binding = self._session_binding_row()
        if not str(binding.get("profile_id") or "").strip() or str(binding.get("profile_id") or "").strip() == profile.profile_id:
            self._update_session_binding(
                profile_id=profile.profile_id,
                session_id=str(binding.get("session_id") or ""),
                tab_id=str(status.active_tab_id or ""),
            )
        else:
            self._persist_runtime_state()
        return status.to_dict()

    def stop_profile(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        profile = self._profile(profile_id)
        status = self.drivers[profile.driver].stop(profile, runtime_rows)
        install_state = self.install_manager.get_state()
        status.diagnostics = build_profile_diagnostics(profile, status, install_state)
        runtime_rows[profile.profile_id] = status.to_dict()
        self._persist_runtime_state()
        return status.to_dict()

    def diagnose_profile(self, profile_id: str) -> Dict[str, object]:
        return self.get_profile_status(profile_id)

    def reset_profile(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        profile = self._profile(profile_id)
        try:
            self.drivers[profile.driver].stop(profile, runtime_rows)
        except Exception:
            pass
        runtime_rows.pop(profile.profile_id, None)
        self._persist_runtime_state()
        return self.get_profile_status(profile.profile_id)

    def reconnect_profile(self, profile_id: str) -> Dict[str, object]:
        runtime_rows = self._profile_runtime_rows()
        profile = self._profile(profile_id)
        status = self.drivers[profile.driver].start(profile, runtime_rows)
        install_state = self.install_manager.get_state()
        status.diagnostics = build_profile_diagnostics(profile, status, install_state)
        runtime_rows[profile.profile_id] = status.to_dict()
        binding = self._session_binding_row()
        self._update_session_binding(
            profile_id=profile.profile_id,
            session_id=str(binding.get("session_id") or ""),
            tab_id=str(status.active_tab_id or ""),
        )
        return status.to_dict()

    def list_profile_tabs(self, profile_id: str) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.list_tabs(profile)
        status = self.get_profile_status(profile_id)
        payload["status"] = status
        return payload

    def open_profile_tab(self, profile_id: str, url: str) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.open_tab(profile, url=url)
        payload["status"] = self.get_profile_status(profile_id)
        return payload

    def select_profile_tab(self, profile_id: str, target_id: str) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.select_tab(profile, target_id=target_id)
        self.set_session_binding({"profile_id": profile_id, "tab_id": target_id, "session_id": self._session_binding_row().get("session_id", "")})
        payload["status"] = self.get_profile_status(profile_id)
        return payload

    def close_profile_tab(self, profile_id: str, target_id: str) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.close_tab(profile, target_id=target_id)
        binding = self._session_binding_row()
        if str(binding.get("profile_id") or "") == profile_id and str(binding.get("tab_id") or "") == target_id:
            binding["tab_id"] = ""
            self._persist_runtime_state()
        payload["status"] = self.get_profile_status(profile_id)
        return payload

    def snapshot_profile(self, profile_id: str, target_id: str = "") -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.snapshot(profile, target_id=target_id)
        binding = self._session_binding_row()
        self._update_session_binding(
            profile_id=profile_id,
            session_id=str(binding.get("session_id") or ""),
            tab_id=str(payload.get("tab", {}).get("target_id") or ""),
        )
        self.get_profile_status(profile_id)
        return payload

    def screenshot_profile(self, profile_id: str, target_id: str = "", full_page: bool = True) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.screenshot(profile, target_id=target_id, full_page=full_page)
        binding = self._session_binding_row()
        self._update_session_binding(
            profile_id=profile_id,
            session_id=str(binding.get("session_id") or ""),
            tab_id=str(payload.get("tab", {}).get("target_id") or ""),
        )
        self.get_profile_status(profile_id)
        return payload

    def act_profile(
        self,
        profile_id: str,
        *,
        target_id: str = "",
        kind: str = "",
        selector: str = "",
        value: str = "",
        expression: str = "",
        url: str = "",
        key: str = "",
        file_path: str = "",
        timeout_ms: int = 0,
    ) -> Dict[str, object]:
        profile = self._profile(profile_id)
        payload = self.runtime.act(
            profile,
            target_id=target_id,
            kind=kind,
            selector=selector,
            value=value,
            expression=expression,
            url=url,
            key=key,
            file_path=file_path,
            timeout_ms=timeout_ms,
        )
        binding = self._session_binding_row()
        self._update_session_binding(
            profile_id=profile_id,
            session_id=str(binding.get("session_id") or ""),
            tab_id=str(target_id or payload.get("tab", {}).get("target_id", "")),
        )
        self.get_profile_status(profile_id)
        return payload

    def list_recent_captures(self, *, kind: str = "", profile_id: str = "", limit: int = 10) -> List[Dict[str, object]]:
        return self.artifacts.list_recent(limit=limit, kind=kind, profile_id=profile_id)

    def get_install_status(self) -> Dict[str, object]:
        return self.install_manager.get_state().to_dict()

    def get_default_profile_id(self) -> str:
        return str(self.profile_manager.config.default_profile or "managed-default")

    def install_managed_browser(self) -> Dict[str, object]:
        state = self.install_manager.install_managed_browser()
        return state.to_dict()

    def cancel_install(self) -> Dict[str, object]:
        return self.install_manager.cancel_install().to_dict()

    def remove_managed_browser(self) -> Dict[str, object]:
        return self.install_manager.remove_managed_browser().to_dict()

    def reinstall_managed_browser(self) -> Dict[str, object]:
        return self.install_manager.reinstall_managed_browser().to_dict()

    def get_session_binding(self) -> Dict[str, object]:
        return {"success": True, "binding": dict(self._session_binding_row())}

    def set_session_binding(self, payload: Dict[str, object]) -> Dict[str, object]:
        row = self._session_binding_row()
        row.clear()
        row.update(dict(payload or {}))
        self._persist_runtime_state()
        return {"success": True, "binding": dict(row)}

    def get_artifacts(self, *, kind: str = "", profile_id: str = "", limit: int = 20) -> Dict[str, object]:
        return {
            "success": True,
            "captures": self.list_recent_captures(kind=kind, profile_id=profile_id, limit=limit),
        }

    def get_status(self) -> Dict[str, object]:
        return {
            "success": True,
            "workspace_browser_root": str(Path(self.layout.browser_root).resolve()),
            "default_profile": self.profile_manager.config.default_profile,
            "profiles": self.list_profiles(),
            "install": self.get_install_status(),
            "recent_captures": self.list_recent_captures(),
            "session_binding": dict(self._session_binding_row()),
            "user_config": self.get_user_config()["config"],
        }
