# -*- coding: utf-8 -*-
"""Search text in files under the allowed workspace root."""

from __future__ import annotations

from typing import Optional
import os

from integrations.mcp.openai_tool import Tool
from .path_utils import is_within_base, normalize_root, resolve_relative_path


class GrepTool(Tool):
    """Search file contents for a plain text pattern."""

    def __init__(self, agent_root: Optional[str] = None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        super().__init__(
            name="grep",
            description="Search for text in files under agent working directory.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Text to search for."},
                    "path": {"type": "string", "description": "Relative file or directory path."},
                    "max_matches": {"type": "integer", "description": "Maximum matches to return."},
                },
                "required": ["pattern"],
            },
        )

    def _execute(self, **kwargs):
        pattern = str(kwargs.get("pattern") or "")
        target = str(kwargs.get("path") or ".").strip()
        max_matches = int(kwargs.get("max_matches") or 200)
        if not pattern:
            return "pattern must not be empty."
        try:
            base = resolve_relative_path(self._agent_root, ".")
            abs_target = resolve_relative_path(self._agent_root, target)
        except ValueError:
            return "path is not allowed or escapes base directory."

        matches: list[str] = []
        if os.path.isfile(abs_target):
            _scan_file(abs_target, base, pattern, matches, max_matches)
        else:
            for root, _, files in os.walk(abs_target):
                if not is_within_base(root, base):
                    continue
                for name in files:
                    file_path = os.path.join(root, name)
                    _scan_file(file_path, base, pattern, matches, max_matches)
                    if len(matches) >= max_matches:
                        break
                if len(matches) >= max_matches:
                    break
        if not matches:
            return "no matches found."
        return "\n".join(matches)


def _scan_file(path: str, base: str, pattern: str, out: list[str], limit: int) -> None:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for index, line in enumerate(handle, start=1):
                if pattern in line:
                    rel = os.path.relpath(path, base)
                    out.append(f"{rel}:{index}: {line.rstrip()}")
                    if len(out) >= limit:
                        return
    except (OSError, UnicodeError):
        return
