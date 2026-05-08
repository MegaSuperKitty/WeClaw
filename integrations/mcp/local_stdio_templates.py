# -*- coding: utf-8 -*-
"""Built-in local MCP stdio templates and compatibility helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional


_STDIO_BUILTIN_SERVERS = {
    "filesystem",
    "research",
    "skills",
    "brave_search",
    "vision_models",
    "generation_models",
    "speech_models",
    "embedding_models",
}


def supports_local_stdio(server_id: str) -> bool:
    return str(server_id or "").strip() in _STDIO_BUILTIN_SERVERS


def local_stdio_template(project_root: str, server_id: str) -> Optional[Dict[str, object]]:
    normalized = str(server_id or "").strip()
    if not supports_local_stdio(normalized):
        return None
    root = str(Path(project_root).resolve()) if str(project_root or "").strip() else str(Path.cwd().resolve())
    runner = str((Path(__file__).resolve().parent / "local_stdio_runner.py").resolve())
    return {
        "command": sys.executable,
        "args": [runner, "--server-id", normalized, "--project-root", root],
        "cwd": root,
    }
