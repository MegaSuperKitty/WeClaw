# -*- coding: utf-8 -*-
"""Public entrypoints for model metering core."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .engine import ModelMeteringEngine
from core.workspace.layout import ensure_workspace_layout
from core.workspace.state_paths import resolve_agent_root, resolve_current_agent_id


_DEFAULT_ENGINE: Optional[ModelMeteringEngine] = None


def default_log_dir() -> str:
    env = str(os.getenv("MODEL_CALL_LOG_DIR", "")).strip()
    if env:
        return str(Path(env).resolve())
    agent_root = resolve_agent_root(resolve_current_agent_id())
    layout = ensure_workspace_layout(agent_root=agent_root, agent_id=resolve_current_agent_id())
    return str(Path(layout.metering_logs_root).resolve())


def get_default_engine(log_dir: str = "") -> ModelMeteringEngine:
    global _DEFAULT_ENGINE
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = ModelMeteringEngine(log_dir or default_log_dir())
    return _DEFAULT_ENGINE


__all__ = [
    "ModelMeteringEngine",
    "get_default_engine",
    "default_log_dir",
]
