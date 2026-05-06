# -*- coding: utf-8 -*-
"""Find files by glob pattern under the fixed workspace root."""

from __future__ import annotations

from typing import Optional
import glob
import os

from integrations.mcp.openai_tool import Tool

from .path_utils import is_within_base, normalize_root, resolve_relative_path, resolve_tool_base


class GlobTool(Tool):
    """Find files by glob pattern under the shared session cwd."""

    def __init__(self, agent_root: Optional[str] = None, cwd_manager=None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="glob",
            description="Find files by glob pattern under agent working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern relative to the fixed workspace root."},
                    "workdir": {"type": "string", "description": "Optional subdirectory for this call only."},
                    "max_results": {"type": "integer", "description": "Maximum results to return."},
                },
                "required": ["pattern"],
            },
        )

    def _execute(self, **kwargs):
        pattern = (kwargs.get("pattern") or "").strip()
        max_results = int(kwargs.get("max_results") or 200)
        if not pattern:
            return "pattern must not be empty."
        try:
            base = resolve_relative_path(self._base_dir(kwargs.get("workdir")), ".")
        except ValueError:
            return "base directory is invalid."
        full_pattern = os.path.join(base, pattern)
        results = glob.glob(full_pattern, recursive=True)
        filtered = []
        for path in results:
            if not is_within_base(path, base):
                continue
            filtered.append(os.path.relpath(path, base))
            if len(filtered) >= max_results:
                break
        if not filtered:
            return "no files matched."
        return "\n".join(filtered)

    def _base_dir(self, workdir: Optional[str]) -> str:
        return resolve_tool_base(self._agent_root, workdir)
