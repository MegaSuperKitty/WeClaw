# -*- coding: utf-8 -*-
"""Load workspace prompt markdown files from the workspace-private prompt root."""

from __future__ import annotations

import os

from core.workspace.layout import WorkspaceLayout


PROMPT_FILE_NAMES = (
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "AGENT.md",
    "MEMORY.md",
)

SYSTEM_PROMPT_TEMPLATE = (
    "# Highest-Priority Runtime Constraints\n"
    "{highest_priority_runtime_constraints}\n\n"
    "# Core Principles\n"
    "{soul_content}\n\n"
    "# Identity\n"
    "{identity_content}\n\n"
    "# User Profile\n"
    "{user_content}\n\n"
    "# Operating Rules\n"
    "{agent_content}\n\n"
    "# Long-Term Memory\n"
    "{memory_content}\n\n"
    "# Current Workspace State\n"
    "{workspace_runtime}\n\n"
    "# Active Skills\n"
    "{skills_runtime}\n"
)


def load_workspace_prompt_bundle(layout: WorkspaceLayout) -> dict[str, str]:
    """Load the prompt bundle from the workspace prompt directory."""
    bundle: dict[str, str] = {"SYSTEM_PROMPT.md": SYSTEM_PROMPT_TEMPLATE}
    for file_name in PROMPT_FILE_NAMES:
        path = os.path.join(layout.prompt_root, file_name)
        with open(path, "r", encoding="utf-8") as handle:
            bundle[file_name] = handle.read()
    return bundle
