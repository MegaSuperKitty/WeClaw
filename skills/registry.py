# -*- coding: utf-8 -*-
"""Skill registry backed by discovery + persisted activation state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import os

from skills.registry_manager import SkillRegistryManager, discover_skill_content_roots, seed_workspace_skills_from_project


@dataclass
class SkillMeta:
    """Metadata plus registry fields for one skill."""

    skill_id: str
    name: str
    description: str = ""
    when_to_use: str = ""
    allowed_tools: Optional[List[str]] = None
    enabled: bool = True
    kind: str = "local"
    source_id: str = "local"
    path: str = ""
    absolute_path: str = ""
    version: str = ""
    has_local_changes: bool = False
    last_synced_at: str = ""


class SkillRegistry:
    """Discover skill content, sync registry state, and expose filtered views."""

    def __init__(self, project_root: str, workspace_root: str):
        self.project_root = os.path.abspath(project_root)
        self.workspace_root = os.path.abspath(workspace_root)
        self.skills_root = os.path.join(self.workspace_root, "skills")
        seed_workspace_skills_from_project(self.project_root, os.path.join(self.skills_root, "local"))
        self.registry_manager = SkillRegistryManager(
            registry_path=os.path.join(self.skills_root, "registry.json"),
            workspace_root=self.workspace_root,
        )
        self._all_cache: Dict[str, tuple[SkillMeta, str]] = {}
        self._enabled_cache: Dict[str, tuple[SkillMeta, str]] = {}

    def refresh(self) -> None:
        """Refresh discovery and registry-backed activation state."""
        discovered = self._discover_skills()
        records = self.registry_manager.ensure_records(discovered)

        all_cache: Dict[str, tuple[SkillMeta, str]] = {}
        enabled_cache: Dict[str, tuple[SkillMeta, str]] = {}
        for item in discovered:
            skill_id = str(item.get("skill_id") or "").strip()
            if not skill_id:
                continue
            record = records.get(skill_id)
            if record is None:
                continue
            meta, prompt = self._load_skill_file(str(item["skill_file"]), item, record.enabled)
            meta.enabled = record.enabled
            meta.kind = record.kind
            meta.source_id = record.source_id
            meta.version = record.version
            meta.has_local_changes = record.has_local_changes
            meta.last_synced_at = record.last_synced_at
            meta.path = record.path or self.registry_manager.relpath(meta.absolute_path)
            all_cache[skill_id] = (meta, prompt)
            if meta.enabled:
                enabled_cache[skill_id] = (meta, prompt)

        self._all_cache = all_cache
        self._enabled_cache = enabled_cache

    def snapshot(self, refresh: bool = True, include_disabled: bool = False) -> Dict[str, tuple[SkillMeta, str]]:
        """Return a copy of the current registry snapshot."""
        if refresh:
            self.refresh()
        cache = self._all_cache if include_disabled else self._enabled_cache
        return {name: (meta, prompt) for name, (meta, prompt) in cache.items()}

    def list_skills(self, include_disabled: bool = False) -> List[SkillMeta]:
        """List skill metadata from the current snapshot."""
        self.refresh()
        return self.list_cached_skills(include_disabled=include_disabled)

    def list_cached_skills(self, include_disabled: bool = False) -> List[SkillMeta]:
        """Return cached skill metadata without refreshing."""
        cache = self._all_cache if include_disabled else self._enabled_cache
        return [meta for meta, _ in cache.values()]

    def get_prompt(self, name: str, include_disabled: bool = False) -> Optional[str]:
        """Return a prompt by skill id or name."""
        self.refresh()
        return self.get_cached_prompt(name, include_disabled=include_disabled)

    def get_cached_prompt(self, name: str, include_disabled: bool = False) -> Optional[str]:
        """Return a cached prompt without refreshing."""
        cache = self._all_cache if include_disabled else self._enabled_cache
        item = self._lookup(cache, name)
        return item[1] if item else None

    def get_meta(self, name: str, include_disabled: bool = False) -> Optional[SkillMeta]:
        """Return metadata by skill id or name."""
        self.refresh()
        return self.get_cached_meta(name, include_disabled=include_disabled)

    def get_cached_meta(self, name: str, include_disabled: bool = False) -> Optional[SkillMeta]:
        """Return cached metadata without refreshing."""
        cache = self._all_cache if include_disabled else self._enabled_cache
        item = self._lookup(cache, name)
        return item[0] if item else None

    def set_enabled(self, skill_id: str, enabled: bool) -> SkillMeta:
        """Toggle one skill and refresh the cache."""
        self.refresh()
        self.registry_manager.set_enabled(skill_id, enabled=enabled)
        self.refresh()
        meta = self.get_cached_meta(skill_id, include_disabled=True)
        if meta is None:
            raise KeyError(skill_id)
        return meta

    def _lookup(self, cache: Dict[str, tuple[SkillMeta, str]], name: str) -> Optional[tuple[SkillMeta, str]]:
        key = str(name or "").strip()
        if not key:
            return None
        direct = cache.get(key)
        if direct is not None:
            return direct
        for skill_id, item in cache.items():
            meta = item[0]
            if meta.name == key or skill_id == key:
                return item
        return None

    def _discover_skills(self) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        seen: set[str] = set()
        for kind, source_id, root in discover_skill_content_roots(self.project_root, self.skills_root):
            root_path = Path(root)
            if not root_path.is_dir():
                continue
            for entry in sorted(root_path.iterdir(), key=lambda item: item.name.lower()):
                if not entry.is_dir():
                    continue
                skill_file = entry / "SKILL.md"
                if not skill_file.is_file():
                    continue
                skill_id = entry.name
                if skill_id in seen:
                    continue
                seen.add(skill_id)
                rows.append(
                    {
                        "skill_id": skill_id,
                        "name": entry.name,
                        "kind": kind,
                        "source_id": source_id,
                        "path": self.registry_manager.relpath(str(entry.resolve())),
                        "skill_file": str(skill_file.resolve()),
                    }
                )
        return rows

    def _load_skill_file(self, path: str, discovered: Dict[str, str], enabled: bool) -> tuple[SkillMeta, str]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except Exception:
            return (
                SkillMeta(
                    skill_id=str(discovered.get("skill_id") or ""),
                    name=str(discovered.get("name") or ""),
                    enabled=enabled,
                    kind=str(discovered.get("kind") or "local"),
                    source_id=str(discovered.get("source_id") or "local"),
                    path=str(discovered.get("path") or ""),
                    absolute_path=str(Path(path).resolve().parent),
                ),
                "",
            )

        meta_data, body = _parse_frontmatter(text)
        skill_id = str(discovered.get("skill_id") or "")
        name = str(meta_data.get("name") or discovered.get("name") or skill_id).strip() or skill_id
        description = str(meta_data.get("description") or "").strip()
        when_to_use = str(meta_data.get("when_to_use") or "").strip()
        allowed_tools = _parse_list(meta_data.get("allowed_tools"))
        return (
            SkillMeta(
                skill_id=skill_id,
                name=name,
                description=description,
                when_to_use=when_to_use,
                allowed_tools=allowed_tools,
                enabled=enabled,
                kind=str(discovered.get("kind") or "local"),
                source_id=str(discovered.get("source_id") or "local"),
                path=str(discovered.get("path") or ""),
                absolute_path=str(Path(path).resolve().parent),
            ),
            body,
        )


def _parse_frontmatter(text: str) -> tuple[Dict[str, object], str]:
    """Parse simple frontmatter from a SKILL.md file."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text
    meta: Dict[str, object] = {}
    end_idx = None
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            end_idx = index
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    if end_idx is None:
        return {}, text
    return meta, "\n".join(lines[end_idx + 1 :]).lstrip()


def _parse_list(value: object) -> Optional[List[str]]:
    """Normalize simple list frontmatter values."""
    if value is None:
        return None
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items or None
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1]
        parts = [item.strip().strip('"').strip("'") for item in inner.split(",")]
        cleaned = [item for item in parts if item]
        return cleaned or None
    return [text]
