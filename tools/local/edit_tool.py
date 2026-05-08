# -*- coding: utf-8 -*-
"""Edit files under the fixed workspace root."""

from __future__ import annotations

from typing import Optional
import os

from integrations.mcp.openai_tool import Tool

from .path_utils import normalize_root, resolve_relative_path, resolve_tool_base


class EditTool(Tool):
    """Edit files under the shared session cwd."""

    def __init__(self, agent_root: Optional[str] = None, cwd_manager=None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="edit",
            description=(
                "Edit a file under the agent working directory. "
                "Prefer text replacement by context; line edits are a fallback."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under the fixed workspace root."},
                    "workdir": {"type": "string", "description": "Optional subdirectory for this call only."},
                    "old_text": {"type": "string", "description": "Text to replace (context-based)."},
                    "new_text": {"type": "string", "description": "Replacement text."},
                    "line_start": {"type": "integer", "description": "1-based start line for line edit."},
                    "line_end": {"type": "integer", "description": "1-based end line for line edit."},
                },
                "required": ["path"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        old_text = kwargs.get("old_text")
        new_text = kwargs.get("new_text") or ""
        line_start = kwargs.get("line_start")
        line_end = kwargs.get("line_end")

        try:
            abs_path = resolve_relative_path(self._base_dir(kwargs.get("workdir")), path)
        except ValueError:
            return "path is invalid or outside the allowed workspace."
        if not os.path.isfile(abs_path):
            return "file does not exist."

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read()

        if old_text:
            if old_text not in content:
                return "old_text was not found in the file."
            _write_file(abs_path, content.replace(old_text, new_text, 1))
            return "file updated."

        if line_start is None or line_end is None:
            return "provide either old_text or line_start/line_end."
        try:
            start = int(line_start)
            end = int(line_end)
        except (TypeError, ValueError):
            return "line_start and line_end must be integers."
        if start < 1 or end < start:
            return "line range is invalid."

        lines = content.splitlines()
        updated_lines = lines[: start - 1] + new_text.splitlines() + lines[end:]
        _write_file(abs_path, "\n".join(updated_lines) + ("\n" if content.endswith("\n") else ""))
        return "file updated by line range."

    def _base_dir(self, workdir: Optional[str]) -> str:
        return resolve_tool_base(self._agent_root, workdir)


def _write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
