# -*- coding: utf-8 -*-
"""Read text files under the fixed workspace root."""

from __future__ import annotations

from typing import Optional
import os

from integrations.mcp.openai_tool import Tool

from .path_utils import normalize_root, resolve_relative_path, resolve_tool_base


class ReadTool(Tool):
    """Read a text file with line numbers."""

    def __init__(self, agent_root: Optional[str] = None, cwd_manager=None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="read",
            description="Read a text file with line numbers (agent working directory only).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path under the fixed workspace root."},
                    "workdir": {"type": "string", "description": "Optional subdirectory for this call only."},
                    "start_line": {"type": "integer", "description": "Start line (1-based)."},
                    "end_line": {"type": "integer", "description": "End line (1-based)."},
                    "max_lines": {"type": "integer", "description": "Maximum lines to return (capped at 100)."},
                    "start_char": {"type": "integer", "description": "Start character offset (0-based)."},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return (capped at 9000)."},
                },
                "required": ["path"],
            },
        )

    def _execute(self, **kwargs):
        path = kwargs.get("path")
        start_line = int(kwargs.get("start_line") or 1)
        end_line = kwargs.get("end_line")
        max_lines = min(int(kwargs.get("max_lines") or 200), 100)
        start_char = max(int(kwargs.get("start_char") or 0), 0)
        max_chars = max(min(int(kwargs.get("max_chars") or 4000), 9000), 1)
        try:
            abs_path = resolve_relative_path(self._base_dir(kwargs.get("workdir")), path)
        except ValueError:
            return "path is invalid or outside the allowed workspace."
        if not os.path.isfile(abs_path):
            return "file does not exist."
        if start_line < 1:
            start_line = 1

        lines = []
        file_pos = 0
        out_chars = 0
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                line_len = len(line)
                if idx < start_line:
                    file_pos += line_len
                    continue
                if end_line is not None and idx > int(end_line):
                    break
                line_start = file_pos
                line_end = file_pos + line_len
                file_pos = line_end
                if start_char >= line_end:
                    continue
                slice_start = max(start_char - line_start, 0) if start_char > line_start else 0
                display_line = line.rstrip()
                if slice_start >= len(display_line):
                    continue
                display_line = display_line[slice_start:]
                prefix = f"{idx:>6}: "
                remaining = max_chars - out_chars
                if remaining <= len(prefix):
                    break
                available = remaining - len(prefix)
                if len(display_line) > available:
                    display_line = display_line[:available]
                output_line = prefix + display_line
                lines.append(output_line)
                out_chars += len(output_line) + 1
                if len(lines) >= max_lines or out_chars >= max_chars:
                    break
        if not lines:
            return "no readable content found in the requested range."
        return "\n".join(lines)

    def _base_dir(self, workdir: Optional[str]) -> str:
        return resolve_tool_base(self._agent_root, workdir)
