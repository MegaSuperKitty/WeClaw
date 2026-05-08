# -*- coding: utf-8 -*-
"""Unified browser runtime adapter for tabs, snapshots, and screenshots."""

from __future__ import annotations

from typing import Dict

from .artifacts import BrowserArtifacts
from .cdp import (
    act_in_tab,
    BrowserCdpError,
    activate_tab,
    capture_tab_screenshot,
    capture_tab_snapshot,
    choose_tab,
    close_tab,
    list_page_tabs,
    open_new_tab,
)
from .models import BrowserProfile


class BrowserRuntime:
    """Expose one tool-facing surface across browser driver types."""

    def __init__(self, artifacts: BrowserArtifacts):
        self.artifacts = artifacts

    def list_tabs(self, profile: BrowserProfile) -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        tabs = list_page_tabs(endpoint)
        return {"success": True, "profile_id": profile.profile_id, "tabs": tabs}

    def open_tab(self, profile: BrowserProfile, *, url: str) -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        tab = open_new_tab(endpoint, url)
        return {"success": True, "profile_id": profile.profile_id, "tab": tab}

    def select_tab(self, profile: BrowserProfile, *, target_id: str) -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        activate_tab(endpoint, target_id)
        tabs = list_page_tabs(endpoint)
        tab = choose_tab(tabs, target_id)
        return {"success": True, "profile_id": profile.profile_id, "tab": tab, "tabs": tabs}

    def close_tab(self, profile: BrowserProfile, *, target_id: str) -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        tabs = list_page_tabs(endpoint)
        tab = choose_tab(tabs, target_id)
        close_tab(endpoint, str(tab.get("target_id") or ""))
        remaining_tabs = list_page_tabs(endpoint)
        return {"success": True, "profile_id": profile.profile_id, "closed_tab": tab, "tabs": remaining_tabs}

    def snapshot(self, profile: BrowserProfile, *, target_id: str = "") -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        tabs = list_page_tabs(endpoint)
        tab = choose_tab(tabs, target_id)
        payload = capture_tab_snapshot(str(tab.get("websocket_url") or ""))
        artifact = self.artifacts.save_snapshot(
            profile_id=profile.profile_id,
            tab_id=str(tab.get("target_id") or "page"),
            payload=payload,
        )
        return {
            "success": True,
            "profile_id": profile.profile_id,
            "tab": tab,
            "snapshot": payload,
            "artifact": artifact,
        }

    def screenshot(self, profile: BrowserProfile, *, target_id: str = "", full_page: bool = True) -> Dict[str, object]:
        endpoint = self._resolve_endpoint(profile)
        tabs = list_page_tabs(endpoint)
        tab = choose_tab(tabs, target_id)
        content = capture_tab_screenshot(str(tab.get("websocket_url") or ""), full_page=full_page)
        artifact = self.artifacts.save_screenshot(
            profile_id=profile.profile_id,
            tab_id=str(tab.get("target_id") or "page"),
            content=content,
        )
        return {
            "success": True,
            "profile_id": profile.profile_id,
            "tab": tab,
            "artifact": artifact,
        }

    def act(
        self,
        profile: BrowserProfile,
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
        endpoint = self._resolve_endpoint(profile)
        tabs = list_page_tabs(endpoint)
        tab = choose_tab(tabs, target_id)
        result = act_in_tab(
            str(tab.get("websocket_url") or ""),
            kind=kind,
            selector=selector,
            value=value,
            expression=expression,
            url=url,
            key=key,
            file_path=file_path,
            timeout_ms=timeout_ms,
        )
        return {
            "success": True,
            "profile_id": profile.profile_id,
            "tab": tab,
            "action": {
                "kind": kind,
                "selector": selector,
                "url": url,
                "key": key,
                "file_path": file_path,
                "timeout_ms": timeout_ms,
            },
            "result": result,
        }

    def _resolve_endpoint(self, profile: BrowserProfile) -> str:
        from .cdp import build_cdp_endpoint

        endpoint = build_cdp_endpoint(profile.cdp_url, profile.cdp_host, profile.cdp_port)
        if not endpoint:
            raise BrowserCdpError(f"profile {profile.profile_id} has no CDP endpoint configured")
        return endpoint
