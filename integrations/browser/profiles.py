# -*- coding: utf-8 -*-
"""Browser profile management."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from .config import load_browser_config
from .models import BrowserConfig, BrowserProfile
from .session_store import BrowserSessionStore


def compute_profile_capabilities(profile: BrowserProfile) -> Dict[str, bool]:
    driver = profile.driver
    return {
        "supports_start": driver in {"managed", "user-identity"},
        "supports_stop": driver in {"managed", "user-identity"},
        "supports_reset": driver in {"managed", "user-identity"},
        "supports_attach": driver in {"existing-session", "remote-cdp"},
        "supports_playwright_overlay": driver in {"managed", "user-identity"},
        "supports_existing_tabs": driver in {"user-identity", "existing-session", "remote-cdp"},
        "supports_install_fallback": driver == "managed",
        "supports_reconnect": driver in {"existing-session", "remote-cdp"},
        "supports_tabs": True,
        "supports_snapshot": True,
        "supports_screenshot": True,
        "supports_act": True,
    }


class BrowserProfileManager:
    """Load and persist browser profile definitions."""

    def __init__(self, store: BrowserSessionStore):
        self.store = store
        self.config = self._load_config()

    def _load_config(self) -> BrowserConfig:
        raw = self.store.load_profiles_payload()
        if raw:
            return load_browser_config(raw)
        config = load_browser_config({})
        self.store.save_profiles_payload(config.to_dict())
        return config

    def save(self) -> None:
        self.store.save_profiles_payload(self.config.to_dict())

    def list_profiles(self) -> Iterable[BrowserProfile]:
        return list(self.config.profiles.values())

    def get_profile(self, profile_id: str) -> BrowserProfile:
        target = str(profile_id or "").strip() or self.config.default_profile
        profile = self.config.profiles.get(target)
        if profile is None:
            raise KeyError(f"browser profile not found: {target}")
        if profile.driver == "managed" and not profile.user_data_dir:
            profile.user_data_dir = self.store.profile_runtime_user_dir(profile.profile_id)
        return profile

    def get_default_profile(self) -> BrowserProfile:
        return self.get_profile(self.config.default_profile)

    def create_profile(self, payload: Dict[str, Any]) -> BrowserProfile:
        profile = self._build_profile(payload)
        if profile.profile_id in self.config.profiles:
            raise ValueError(f"browser profile already exists: {profile.profile_id}")
        self.config.profiles[profile.profile_id] = profile
        self.save()
        return self.get_profile(profile.profile_id)

    def update_profile(self, profile_id: str, payload: Dict[str, Any]) -> BrowserProfile:
        current = self.get_profile(profile_id)
        merged = current.to_dict()
        for key, value in dict(payload or {}).items():
            if key == "profile_id":
                continue
            merged[key] = value
        merged["profile_id"] = current.profile_id
        profile = self._build_profile(merged)
        self.config.profiles[current.profile_id] = profile
        self.save()
        return self.get_profile(profile.profile_id)

    def delete_profile(self, profile_id: str) -> None:
        target = str(profile_id or "").strip()
        if not target or target not in self.config.profiles:
            raise KeyError(f"browser profile not found: {target}")
        if target in {"managed-default", "identity-default", "existing-default"}:
            raise ValueError(f"browser profile is protected: {target}")
        del self.config.profiles[target]
        if self.config.default_profile == target:
            if "identity-default" in self.config.profiles:
                self.config.default_profile = "identity-default"
            elif "existing-default" in self.config.profiles:
                self.config.default_profile = "existing-default"
            else:
                self.config.default_profile = "managed-default"
        self.save()

    def set_default_profile(self, profile_id: str) -> BrowserProfile:
        profile = self.get_profile(profile_id)
        self.config.default_profile = profile.profile_id
        self.save()
        return profile

    def _build_profile(self, payload: Dict[str, Any]) -> BrowserProfile:
        config = load_browser_config(
            {
                "default_profile": "identity-default",
                "profiles": {
                    str(payload.get("profile_id") or "").strip() or "profile": payload,
                },
            }
        )
        return next(iter(config.profiles.values()))
