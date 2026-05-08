# -*- coding: utf-8 -*-
"""Secret loading helpers for MCP client configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping, Optional


def load_mcp_secrets(path: str) -> Dict[str, str]:
    secret_path = Path(path)
    if not secret_path.is_file():
        return {}
    try:
        import yaml

        with secret_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    secrets: Dict[str, str] = {}
    for key, value in data.items():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            secrets[str(key)] = text
    return secrets


def resolve_secret_refs(secret_refs: Optional[Mapping[str, str]], secrets: Mapping[str, str]) -> Dict[str, str]:
    resolved: Dict[str, str] = {}
    for key, secret_key in (secret_refs or {}).items():
        slot_name = str(key or "").strip()
        name = str(secret_key or "").strip()
        value = resolve_secret_value(slot_name, name, secrets)
        if value:
            resolved[slot_name] = value
    return resolved


def save_mcp_secrets(path: str, updates: Mapping[str, object]) -> Dict[str, str]:
    current = load_mcp_secrets(path)
    changed = False
    for key, value in (updates or {}).items():
        name = str(key or "").strip()
        if not name:
            continue
        text = str(value or "").strip()
        if not text:
            continue
        if current.get(name) == text:
            continue
        current[name] = text
        changed = True
    if not changed and Path(path).is_file():
        return current
    secret_path = Path(path)
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    import yaml

    with secret_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(current, handle, allow_unicode=False, sort_keys=True)
    return current


def stable_secret_ref(client_id: str, slot_name: str) -> str:
    client_token = str(client_id or "").strip()
    slot_token = str(slot_name or "").strip()
    if not client_token or not slot_token:
        return ""
    return f"mcp.{client_token}.{slot_token}"


def mask_secret(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) <= 4:
        return "*" * len(text)
    return f"{'*' * 4}{text[-4:]}"


def resolve_secret_value(slot_name: str, secret_ref: str, secrets: Mapping[str, str]) -> str:
    candidates = _secret_candidates(slot_name, secret_ref)
    for name in candidates:
        value = str(secrets.get(name, "") or "").strip()
        if value:
            return value
    return ""


def _secret_candidates(slot_name: str, secret_ref: str) -> list[str]:
    rows: list[str] = []
    for candidate in (secret_ref, slot_name):
        text = str(candidate or "").strip()
        if text and text not in rows:
            rows.append(text)
    normalized_slot = str(slot_name or "").strip().lower()
    if normalized_slot == "api_key":
        for name in ("ZHIPU_API_KEY", "BIGMODEL_API_KEY", "API_KEY"):
            if name not in rows:
                rows.append(name)
    upper_slot = str(slot_name or "").strip().upper()
    if upper_slot.endswith("_API_KEY") and upper_slot not in rows:
        rows.append(upper_slot)
    return rows
