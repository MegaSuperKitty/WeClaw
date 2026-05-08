# -*- coding: utf-8 -*-
"""Helpers for the durable task-session plan file."""

from __future__ import annotations

import os


PLAN_FILE_NAME = "agent_plan.md"


def plan_path_for_session_history(session_path: str) -> str:
    """Return the durable sibling plan path for one session history file."""
    session_dir = os.path.dirname(os.path.abspath(str(session_path or "").strip()))
    return os.path.join(session_dir, PLAN_FILE_NAME)


def ensure_plan_file(session_path: str) -> str:
    """Materialize an empty plan file next to one session history if missing."""
    path = plan_path_for_session_history(session_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("")
    return path


def read_plan_file(session_path: str) -> str:
    """Read the durable plan content for one session history."""
    path = ensure_plan_file(session_path)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_plan_file(session_path: str, content: str) -> str:
    """Overwrite the durable plan file for one session history."""
    path = ensure_plan_file(session_path)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(content or ""))
    return path
