# -*- coding: utf-8 -*-
"""Workspace skill registry and discovery helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shutil
from typing import Dict, Iterable, List


@dataclass
class SkillRecord:
    """Persisted skill registry row."""

    skill_id: str
    name: str
    kind: str
    source_id: str
    path: str
    enabled: bool = True
    version: str = ""
    has_local_changes: bool = False
    last_synced_at: str = ""

    def to_dict(self) -> Dict[str, object]:
        """Serialize one registry row."""
        return asdict(self)


class SkillRegistryManager:
    """Persist skill activation state as the single source of truth."""

    def __init__(self, registry_path: str, workspace_root: str):
        self.registry_path = os.path.abspath(registry_path)
        self.workspace_root = os.path.abspath(workspace_root)

    def load(self) -> Dict[str, SkillRecord]:
        """Load registry rows keyed by skill id."""
        if not os.path.isfile(self.registry_path):
            return {}
        try:
            with open(self.registry_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            return {}
        rows = payload if isinstance(payload, list) else []
        result: Dict[str, SkillRecord] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            skill_id = str(row.get("skill_id") or "").strip()
            if not skill_id:
                continue
            result[skill_id] = SkillRecord(
                skill_id=skill_id,
                name=str(row.get("name") or skill_id).strip() or skill_id,
                kind=str(row.get("kind") or "local").strip() or "local",
                source_id=str(row.get("source_id") or "local").strip() or "local",
                path=str(row.get("path") or "").strip(),
                enabled=bool(row.get("enabled", True)),
                version=str(row.get("version") or "").strip(),
                has_local_changes=bool(row.get("has_local_changes", False)),
                last_synced_at=str(row.get("last_synced_at") or "").strip(),
            )
        return result

    def save(self, rows: Iterable[SkillRecord]) -> None:
        """Persist registry rows atomically."""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        payload = [row.to_dict() for row in rows]
        tmp_path = f"{self.registry_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.registry_path)

    def ensure_records(self, discovered_rows: List[Dict[str, str]]) -> Dict[str, SkillRecord]:
        """Merge discovered skills into the registry and persist missing rows."""
        current = self.load()
        changed = False
        result: Dict[str, SkillRecord] = {}
        for item in discovered_rows:
            skill_id = str(item.get("skill_id") or "").strip()
            if not skill_id:
                continue
            existing = current.get(skill_id)
            if existing is None:
                existing = SkillRecord(
                    skill_id=skill_id,
                    name=str(item.get("name") or skill_id).strip() or skill_id,
                    kind=str(item.get("kind") or "local").strip() or "local",
                    source_id=str(item.get("source_id") or "local").strip() or "local",
                    path=str(item.get("path") or "").strip(),
                    enabled=True,
                )
                changed = True
            else:
                normalized_path = str(item.get("path") or "").strip()
                normalized_name = str(item.get("name") or existing.name).strip() or existing.name
                normalized_kind = str(item.get("kind") or existing.kind).strip() or existing.kind
                normalized_source_id = str(item.get("source_id") or existing.source_id).strip() or existing.source_id
                if (
                    existing.path != normalized_path
                    or existing.name != normalized_name
                    or existing.kind != normalized_kind
                    or existing.source_id != normalized_source_id
                ):
                    existing = SkillRecord(
                        skill_id=existing.skill_id,
                        name=normalized_name,
                        kind=normalized_kind,
                        source_id=normalized_source_id,
                        path=normalized_path,
                        enabled=existing.enabled,
                        version=existing.version,
                        has_local_changes=existing.has_local_changes,
                        last_synced_at=existing.last_synced_at,
                    )
                    changed = True
            result[skill_id] = existing
        if set(current.keys()) != set(result.keys()):
            changed = True
        if changed:
            self.save(result.values())
        return result

    def set_enabled(self, skill_id: str, enabled: bool) -> SkillRecord:
        """Toggle one skill and persist the registry."""
        rows = self.load()
        target = rows.get(skill_id)
        if target is None:
            raise KeyError(skill_id)
        updated = SkillRecord(
            skill_id=target.skill_id,
            name=target.name,
            kind=target.kind,
            source_id=target.source_id,
            path=target.path,
            enabled=bool(enabled),
            version=target.version,
            has_local_changes=target.has_local_changes,
            last_synced_at=target.last_synced_at,
        )
        rows[skill_id] = updated
        self.save(rows.values())
        return updated

    def relpath(self, path: str) -> str:
        """Return a workspace-relative path when possible."""
        absolute = os.path.abspath(path)
        try:
            return os.path.relpath(absolute, self.workspace_root).replace("\\", "/")
        except ValueError:
            return absolute.replace("\\", "/")


def discover_skill_content_roots(project_root: str, workspace_skills_root: str) -> List[tuple[str, str, str]]:
    """Return the ordered content roots for skills discovery."""
    roots: List[tuple[str, str, str]] = []
    workspace_local = Path(workspace_skills_root) / "local"
    workspace_imported = Path(workspace_skills_root) / "imported"
    roots.append(("local", "local", str(workspace_local.resolve())))
    roots.append(("imported", "imported", str(workspace_imported.resolve())))
    return roots


def seed_workspace_skills_from_project(project_root: str, workspace_skills_local_root: str) -> None:
    """Copy bundled project skills into the workspace-local skills root once."""
    source_root = Path(project_root) / "skills"
    target_root = Path(workspace_skills_local_root)
    if not source_root.is_dir():
        return
    target_root.mkdir(parents=True, exist_ok=True)
    for entry in source_root.iterdir():
        if not entry.is_dir():
            continue
        if not (entry / "SKILL.md").is_file():
            continue
        target = target_root / entry.name
        if target.exists():
            continue
        shutil.copytree(entry, target)
