# -*- coding: utf-8 -*-
"""Persistent runtime preferences for the console and chat entrypoints."""

from __future__ import annotations

from pathlib import Path
import threading
from typing import Any, Dict, Mapping

import yaml


DEFAULT_RUNTIME_CONFIG: Dict[str, Dict[str, str]] = {
    "ui": {
        "language": "zh",
        "theme_mode": "light",
    },
    "chat": {
        "preferred_response_language": "zh",
    },
}


def _normalize_language(value: Any) -> str:
    text = str(value or "").strip().lower()
    return "en" if text == "en" else "zh"


def _normalize_theme_mode(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"dark", "auto"}:
        return text
    return "light"


def normalize_runtime_config(payload: Mapping[str, Any] | None) -> Dict[str, Dict[str, str]]:
    data = payload if isinstance(payload, Mapping) else {}
    ui = data.get("ui", {})
    ui = ui if isinstance(ui, Mapping) else {}
    chat = data.get("chat", {})
    chat = chat if isinstance(chat, Mapping) else {}
    return {
        "ui": {
            "language": _normalize_language(ui.get("language")),
            "theme_mode": _normalize_theme_mode(ui.get("theme_mode")),
        },
        "chat": {
            "preferred_response_language": _normalize_language(chat.get("preferred_response_language")),
        },
    }


class RuntimeConfigStore:
    """Read and write runtime preferences under the agent runtime root."""

    def __init__(self, path: str):
        self.path = Path(path).resolve()
        self._lock = threading.Lock()

    def get_state(self) -> Dict[str, Dict[str, str]]:
        with self._lock:
            return self._read_locked()

    def update_state(self, payload: Mapping[str, Any] | None) -> Dict[str, Dict[str, str]]:
        with self._lock:
            current = self._read_locked()
            incoming = payload if isinstance(payload, Mapping) else {}
            merged: Dict[str, Any] = {
                "ui": dict(current.get("ui", {})),
                "chat": dict(current.get("chat", {})),
            }
            incoming_ui = incoming.get("ui", {})
            if isinstance(incoming_ui, Mapping):
                merged["ui"].update(dict(incoming_ui))
            incoming_chat = incoming.get("chat", {})
            if isinstance(incoming_chat, Mapping):
                merged["chat"].update(dict(incoming_chat))
            normalized = normalize_runtime_config(merged)
            self._write_locked(normalized)
            return normalized

    def preferred_response_language(self) -> str:
        return self.get_state()["chat"]["preferred_response_language"]

    def ensure_exists(self) -> Dict[str, Dict[str, str]]:
        with self._lock:
            current = self._read_locked()
            if not self.path.is_file():
                self._write_locked(current)
            return current

    def _read_locked(self) -> Dict[str, Dict[str, str]]:
        if not self.path.is_file():
            return normalize_runtime_config(DEFAULT_RUNTIME_CONFIG)
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        except Exception:
            return normalize_runtime_config(DEFAULT_RUNTIME_CONFIG)
        if not isinstance(raw, Mapping):
            return normalize_runtime_config(DEFAULT_RUNTIME_CONFIG)
        return normalize_runtime_config(raw)

    def _write_locked(self, data: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(dict(data), allow_unicode=True, sort_keys=False)
        self.path.write_text(text, encoding="utf-8")
