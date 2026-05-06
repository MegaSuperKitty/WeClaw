# -*- coding: utf-8 -*-
"""Persistent storage for channel configuration."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any, Dict, Mapping


class ChannelConfigStore:
    """Read and write raw channel configuration."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path).resolve()
        self._lock = threading.Lock()

    def read_channels(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return self._read_locked()

    def update_channel(
        self,
        channel_name: str,
        *,
        default_enabled: bool,
        default_bot_prefix: str,
        field_secret_flags: Mapping[str, bool],
        enabled: bool | None = None,
        bot_prefix: str | None = None,
        settings: Mapping[str, Any] | None = None,
    ) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            channels = self._read_locked()
            row = channels.get(channel_name, {})
            row = row if isinstance(row, dict) else {}
            current_settings = row.get("settings", {})
            current_settings = current_settings if isinstance(current_settings, dict) else {}

            next_settings: Dict[str, str] = {}
            for key, value in current_settings.items():
                next_settings[str(key)] = str(value or "").strip()

            incoming = settings if isinstance(settings, Mapping) else {}
            for key, value in incoming.items():
                key_text = str(key or "").strip()
                if not key_text:
                    continue
                text = str(value or "").strip()
                if field_secret_flags.get(key_text, False):
                    if text:
                        next_settings[key_text] = text
                    continue
                next_settings[key_text] = text

            merged: Dict[str, Any] = {
                "enabled": bool(row.get("enabled", default_enabled)),
                "bot_prefix": str(row.get("bot_prefix", default_bot_prefix) or "").strip(),
                "settings": next_settings,
            }
            if enabled is not None:
                merged["enabled"] = bool(enabled)
            if bot_prefix is not None:
                merged["bot_prefix"] = str(bot_prefix or "").strip()

            channels[channel_name] = merged
            self._write_locked(channels)
            return channels

    def _read_locked(self) -> Dict[str, Dict[str, Any]]:
        if not self.data_path.is_file():
            return {}
        try:
            payload = json.loads(self.data_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        node = payload.get("channels", payload)
        if not isinstance(node, dict):
            return {}

        out: Dict[str, Dict[str, Any]] = {}
        for key, value in node.items():
            if isinstance(value, dict):
                out[str(key)] = dict(value)
        return out

    def _write_locked(self, channels: Mapping[str, Any]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"channels": channels}
        self.data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
