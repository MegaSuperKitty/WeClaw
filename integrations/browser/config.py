# -*- coding: utf-8 -*-
"""Browser configuration normalization."""

from __future__ import annotations

import os
from typing import Any, Dict

from .models import BrowserConfig, BrowserProfile


SUPPORTED_DRIVERS = {"managed", "user-identity", "existing-session", "remote-cdp"}


def _normalize_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _normalize_port(value: Any, default: int) -> int:
    try:
        port = int(value)
    except Exception:
        return default
    if 1 <= port <= 65535:
        return port
    return default


def _normalize_path(value: Any) -> str:
    text = str(value or "").strip()
    return os.path.abspath(text) if text else ""


def build_default_profile() -> BrowserProfile:
    return BrowserProfile(profile_id="managed-default", driver="managed", channel="chrome", cdp_port=18800)


def build_default_identity_profile() -> BrowserProfile:
    return BrowserProfile(
        profile_id="identity-default",
        driver="user-identity",
        channel="chrome",
        cdp_port=9222,
    )


def build_default_existing_profile() -> BrowserProfile:
    return BrowserProfile(
        profile_id="existing-default",
        driver="existing-session",
        channel="chrome",
        cdp_port=9222,
        attach_only=True,
    )


def load_browser_config(raw: Dict[str, Any] | None = None) -> BrowserConfig:
    payload = raw or {}
    install = payload.get("install") if isinstance(payload.get("install"), dict) else {}
    profiles_payload = payload.get("profiles") if isinstance(payload.get("profiles"), dict) else {}

    profiles: Dict[str, BrowserProfile] = {}
    for profile_id, item in profiles_payload.items():
        data = item if isinstance(item, dict) else {}
        driver = str(data.get("driver") or "managed").strip() or "managed"
        if driver not in SUPPORTED_DRIVERS:
            raise ValueError(f"unsupported browser driver: {driver}")
        profiles[str(profile_id)] = BrowserProfile(
            profile_id=str(profile_id),
            driver=driver,
            channel=str(data.get("channel") or "chrome").strip() or "chrome",
            executable_path=_normalize_path(data.get("executable_path")),
            user_data_dir=_normalize_path(data.get("user_data_dir")),
            profile_directory=str(data.get("profile_directory") or "").strip(),
            cdp_host=str(data.get("cdp_host") or "127.0.0.1").strip() or "127.0.0.1",
            cdp_port=_normalize_port(data.get("cdp_port"), 18800),
            cdp_url=str(data.get("cdp_url") or "").strip(),
            attach_only=_normalize_bool(data.get("attach_only"), driver in {"existing-session", "remote-cdp"}),
        )

    if "managed-default" not in profiles:
        managed_profile = build_default_profile()
        profiles[managed_profile.profile_id] = managed_profile
    if "identity-default" not in profiles:
        identity_profile = build_default_identity_profile()
        profiles[identity_profile.profile_id] = identity_profile
    if "existing-default" not in profiles:
        existing_profile = build_default_existing_profile()
        profiles[existing_profile.profile_id] = existing_profile

    default_profile_id = str(payload.get("default_profile") or "identity-default").strip() or "identity-default"
    if default_profile_id not in profiles:
        default_profile_id = "identity-default" if "identity-default" in profiles else "existing-default"

    return BrowserConfig(
        enabled=_normalize_bool(payload.get("enabled"), True),
        default_profile=default_profile_id,
        profiles=profiles,
        install_allow_managed_browser_install=_normalize_bool(
            install.get("allow_managed_browser_install"), True
        ),
        install_managed_browser_channel=str(install.get("managed_browser_channel") or "chromium").strip() or "chromium",
        install_prefer_system_browser=_normalize_bool(install.get("prefer_system_browser"), True),
        install_cache_dir=_normalize_path(install.get("cache_dir")),
    )
