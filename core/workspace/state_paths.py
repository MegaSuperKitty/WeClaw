# -*- coding: utf-8 -*-
"""Global state and workspace path resolution."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


DEFAULT_GLOBAL_DIRNAME = ".weclaw"
GLOBAL_ROOT_ENV = "WE_CLAW_HOME"
AGENT_ID_ENV = "WE_CLAW_AGENT_ID"
DEFAULT_AGENT_ID = "main"


def _normalize_name(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "default"
    cleaned: list[str] = []
    for ch in text:
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in {"-", "_"}:
            cleaned.append(ch)
        else:
            cleaned.append("-")
    normalized = "".join(cleaned).strip("-_")
    return normalized or "default"


def build_workspace_id(source_root: str) -> str:
    """Return the singleton workspace id for display/runtime metadata."""
    _ = source_root
    return resolve_current_agent_id()


def normalize_agent_id(agent_id: str | None) -> str:
    """Normalize one agent id to a stable filesystem-safe name."""
    return _normalize_name(agent_id or DEFAULT_AGENT_ID)


def resolve_current_agent_id(agent_id: str | None = None) -> str:
    """Resolve the active agent id from explicit input or environment."""
    candidate = str(agent_id or "").strip()
    if candidate:
        return normalize_agent_id(candidate)
    env_value = os.getenv(AGENT_ID_ENV, "").strip()
    if env_value:
        return normalize_agent_id(env_value)
    return DEFAULT_AGENT_ID


def resolve_global_root() -> str:
    """Resolve the global WeClaw state root."""
    env_root = os.getenv(GLOBAL_ROOT_ENV, "").strip()
    if env_root:
        return str(Path(env_root).resolve())
    return str((Path.home() / DEFAULT_GLOBAL_DIRNAME).resolve())


def resolve_agents_root() -> str:
    """Resolve the global agents root."""
    return str((Path(resolve_global_root()) / "agents").resolve())


def resolve_agent_root(agent_id: str | None = None) -> str:
    """Resolve the root directory for one agent."""
    return str((Path(resolve_agents_root()) / resolve_current_agent_id(agent_id)).resolve())


def resolve_workspace_root(source_root: str, workspace_id: str | None = None) -> str:
    """Resolve the fixed workspace root for one agent."""
    _ = source_root
    return str((Path(resolve_agent_root(workspace_id)) / "workspace").resolve())


@dataclass(frozen=True)
class GlobalStatePaths:
    """Describe the global WeClaw state tree."""

    global_root: str
    agents_root: str


def build_global_state_paths() -> GlobalStatePaths:
    """Build the minimal global state tree rooted at ``~/.weclaw`` by default."""
    root = Path(resolve_global_root())
    return GlobalStatePaths(
        global_root=str(root),
        agents_root=str(root / "agents"),
    )


def ensure_global_state_paths() -> GlobalStatePaths:
    """Create the global WeClaw state tree."""
    paths = build_global_state_paths()
    for path in (
        paths.global_root,
        paths.agents_root,
    ):
        os.makedirs(path, exist_ok=True)
    return paths
