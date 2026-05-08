# -*- coding: utf-8 -*-
"""Browser local MCP tools backed by the browser runtime service."""

from __future__ import annotations

import json

from integrations.mcp.openai_tool import Tool


class _BrowserToolBase(Tool):
    """Share browser service lookup and profile selection helpers."""

    def __init__(self, *, name: str, description: str, target):
        self._target = target
        super().__init__(
            name=name,
            description=description,
            parameters={
                "type": "object",
                "properties": {
                    "profile_id": {
                        "type": "string",
                        "description": "Optional browser profile id. Defaults to the runtime default profile.",
                    },
                "target_id": {
                    "type": "string",
                    "description": "Optional browser tab target id for snapshot or screenshot actions.",
                },
                    "url": {
                        "type": "string",
                        "description": "URL used when opening a new browser tab.",
                    },
                    "kind": {
                        "type": "string",
                        "description": "Browser action kind such as navigate, evaluate, click, or fill.",
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector used by click or fill actions.",
                    },
                    "value": {
                        "type": "string",
                        "description": "Value used by fill actions.",
                    },
                    "expression": {
                        "type": "string",
                        "description": "JavaScript expression used by evaluate actions.",
                    },
                    "key": {
                        "type": "string",
                        "description": "Keyboard key used by press actions.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Local file path used by upload actions.",
                    },
                    "timeout_ms": {
                        "type": "integer",
                        "description": "Timeout used by wait actions in milliseconds.",
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Whether screenshot should capture beyond the viewport when supported.",
                    },
                },
            },
        )

    def _service(self):
        service = getattr(self._target, "browser_service", None)
        if service is None:
            raise RuntimeError("browser_service_not_ready")
        return service

    def _resolve_profile_id(self, profile_id: str = "") -> str:
        service = self._service()
        return str(profile_id or "").strip() or service.get_default_profile_id()

    def _json(self, payload) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2)


class BrowserStatusTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_status",
            description="Read browser runtime status, profiles, and install state.",
            target=target,
        )

    def _execute(self, **kwargs):
        return self._json(self._service().get_status())


class BrowserStartTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_start",
            description="Start or attach one browser profile through the browser runtime.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json({"success": True, "status": self._service().start_profile(profile_id)})


class BrowserStopTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_stop",
            description="Stop or detach one browser profile through the browser runtime.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json({"success": True, "status": self._service().stop_profile(profile_id)})


class BrowserDiagnoseTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_diagnose",
            description="Run browser diagnostics for one profile and return structured status.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json({"success": True, "status": self._service().diagnose_profile(profile_id)})


class BrowserReconnectTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_reconnect",
            description="Reconnect to one existing-session or remote browser profile.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json({"success": True, "status": self._service().reconnect_profile(profile_id)})


class BrowserTabsTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_tabs",
            description="List the current tabs visible to one browser profile.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json(self._service().list_profile_tabs(profile_id))


class BrowserSnapshotTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_snapshot",
            description="Capture a page text snapshot from the selected browser tab and archive it.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        target_id = str(kwargs.get("target_id") or "").strip()
        return self._json(self._service().snapshot_profile(profile_id, target_id=target_id))


class BrowserScreenshotTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_screenshot",
            description="Capture a browser screenshot from the selected tab and archive it.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        target_id = str(kwargs.get("target_id") or "").strip()
        full_page = bool(kwargs.get("full_page", True))
        return self._json(self._service().screenshot_profile(profile_id, target_id=target_id, full_page=full_page))


class BrowserTabsOpenTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_tabs_open",
            description="Open one new browser tab through the runtime.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        url = str(kwargs.get("url") or "").strip() or "about:blank"
        return self._json(self._service().open_profile_tab(profile_id, url))


class BrowserTabsSelectTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_tabs_select",
            description="Select one existing browser tab through the runtime.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        target_id = str(kwargs.get("target_id") or "").strip()
        return self._json(self._service().select_profile_tab(profile_id, target_id))


class BrowserTabsCloseTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_tabs_close",
            description="Close one existing browser tab through the runtime.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        target_id = str(kwargs.get("target_id") or "").strip()
        return self._json(self._service().close_profile_tab(profile_id, target_id))


class BrowserActTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_act",
            description="Run one minimal browser action such as navigate, evaluate, click, fill, or upload.",
            target=target,
        )

    def _execute(self, **kwargs):
        profile_id = self._resolve_profile_id(kwargs.get("profile_id") or "")
        return self._json(
            self._service().act_profile(
                profile_id,
                target_id=str(kwargs.get("target_id") or "").strip(),
                kind=str(kwargs.get("kind") or "").strip(),
                selector=str(kwargs.get("selector") or "").strip(),
                value=str(kwargs.get("value") or ""),
                expression=str(kwargs.get("expression") or ""),
                url=str(kwargs.get("url") or ""),
                key=str(kwargs.get("key") or ""),
                file_path=str(kwargs.get("file_path") or ""),
                timeout_ms=int(kwargs.get("timeout_ms") or 0),
            )
        )


class BrowserInstallManagedTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_install_managed",
            description="Install managed Chromium for the managed browser driver when no system Chromium browser is available.",
            target=target,
        )

    def _execute(self, **kwargs):
        service = self._service()
        # Re-detect before installing so the tool can short-circuit if a browser becomes available.
        install_state = service.refresh_install_detection()
        if not bool(install_state.get("offer_install")) and not str(install_state.get("status") or "").strip() == "failed":
            return self._json(
                {
                    "success": True,
                    "skipped": True,
                    "reason": "system_browser_available",
                    "install": install_state,
                }
            )
        return self._json({"success": True, "install": service.install_managed_browser()})


class BrowserInstallRemoveTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_install_remove",
            description="Remove managed Chromium cache and reset managed install state.",
            target=target,
        )

    def _execute(self, **kwargs):
        return self._json({"success": True, "install": self._service().remove_managed_browser()})


class BrowserInstallReinstallTool(_BrowserToolBase):
    def __init__(self, target):
        super().__init__(
            name="browser_install_reinstall",
            description="Reinstall managed Chromium for the managed browser driver.",
            target=target,
        )

    def _execute(self, **kwargs):
        return self._json({"success": True, "install": self._service().reinstall_managed_browser()})
