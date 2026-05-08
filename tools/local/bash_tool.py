# -*- coding: utf-8 -*-
"""Tool for executing shell commands inside the fixed workspace root."""

from __future__ import annotations

from typing import Optional
import os
import shutil
import subprocess

from integrations.mcp.openai_tool import Tool

from .command_safety import contains_path_escape, is_risky_command
from .path_utils import normalize_root, require_existing_dir, resolve_tool_base


class BashTool(Tool):
    """Execute a shell command with an explicit per-call workdir."""

    def __init__(self, agent_root: Optional[str] = None, cwd_manager=None):
        self._agent_root = normalize_root(agent_root or os.getcwd())
        self._runner = self._detect_runner()
        super().__init__(
            name="bash",
            description=(
                "Execute a shell command and return its output. "
                "All paths are resolved under the agent working directory."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute."},
                    "workdir": {
                        "type": "string",
                        "description": "Optional working directory resolved from the fixed workspace root.",
                    },
                },
                "required": ["command"],
            },
        )

    def _execute(self, command: str, workdir: str = None, cd: str = None):
        if is_risky_command(command):
            return "command blocked by safety policy."
        if contains_path_escape(command):
            return "command contains a path escape outside the agent workspace."
        if cd is not None:
            return "persistent cd is no longer supported; pass workdir for this call."

        cwd = self._resolve_workdir(workdir)
        try:
            require_existing_dir(cwd)
        except ValueError:
            return "working directory does not exist."

        if not self._runner:
            return "no supported shell runner found (powershell/pwsh/bash/sh)."

        normalized_command = self._normalize_command_for_runner(command)
        completed = subprocess.run(self._runner + [normalized_command], capture_output=True, text=True, cwd=cwd)

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        output = stdout.strip()
        if stderr.strip():
            output = f"{output}\n{stderr.strip()}".strip()
        if not output:
            output = f"(no output, exit code {completed.returncode})"
        return output

    def _resolve_workdir(self, workdir: Optional[str], strict: bool = False) -> str:
        try:
            return resolve_tool_base(self._agent_root, workdir)
        except ValueError:
            if strict:
                raise
            return self._agent_root

    def _detect_runner(self):
        if os.name == "nt":
            if shutil.which("powershell"):
                return ["powershell", "-NoProfile", "-Command"]
            if shutil.which("pwsh"):
                return ["pwsh", "-NoProfile", "-Command"]
            return None
        if shutil.which("bash"):
            return ["bash", "-lc"]
        if shutil.which("sh"):
            return ["sh", "-lc"]
        return None

    def _normalize_command_for_runner(self, command: str) -> str:
        text = str(command or "").strip()
        if not text:
            return text
        if os.name != "nt" and text.lower().startswith("get-command "):
            target = text[len("Get-Command ") :].strip()
            if target:
                return f"command -v {target}"
        return text
