# -*- coding: utf-8 -*-
"""Build prompt runtime text from workspace layout and session id."""

from __future__ import annotations

from core.workspace.layout import WorkspaceLayout


def build_workspace_runtime_block(layout: WorkspaceLayout, session_id: str) -> str:
    """Describe the current agent and workspace runtime in prompt-ready text."""
    return (
        f"Agent ID: {layout.agent_id}\n"
        f"Agent Root: {layout.agent_root}\n"
        f"Workspace Root: {layout.workspace_root}\n"
        f"Source Root: {layout.source_root}\n"
        f"Session ID: {session_id}\n"
        "Default Rule:\n"
        "- Resolve relative paths from the fixed workspace root.\n"
        "- Use an explicit workdir only for the current tool call.\n"
        "- Do not assume shell state persists across tool calls.\n"
    )
