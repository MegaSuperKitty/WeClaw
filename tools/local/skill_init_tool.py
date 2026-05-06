# -*- coding: utf-8 -*-
"""Skill initializer tool: create a new skill directory under ./skills."""

from __future__ import annotations

import os
import re
import subprocess
import sys

from integrations.mcp.openai_tool import Tool


_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SkillInitTool(Tool):
    """Initialize a skill directory from the skill-creator script."""

    def __init__(self, skills_root: str):
        self._skills_root = os.path.abspath(skills_root)
        self._script_path = os.path.join(self._skills_root, "skill-creator", "scripts", "init_skill.py")
        super().__init__(
            name="skill_init",
            description=(
                "Initialize a new skill folder under ./skills using the skill-creator template. "
                "Provide the skill name only (lowercase letters/numbers with hyphens)."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Skill name, e.g. my-new-skill"}
                },
                "required": ["skill_name"],
            },
        )

    def _execute(self, **kwargs):
        skill_name = (kwargs.get("skill_name") or "").strip()
        if not skill_name:
            return "skill_name must not be empty."
        if not _SKILL_NAME_RE.match(skill_name):
            return "skill_name must be lowercase letters/numbers separated by hyphens."
        if not os.path.isfile(self._script_path):
            return "init_skill.py not found; cannot initialize skill."

        target_dir = os.path.join(self._skills_root, skill_name)
        if os.path.exists(target_dir):
            return f"skill directory already exists: {target_dir}"

        try:
            completed = subprocess.run(
                [sys.executable, self._script_path, skill_name, "--path", self._skills_root],
                capture_output=True,
                text=True,
                cwd=self._skills_root,
            )
        except Exception as exc:
            return f"skill initialization failed: {exc}"

        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        output = "\n".join(part for part in [stdout, stderr] if part).strip()
        if not output:
            output = f"(no output, exit code {completed.returncode})"
        return output + f"\n\nskill path: {target_dir}"
