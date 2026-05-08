# -*- coding: utf-8 -*-
"""Dataclasses shared by the browser runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


INSTALL_PENDING = "pending"
INSTALL_INSTALLING = "installing"
INSTALL_INSTALLED = "installed"
INSTALL_FAILED = "failed"


@dataclass
class BrowserProfile:
    profile_id: str
    driver: str = "managed"
    channel: str = "chrome"
    executable_path: str = ""
    user_data_dir: str = ""
    profile_directory: str = ""
    cdp_host: str = "127.0.0.1"
    cdp_port: int = 18800
    cdp_url: str = ""
    attach_only: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrowserProfileStatus:
    profile_id: str
    driver: str
    running: bool = False
    status: str = "idle"
    pid: int | None = None
    executable_path: str = ""
    cdp_url: str = ""
    last_error: str = ""
    updated_at: str = ""
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: Dict[str, bool] = field(default_factory=dict)
    transport: str = ""
    tabs: List[Dict[str, Any]] = field(default_factory=list)
    active_tab_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrowserInstallState:
    status: str = INSTALL_PENDING
    platform: str = ""
    cache_dir: str = ""
    installed_executable_path: str = ""
    installed_browser_name: str = ""
    installed_at: str = ""
    last_error: str = ""
    system_browsers: List[Dict[str, str]] = field(default_factory=list)
    offer_install: bool = False
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrowserConfig:
    enabled: bool = True
    default_profile: str = "managed-default"
    profiles: Dict[str, BrowserProfile] = field(default_factory=dict)
    install_allow_managed_browser_install: bool = True
    install_managed_browser_channel: str = "chromium"
    install_prefer_system_browser: bool = True
    install_cache_dir: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "default_profile": self.default_profile,
            "profiles": {key: profile.to_dict() for key, profile in self.profiles.items()},
            "install": {
                "allow_managed_browser_install": self.install_allow_managed_browser_install,
                "managed_browser_channel": self.install_managed_browser_channel,
                "prefer_system_browser": self.install_prefer_system_browser,
                "cache_dir": self.install_cache_dir,
            },
        }
