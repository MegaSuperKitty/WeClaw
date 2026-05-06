# -*- coding: utf-8 -*-
"""Write file contents under the fixed workspace root."""

from __future__ import annotations

from typing import Optional
import os

from integrations.mcp.openai_tool import Tool

from .path_utils import normalize_root, resolve_relative_path, resolve_tool_base


class WriteFileTool(Tool):
    """Create new files under the current shared cwd."""

    def __init__(self, agent_root: Optional[str] = None, cwd_manager=None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="write_file",
            description=(
                "Create a new file under the agent working directory. "
                "Will not overwrite existing files; use edit for modifications. "
                "Paths are restricted to the agent root."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under the fixed workspace root."},
                    "workdir": {"type": "string", "description": "Optional subdirectory for this call only."},
                    "content": {"type": "string", "description": "Full file content to write."},
                },
                "required": ["path", "content"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        content = kwargs.get("content") or ""
        try:
            abs_path = resolve_relative_path(self._base_dir(kwargs.get("workdir")), path)
        except ValueError:
            return "path is invalid or outside the allowed workspace."
        if os.path.exists(abs_path):
            return "file already exists; use edit for modifications."
        parent = os.path.dirname(abs_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return "file written successfully."

    def _base_dir(self, workdir: Optional[str]) -> str:
        return resolve_tool_base(self._agent_root, workdir)
