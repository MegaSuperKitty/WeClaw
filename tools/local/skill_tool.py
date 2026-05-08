# -*- coding: utf-8 -*-
"""Skill tool: load skill prompts and synchronize skill-aware runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from skills.registry import SkillMeta, SkillRegistry
from integrations.mcp.openai_tool import Tool


@dataclass
class SkillRuntimeSnapshot:
    """Cached skill-derived runtime values."""

    skills: List[SkillMeta] = field(default_factory=list)
    skills_prompt_block: str = ""
    tool_description: str = "Load a skill prompt by name. No skills available."
    system_prompt: str = ""


class SkillRuntime:
    """Own skill discovery state and derived prompt metadata."""

    def __init__(self, project_root: str, workspace_root: str):
        self.project_root = project_root
        self.workspace_root = workspace_root
        self._registry = SkillRegistry(project_root=project_root, workspace_root=workspace_root)
        self._snapshot = SkillRuntimeSnapshot()
        self._managed_tools: List["SkillTool"] = []
        self._last_base_system_prompt = ""

    def create_tool(self, allowed_skills: Optional[List[str]] = None, register: bool = False) -> "SkillTool":
        """Create a skill tool backed by the current cached runtime snapshot."""
        tool = SkillTool(self, allowed_skills=allowed_skills)
        if register:
            self._managed_tools.append(tool)
        return tool

    def refresh(self, base_system_prompt: str) -> SkillRuntimeSnapshot:
        """Refresh skills from disk and rebuild derived runtime text."""
        self._last_base_system_prompt = str(base_system_prompt or "")
        self._registry.refresh()
        skills = self._registry.list_cached_skills()
        snapshot = SkillRuntimeSnapshot(
            skills=list(skills),
            skills_prompt_block=_build_skills_prompt_block(skills),
            tool_description=_build_description(skills, None),
        )
        snapshot.system_prompt = _compose_system_prompt(self._last_base_system_prompt, snapshot.skills_prompt_block)
        self._snapshot = snapshot
        self._refresh_managed_tools()
        return snapshot

    def list_skills(self) -> List[SkillMeta]:
        """Return the current cached skill metadata snapshot."""
        return list(self._snapshot.skills)

    def build_tool_description(self, allowlist: Optional[List[str]] = None) -> str:
        """Build a skill tool description from the cached runtime snapshot."""
        return _build_description(self._snapshot.skills, _normalize_allowlist(allowlist))

    def get_prompt(self, name: str) -> Optional[str]:
        """Return a cached prompt from the most recent synchronized snapshot."""
        return self._registry.get_cached_prompt(name)

    def get_meta(self, name: str) -> Optional[SkillMeta]:
        """Return cached metadata from the most recent synchronized snapshot."""
        return self._registry.get_cached_meta(name)

    def list_all_skills(self) -> List[SkillMeta]:
        """Return all discovered skills, including disabled ones."""
        self._registry.refresh()
        return self._registry.list_cached_skills(include_disabled=True)

    def set_enabled(self, skill_id: str, enabled: bool) -> SkillMeta:
        """Toggle one skill and refresh derived runtime state."""
        meta = self._registry.set_enabled(skill_id, enabled=enabled)
        self.refresh(self._last_base_system_prompt)
        return meta

    def _refresh_managed_tools(self) -> None:
        for tool in self._managed_tools:
            tool.refresh_description()


class SkillTool(Tool):
    """Load a skill prompt as a tool result."""

    def __init__(self, runtime: SkillRuntime, allowed_skills: Optional[List[str]] = None):
        self.runtime = runtime
        self.allowed_skills = _normalize_allowlist(allowed_skills)
        parameters = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name to load",
                },
            },
            "required": ["name"],
        }
        super().__init__(
            name="skill",
            description=runtime.build_tool_description(self.allowed_skills),
            parameters=parameters,
        )

    def refresh_description(self) -> None:
        """Refresh the tool description from the current runtime snapshot."""
        self.description = self.runtime.build_tool_description(self.allowed_skills)

    def _execute(self, **kwargs):
        name = (kwargs.get("name") or "").strip()
        if not name:
            return "Skill error: name is required."
        if self.allowed_skills is not None and name not in self.allowed_skills:
            return f"Skill not allowed: {name}"
        prompt = self.runtime.get_prompt(name)
        if not prompt:
            return f"Skill not found: {name}"
        return prompt


def sync_skill_runtime(target: Any, runtime: Optional[SkillRuntime] = None) -> SkillRuntimeSnapshot:
    """Synchronize skill-derived runtime state onto a target object."""
    current_runtime = runtime or getattr(target, "skill_runtime", None)
    if current_runtime is None:
        raise ValueError("sync_skill_runtime requires a SkillRuntime.")
    base_system_prompt = str(getattr(target, "_base_system_prompt", "") or "")
    snapshot = current_runtime.refresh(base_system_prompt)
    setattr(target, "system_prompt", snapshot.system_prompt)
    return snapshot


def _build_description(skills: List[SkillMeta], allowlist: Optional[List[str]]) -> str:
    visible_skills = list(skills or [])
    if allowlist is not None:
        allowed = set(allowlist)
        visible_skills = [meta for meta in visible_skills if meta.name in allowed]
    if not visible_skills:
        return "Load a skill prompt by name. No skills available."
    lines = [
        "Load a skill prompt by name.",
        "If the user mentions a specific skill, call this tool first and follow the skill instructions before acting.",
        "Skills are prompts, not executable tools.",
        "Available skills:",
    ]
    for meta in visible_skills:
        desc = meta.description or meta.when_to_use or ""
        if desc:
            lines.append(f"- {meta.skill_id}: {desc}")
        else:
            lines.append(f"- {meta.skill_id}")
    return "\n".join(lines)


def _build_skills_prompt_block(skills: List[SkillMeta]) -> str:
    if not skills:
        return "\n\n[Skills]\n(No skills available.)"
    lines = ["\n\n[Skills]"]
    for meta in skills:
        if meta.description:
            lines.append(f"- {meta.skill_id}: {meta.description}")
        elif meta.when_to_use:
            lines.append(f"- {meta.skill_id}: {meta.when_to_use}")
        else:
            lines.append(f"- {meta.skill_id}")
    return "\n".join(lines)


def _compose_system_prompt(base_system_prompt: str, skills_prompt_block: str) -> str:
    return str(base_system_prompt or "") + str(skills_prompt_block or "")


def _normalize_allowlist(allowed: Optional[List[str]]) -> Optional[List[str]]:
    if allowed is None:
        return None
    if isinstance(allowed, list):
        cleaned = [str(s).strip() for s in allowed if str(s).strip()]
        return cleaned
    text = str(allowed).strip()
    return [text] if text else []
