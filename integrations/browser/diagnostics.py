# -*- coding: utf-8 -*-
"""Diagnostics helpers for browser profiles."""

from __future__ import annotations

import os
from typing import Dict, List

from .models import BrowserInstallState, BrowserProfile, BrowserProfileStatus


def build_profile_diagnostics(
    profile: BrowserProfile,
    status: BrowserProfileStatus,
    install_state: BrowserInstallState,
) -> List[Dict[str, str]]:
    diagnostics: List[Dict[str, str]] = []

    diagnostics.append({"key": "driver", "level": "info", "summary": f"driver={profile.driver}"})

    if profile.driver in {"managed", "user-identity"}:
        executable = status.executable_path or profile.executable_path or install_state.installed_executable_path
        if executable and os.path.isfile(executable):
            diagnostics.append({"key": "browser_executable", "level": "info", "summary": f"browser executable ready: {executable}"})
        else:
            diagnostics.append({"key": "browser_executable", "level": "error", "summary": "browser executable missing"})

        if profile.user_data_dir and os.path.isdir(profile.user_data_dir):
            diagnostics.append({"key": "user_data_dir", "level": "info", "summary": f"user data dir ready: {profile.user_data_dir}"})
        else:
            diagnostics.append({"key": "user_data_dir", "level": "warn", "summary": "user data dir missing"})

        if profile.driver == "managed" and install_state.offer_install:
            diagnostics.append(
                {
                    "key": "install_fallback",
                    "level": "warn",
                    "summary": "no system Chromium browser detected; managed install available",
                }
            )
        elif profile.driver == "managed" and install_state.installed_executable_path:
            diagnostics.append(
                {
                    "key": "install_fallback",
                    "level": "info",
                    "summary": f"managed Chromium installed: {install_state.installed_executable_path}",
                }
            )
        if profile.driver == "user-identity":
            diagnostics.append(
                {
                    "key": "launch_endpoint",
                    "level": "info" if status.cdp_url else "warn",
                    "summary": f"launch endpoint: {status.cdp_url or 'missing'}",
                }
            )
            diagnostics.append(
                {
                    "key": "launch_state",
                    "level": "info" if status.running else "warn",
                    "summary": "user identity browser ready" if status.running else "waiting for WeClaw browser work window",
                }
            )

    if profile.driver == "existing-session":
        diagnostics.append(
            {
                "key": "attach_endpoint",
                "level": "info" if status.cdp_url else "warn",
                "summary": f"attach endpoint: {status.cdp_url or 'missing'}",
            }
        )
        diagnostics.append(
            {
                "key": "attach_state",
                "level": "info" if status.running else "warn",
                "summary": "existing browser session attached" if status.running else "waiting for remote debugging browser session",
            }
        )
        diagnostics.append(
            {
                "key": "tabs",
                "level": "info" if status.tabs else "warn",
                "summary": f"attachable tabs: {len(status.tabs)}",
            }
        )

    if profile.driver == "remote-cdp":
        diagnostics.append(
            {
                "key": "cdp_url",
                "level": "info" if status.cdp_url else "error",
                "summary": f"remote cdp endpoint: {status.cdp_url or 'missing'}",
            }
        )
        diagnostics.append(
            {
                "key": "reachability",
                "level": "info" if status.running else "warn",
                "summary": "remote cdp reachable" if status.running else "remote cdp endpoint unreachable",
            }
        )
        diagnostics.append(
            {
                "key": "tabs",
                "level": "info" if status.tabs else "warn",
                "summary": f"attachable tabs: {len(status.tabs)}",
            }
        )

    if status.last_error:
        diagnostics.append({"key": "last_error", "level": "error", "summary": status.last_error})

    return diagnostics
