# -*- coding: utf-8 -*-
"""Skill catalog reader for the web console."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from skills.registry import SkillRegistry


class SkillsCatalog:
    """Read and shape skill metadata from workspace `skills/` directory."""

    def __init__(self, project_root: str, workspace_root: str):
        self.project_root = Path(project_root).resolve()
        self.workspace_root = Path(workspace_root).resolve()
        self.registry = SkillRegistry(str(self.project_root), str(self.workspace_root))

    def list_skills(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for meta in self.registry.list_skills(include_disabled=True):
            rows.append(
                {
                    "skill_id": meta.skill_id,
                    "name": meta.name,
                    "directory": Path(meta.absolute_path).name if meta.absolute_path else meta.skill_id,
                    "description": meta.description,
                    "path": meta.path,
                    "enabled": meta.enabled,
                    "kind": meta.kind,
                    "source_id": meta.source_id,
                    "has_local_changes": meta.has_local_changes,
                    "version": meta.version,
                    "last_synced_at": meta.last_synced_at,
                }
            )
        rows.sort(key=lambda item: (not bool(item.get("enabled")), str(item.get("skill_id") or "").lower()))
        return rows
