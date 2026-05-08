# -*- coding: utf-8 -*-
"""Shared path and config helpers for channel entrypoints."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from core.workspace.layout import ensure_workspace_layout_for_source


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKSPACE_LAYOUT = ensure_workspace_layout_for_source(str(PROJECT_ROOT))
HISTORY_DIR = Path(WORKSPACE_LAYOUT.history_root)
AGENT_ROOT = Path(WORKSPACE_LAYOUT.agent_root)
AGENT_ID = WORKSPACE_LAYOUT.agent_id
RUNTIME_SECRETS_PATH = Path(WORKSPACE_LAYOUT.runtime_secrets_path).resolve()
CHANNEL_CONFIG_PATH = (Path(WORKSPACE_LAYOUT.runtime_console_root) / "channels.json").resolve()


def load_runtime_secrets(path: Path = RUNTIME_SECRETS_PATH) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_channel_settings(channel_name: str, path: Path = CHANNEL_CONFIG_PATH) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    channels = payload.get("channels", payload)
    if not isinstance(channels, dict):
        return {}
    row = channels.get(channel_name, {})
    return row if isinstance(row, dict) else {}
