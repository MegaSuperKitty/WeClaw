# -*- coding: utf-8 -*-
"""Shared helpers for MCP tools backed by typed model config."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import base64
import mimetypes

from openai import OpenAI

from integrations.mcp.model_runtime_resolver import ResolvedModelBackend, build_model_runtime_resolver


def build_openai_client(project_root: str, model_type: str) -> tuple[OpenAI, object]:
    resolver = build_model_runtime_resolver(project_root)
    profile = resolver.resolve_active(model_type)
    client = OpenAI(
        api_key=profile.api_key,
        base_url=profile.base_url or None,
        timeout=profile.timeout or 60.0,
    )
    return client, profile


def resolve_model_backend(project_root: str, model_type: str) -> ResolvedModelBackend:
    resolver = build_model_runtime_resolver(project_root)
    return resolver.resolve_profile_or_fallback(model_type)


def ensure_file_path(path: str) -> Path:
    value = str(path or "").strip()
    if not value:
        raise ValueError("file_path is required")
    target = Path(value).expanduser().resolve()
    if not target.is_file():
        raise ValueError(f"file_not_found:{target}")
    return target


def image_input_from_path_or_url(image_path: str = "", image_url: str = "") -> dict:
    url = str(image_url or "").strip()
    if url:
        return {"type": "input_image", "image_url": url}
    path = str(image_path or "").strip()
    if not path:
        raise ValueError("image_path or image_url is required")
    target = ensure_file_path(path)
    mime_type = mimetypes.guess_type(target.name)[0] or "image/png"
    data = base64.b64encode(target.read_bytes()).decode("ascii")
    return {"type": "input_image", "image_url": f"data:{mime_type};base64,{data}"}


def optional_output_path(output_path: str, default_name: str) -> Path:
    text = str(output_path or "").strip()
    if text:
        return Path(text).expanduser().resolve()
    return (Path.cwd() / default_name).resolve()


def safe_text(value: Optional[str]) -> str:
    return str(value or "").strip()
