# -*- coding: utf-8 -*-
"""Resolve typed model runtime config for MCP tools and server availability."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from WeClaw_console.core.model_config import ModelConfigManager
from core.workspace.layout import ensure_workspace_layout_for_source


FREE_FALLBACK_BY_MODEL_TYPE = {
    "speech_to_text": "local_whisper",
    "text_to_speech": "edge_tts",
    "text_embedding": "retrieval_embedder",
}


@dataclass
class ResolvedModelBackend:
    model_type: str
    mode: str
    backend: str
    profile: object | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_type": self.model_type,
            "mode": self.mode,
            "backend": self.backend,
            "profile": self.profile,
        }


class ModelRuntimeResolver:
    """Thin helper that reads typed model config from runtime secrets yaml."""

    def __init__(self, project_root: str):
        root = Path(project_root).resolve()
        self.project_root = str(root)
        layout = ensure_workspace_layout_for_source(str(root))
        self.secrets_path = str(Path(layout.runtime_secrets_path).resolve())
        self.manager = ModelConfigManager(self.secrets_path)

    def availability(self, model_type: str) -> Dict[str, Any]:
        return self.manager.get_model_type_availability(model_type)

    def free_fallback_available(self, model_type: str) -> Dict[str, Any]:
        normalized = str(model_type or "").strip().lower()
        backend = str(FREE_FALLBACK_BY_MODEL_TYPE.get(normalized) or "").strip()
        if not backend:
            return {"model_type": normalized, "available": False, "detail": f"fallback_unsupported:{normalized}"}
        return {"model_type": normalized, "available": True, "detail": f"free_fallback:{backend}", "backend": backend}

    def resolve_profile_or_fallback(self, model_type: str) -> ResolvedModelBackend:
        availability = self.availability(model_type)
        if availability.get("available"):
            profile = self.resolve_active(model_type)
            return ResolvedModelBackend(
                model_type=str(model_type or "").strip().lower(),
                mode="profile",
                backend="openai_compatible",
                profile=profile,
            )

        fallback = self.free_fallback_available(model_type)
        if fallback.get("available"):
            return ResolvedModelBackend(
                model_type=str(model_type or "").strip().lower(),
                mode="free_fallback",
                backend=str(fallback.get("backend") or "").strip(),
                profile=None,
            )

        detail = str(availability.get("detail") or fallback.get("detail") or f"unavailable:{model_type}")
        raise ValueError(detail)

    def resolve_active(self, model_type: str):
        profile = self.manager.resolve_active_profile(model_type)
        if profile is None:
            raise ValueError(f"missing_active_profile:{model_type}")
        availability = self.manager.get_model_type_availability(model_type)
        if not availability.get("available"):
            raise ValueError(str(availability.get("detail") or f"unavailable:{model_type}"))
        return profile


def resolve_project_root(project_root: str = "") -> str:
    if str(project_root or "").strip():
        return str(Path(project_root).resolve())
    return str(Path.cwd().resolve())


def build_model_runtime_resolver(project_root: str = "") -> ModelRuntimeResolver:
    return ModelRuntimeResolver(resolve_project_root(project_root))
