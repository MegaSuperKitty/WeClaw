# -*- coding: utf-8 -*-
"""Remote CDP browser driver."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from ..cdp import get_cdp_version, list_page_tabs
from ..models import BrowserProfile, BrowserProfileStatus
from ..profiles import compute_profile_capabilities


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RemoteCdpBrowserDriver:
    """Attach to an explicit remote CDP endpoint."""

    def detect(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        endpoint = str(profile.cdp_url or "").strip()
        if not endpoint:
            return BrowserProfileStatus(
                profile_id=profile.profile_id,
                driver=profile.driver,
                running=False,
                status="misconfigured",
                cdp_url="",
                last_error="remote-cdp profile requires cdp_url",
                updated_at=_utc_now(),
                capabilities=compute_profile_capabilities(profile),
                transport="remote-cdp",
            )

        try:
            get_cdp_version(endpoint)
            tabs = list_page_tabs(endpoint)
            return BrowserProfileStatus(
                profile_id=profile.profile_id,
                driver=profile.driver,
                running=True,
                status="attached",
                cdp_url=endpoint,
                updated_at=_utc_now(),
                capabilities=compute_profile_capabilities(profile),
                transport="remote-cdp",
                tabs=tabs,
                active_tab_id=str(tabs[0].get("target_id") or "") if tabs else "",
            )
        except Exception as exc:
            return BrowserProfileStatus(
                profile_id=profile.profile_id,
                driver=profile.driver,
                running=False,
                status="unreachable",
                cdp_url=endpoint,
                last_error=str(exc),
                updated_at=_utc_now(),
                capabilities=compute_profile_capabilities(profile),
                transport="remote-cdp",
            )

    def start(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        status = self.detect(profile, runtime_state)
        runtime_state[profile.profile_id] = status.to_dict()
        if not status.running:
            raise RuntimeError(status.last_error or "remote-cdp reconnect failed")
        return status

    def stop(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        status = BrowserProfileStatus(
            profile_id=profile.profile_id,
            driver=profile.driver,
            running=False,
            status="detached",
            cdp_url=str(profile.cdp_url or "").strip(),
            updated_at=_utc_now(),
            capabilities=compute_profile_capabilities(profile),
            transport="remote-cdp",
        )
        runtime_state[profile.profile_id] = status.to_dict()
        return status
