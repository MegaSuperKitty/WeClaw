# -*- coding: utf-8 -*-
"""Typed model profile manager for runtime secrets-backed config."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import yaml

from integrations.llm.provider import (
    default_model_for_type,
    get_response,
    list_provider_catalog,
    provider_api_key_env,
    provider_supports_model_type,
    validate_llm_config,
)


TEXT_MODEL_TYPE = "text_generation"
MODEL_TYPE_ORDER = [
    TEXT_MODEL_TYPE,
    "vision",
    "image_generation",
    "video_generation",
    "speech_to_text",
    "text_to_speech",
    "multimodal_embedding",
    "text_embedding",
]
MODEL_TYPE_LABELS = {
    TEXT_MODEL_TYPE: "Text Generation",
    "vision": "Vision",
    "image_generation": "Image Generation",
    "video_generation": "Video Generation",
    "speech_to_text": "Speech to Text",
    "text_to_speech": "Text to Speech",
    "multimodal_embedding": "Multimodal Embedding",
    "text_embedding": "Text Embedding",
}
MODEL_TYPE_ALIASES = {
    "chat": TEXT_MODEL_TYPE,
    "llm": TEXT_MODEL_TYPE,
    "text": TEXT_MODEL_TYPE,
    "vision_understanding": "vision",
    "image": "image_generation",
    "video": "video_generation",
    "asr": "speech_to_text",
    "stt": "speech_to_text",
    "tts": "text_to_speech",
    "multimodal_vector": "multimodal_embedding",
    "text_vector": "text_embedding",
}


@dataclass
class TypedModelProfile:
    model_type: str
    profile_id: str
    provider: str
    base_url: str
    model: str
    api_key: str
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


def _mask_secret(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if len(text) <= 8:
        return "*" * len(text)
    return f"{text[:3]}{'*' * (len(text) - 6)}{text[-3:]}"


def _normalize_model_type(model_type: str) -> str:
    text = (model_type or "").strip().lower()
    if not text:
        return TEXT_MODEL_TYPE
    text = MODEL_TYPE_ALIASES.get(text, text)
    if text in MODEL_TYPE_LABELS:
        return text
    return TEXT_MODEL_TYPE


def _parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except Exception:
        return None


def _parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def load_model_types_snapshot(secrets_path: str) -> Dict[str, Any]:
    manager = ModelConfigManager(secrets_path)
    return manager.get_state()


class ModelConfigManager:
    """Persist and apply typed model profiles backed by runtime secrets yaml."""

    def __init__(self, secrets_path: str):
        self.secrets_path = Path(secrets_path).resolve()
        self._lock = threading.Lock()
        self._catalog = list_provider_catalog()
        self._provider_map = {row["provider"]: row for row in self._catalog}
        self._connectivity_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            return self._build_state_locked(typed)

    def apply_active_profile(self, model_type: str = TEXT_MODEL_TYPE) -> Dict[str, Any]:
        normalized_type = _normalize_model_type(model_type)
        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            active_id = typed.get("active", {}).get(normalized_type, "")
            active = typed.get("profiles", {}).get(normalized_type, {}).get(active_id)
            if active and normalized_type == TEXT_MODEL_TYPE:
                self._apply_text_generation_env_locked(active)
            return self._build_state_locked(typed)

    def upsert_profile(
        self,
        profile_id: str,
        provider: str,
        base_url: str = "",
        model: str = "",
        api_key: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        clear_api_key: bool = False,
        model_type: str = TEXT_MODEL_TYPE,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")

        normalized_type = _normalize_model_type(model_type)
        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)

            active_by_type = typed["active"]
            profiles_by_type = typed["profiles"]
            type_profiles = profiles_by_type.setdefault(normalized_type, {})
            existing = type_profiles.get(pid)
            normalized_provider = self._normalize_provider(provider)
            self._validate_provider_for_model_type(normalized_provider, normalized_type)
            preset = self._provider_map.get(normalized_provider, self._provider_map["openai"])

            base = (base_url or "").strip()
            if not base and existing:
                base = existing.base_url
            if not base and not preset.get("is_custom"):
                base = str(preset.get("default_base_url") or "").strip()
            if self._provider_requires_custom_base_url(normalized_provider) and not base:
                raise ValueError("base_url is required for custom provider")

            model_name = (model or "").strip()
            if not model_name and existing:
                model_name = existing.model
            if not model_name:
                model_name = default_model_for_type(normalized_provider, normalized_type, base)

            if clear_api_key:
                key_value = ""
            elif api_key is None:
                key_value = existing.api_key if existing else ""
            else:
                key_value = (api_key or "").strip() or (existing.api_key if existing else "")

            if not key_value:
                raise ValueError("api_key is required")

            profile = TypedModelProfile(
                model_type=normalized_type,
                profile_id=pid,
                provider=normalized_provider,
                base_url=base,
                model=model_name,
                api_key=key_value,
                max_tokens=max_tokens if max_tokens is not None else (existing.max_tokens if existing else None),
                timeout=timeout if timeout is not None else (existing.timeout if existing else None),
                temperature=temperature if temperature is not None else (existing.temperature if existing else None),
                top_p=top_p if top_p is not None else (existing.top_p if existing else None),
                extra=dict(extra or (existing.extra if existing else {})),
            )
            type_profiles[pid] = profile
            self._connectivity_cache.setdefault(normalized_type, {}).pop(pid, None)
            if not active_by_type.get(normalized_type):
                active_by_type[normalized_type] = pid

            self._write_back_locked(data, active_by_type, profiles_by_type)
            self._save_yaml_locked(data)
            return self._build_state_locked({"active": active_by_type, "profiles": profiles_by_type})

    def activate_profile(self, profile_id: str, model_type: str = TEXT_MODEL_TYPE) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")
        normalized_type = _normalize_model_type(model_type)

        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            type_profiles = typed["profiles"].get(normalized_type, {})
            if pid not in type_profiles:
                raise ValueError("profile not found")
            typed["active"][normalized_type] = pid
            self._write_back_locked(data, typed["active"], typed["profiles"])
            self._save_yaml_locked(data)
            return self._build_state_locked(typed)

    def delete_profile(self, profile_id: str, model_type: str = TEXT_MODEL_TYPE) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")
        normalized_type = _normalize_model_type(model_type)

        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            type_profiles = typed["profiles"].setdefault(normalized_type, {})
            if pid not in type_profiles:
                raise ValueError("profile not found")
            type_profiles.pop(pid, None)
            self._connectivity_cache.setdefault(normalized_type, {}).pop(pid, None)
            if not type_profiles:
                if normalized_type == TEXT_MODEL_TYPE:
                    fallback = self._build_default_text_generation_profile(data)
                    type_profiles[fallback.profile_id] = fallback
                    typed["active"][normalized_type] = fallback.profile_id
                else:
                    typed["active"][normalized_type] = ""
            elif typed["active"].get(normalized_type) == pid:
                typed["active"][normalized_type] = next(iter(type_profiles.keys()))
            self._write_back_locked(data, typed["active"], typed["profiles"])
            self._save_yaml_locked(data)
            return self._build_state_locked(typed)

    def test_profile_connectivity(self, profile_id: str, model_type: str = TEXT_MODEL_TYPE) -> Dict[str, Any]:
        pid = (profile_id or "").strip()
        if not pid:
            raise ValueError("profile_id is required")
        normalized_type = _normalize_model_type(model_type)

        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            target = typed["profiles"].get(normalized_type, {}).get(pid)
            if target is None:
                raise ValueError("profile not found")

        status = "failed"
        detail = ""
        try:
            if normalized_type == TEXT_MODEL_TYPE:
                response = get_response(
                    prompts=[
                        {"role": "system", "content": "You are a connectivity probe."},
                        {"role": "user", "content": "hello"},
                    ],
                    tools=None,
                    stream=False,
                    provider=target.provider,
                    base_url=target.base_url,
                    api_key=target.api_key,
                    model=target.model,
                    max_tokens=64,
                    temperature=target.temperature,
                    top_p=target.top_p,
                )
                detail = (response.content or "").strip()[:200]
            else:
                self._validate_profile_runtime(target)
                detail = "validated_by_config"
            status = "success"
        except Exception as exc:
            detail = str(exc)

        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            if pid in typed["profiles"].get(normalized_type, {}):
                self._connectivity_cache.setdefault(normalized_type, {})[pid] = {
                    "status": status,
                    "detail": detail,
                    "checked_at": int(time.time()),
                }
            return self._build_state_locked(typed)

    def get_model_type_availability(self, model_type: str) -> Dict[str, Any]:
        normalized_type = _normalize_model_type(model_type)
        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            return self._compute_model_type_availability_locked(normalized_type, typed)

    def resolve_active_profile(self, model_type: str) -> Optional[TypedModelProfile]:
        normalized_type = _normalize_model_type(model_type)
        with self._lock:
            data = self._read_yaml_locked()
            typed = self._load_typed_profiles_locked(data)
            active_id = typed["active"].get(normalized_type, "")
            return typed["profiles"].get(normalized_type, {}).get(active_id)

    # ---- Internal helpers ----

    def _read_yaml_locked(self) -> Dict[str, Any]:
        if not self.secrets_path.is_file():
            return {}
        try:
            raw = yaml.safe_load(self.secrets_path.read_text(encoding="utf-8")) or {}
            return raw if isinstance(raw, dict) else {}
        except Exception:
            return {}

    def _save_yaml_locked(self, data: Dict[str, Any]) -> None:
        self.secrets_path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        self.secrets_path.write_text(text, encoding="utf-8")

    def _normalize_provider(self, provider: str) -> str:
        text = (provider or "").strip().lower()
        aliases = {
            "claude": "anthropic",
            "qwen": "dashscope",
            "openai_compatible": "openai_custom",
            "openai-compatible": "openai_custom",
            "anthropic_compatible": "anthropic_custom",
            "anthropic-compatible": "anthropic_custom",
        }
        text = aliases.get(text, text)
        if text in self._provider_map:
            return text
        return "openai"

    def _provider_requires_custom_base_url(self, provider: str) -> bool:
        return provider in {"openai_custom", "anthropic_custom"}

    def _validate_provider_for_model_type(self, provider: str, model_type: str) -> None:
        if not provider_supports_model_type(provider, model_type):
            raise ValueError(f"provider {provider} does not support model_type {model_type}")

    def _build_default_text_generation_profile(self, data: Dict[str, Any]) -> TypedModelProfile:
        provider = self._normalize_provider(str(data.get("LLM_PROVIDER", "")).strip() or "openai")
        preset = self._provider_map.get(provider, self._provider_map["openai"])
        env_key = provider_api_key_env(provider)
        api_key = str(data.get("LLM_API_KEY", "") or "").strip() or str(data.get(env_key, "") or "").strip()
        base_url = str(data.get("LLM_BASE_URL", "") or "").strip() or str(preset.get("default_base_url") or "").strip()
        model = str(data.get("LLM_MODEL", "") or "").strip() or default_model_for_type(provider, TEXT_MODEL_TYPE, base_url)
        return TypedModelProfile(
            model_type=TEXT_MODEL_TYPE,
            profile_id="default",
            provider=provider,
            base_url=base_url,
            model=model,
            api_key=api_key,
            max_tokens=_parse_int(data.get("LLM_MAX_TOKENS")),
            timeout=_parse_float(data.get("LLM_TIMEOUT")),
            temperature=_parse_float(data.get("LLM_TEMPERATURE")),
            top_p=_parse_float(data.get("LLM_TOP_P")),
        )

    def _load_typed_profiles_locked(self, data: Dict[str, Any]) -> Dict[str, Any]:
        typed_node = data.get("MODEL_TYPES", {})
        active_by_type: Dict[str, str] = {model_type: "" for model_type in MODEL_TYPE_ORDER}
        profiles_by_type: Dict[str, Dict[str, TypedModelProfile]] = {model_type: {} for model_type in MODEL_TYPE_ORDER}

        if isinstance(typed_node, dict):
            types_node = typed_node.get("types", {})
            if isinstance(types_node, dict):
                for raw_type, bucket in types_node.items():
                    normalized_type = _normalize_model_type(str(raw_type))
                    if not isinstance(bucket, dict):
                        continue
                    active_by_type[normalized_type] = str(bucket.get("active", "") or "").strip()
                    raw_profiles = bucket.get("profiles", {})
                    if not isinstance(raw_profiles, dict):
                        continue
                    for pid, row in raw_profiles.items():
                        if not isinstance(row, dict):
                            continue
                        profile_id = str(pid or "").strip()
                        if not profile_id:
                            continue
                        provider = self._normalize_provider(str(row.get("provider", "")).strip() or "openai")
                        preset = self._provider_map.get(provider, self._provider_map["openai"])
                        base_url = str(row.get("base_url", "") or "").strip()
                        if not base_url and not preset.get("is_custom"):
                            base_url = str(preset.get("default_base_url") or "").strip()
                        model_name = str(row.get("model", "") or "").strip() or default_model_for_type(provider, normalized_type, base_url)
                        profile = TypedModelProfile(
                            model_type=normalized_type,
                            profile_id=profile_id,
                            provider=provider,
                            base_url=base_url,
                            model=model_name,
                            api_key=str(row.get("api_key", "") or "").strip(),
                            max_tokens=_parse_int(row.get("max_tokens")),
                            timeout=_parse_float(row.get("timeout")),
                            temperature=_parse_float(row.get("temperature")),
                            top_p=_parse_float(row.get("top_p")),
                            extra=dict(row.get("extra") or {}),
                        )
                        profiles_by_type[normalized_type][profile_id] = profile

        if not profiles_by_type[TEXT_MODEL_TYPE]:
            default_profile = self._build_default_text_generation_profile(data)
            profiles_by_type[TEXT_MODEL_TYPE][default_profile.profile_id] = default_profile
            if not active_by_type[TEXT_MODEL_TYPE]:
                active_by_type[TEXT_MODEL_TYPE] = default_profile.profile_id

        for model_type, type_profiles in profiles_by_type.items():
            active_id = active_by_type.get(model_type, "")
            if active_id not in type_profiles:
                active_by_type[model_type] = next(iter(type_profiles.keys())) if type_profiles else ""

        return {"active": active_by_type, "profiles": profiles_by_type}

    def _write_back_locked(
        self,
        data: Dict[str, Any],
        active_by_type: Dict[str, str],
        profiles_by_type: Dict[str, Dict[str, TypedModelProfile]],
    ) -> None:
        typed_node: Dict[str, Any] = {"types": {}}
        for model_type in MODEL_TYPE_ORDER:
            profile_map: Dict[str, Any] = {}
            for pid, row in profiles_by_type.get(model_type, {}).items():
                profile_map[pid] = {
                    "provider": row.provider,
                    "base_url": row.base_url,
                    "model": row.model,
                    "api_key": row.api_key,
                    "max_tokens": row.max_tokens,
                    "timeout": row.timeout,
                    "temperature": row.temperature,
                    "top_p": row.top_p,
                    "extra": dict(row.extra or {}),
                }
            typed_node["types"][model_type] = {
                "active": active_by_type.get(model_type, ""),
                "profiles": profile_map,
            }
        data["MODEL_TYPES"] = typed_node

        active_text_id = active_by_type.get(TEXT_MODEL_TYPE, "")
        active_text_profile = profiles_by_type.get(TEXT_MODEL_TYPE, {}).get(active_text_id)
        if active_text_profile:
            self._write_legacy_text_generation_fields(data, active_text_profile)
            self._apply_text_generation_env_locked(active_text_profile)

    def _write_legacy_text_generation_fields(self, data: Dict[str, Any], active: TypedModelProfile) -> None:
        profile_map: Dict[str, Any] = {}
        for pid, row in self._load_typed_profiles_locked(data)["profiles"].get(TEXT_MODEL_TYPE, {}).items():
            profile_map[pid] = {
                "provider": row.provider,
                "base_url": row.base_url,
                "model": row.model,
                "api_key": row.api_key,
                "max_tokens": row.max_tokens,
                "timeout": row.timeout,
                "temperature": row.temperature,
                "top_p": row.top_p,
            }
        data["LLM_PROFILES"] = {"active": active.profile_id, "profiles": profile_map}
        data["LLM_PROVIDER"] = active.provider
        data["LLM_PROFILE_ID"] = active.profile_id
        data["LLM_BASE_URL"] = active.base_url
        data["LLM_MODEL"] = active.model
        data["LLM_API_KEY"] = active.api_key
        data["LLM_MAX_TOKENS"] = "" if active.max_tokens is None else active.max_tokens
        data["LLM_TIMEOUT"] = "" if active.timeout is None else active.timeout
        data["LLM_TEMPERATURE"] = "" if active.temperature is None else active.temperature
        data["LLM_TOP_P"] = "" if active.top_p is None else active.top_p
        provider_env = provider_api_key_env(active.provider)
        data[provider_env] = active.api_key

    def _apply_text_generation_env_locked(self, active: TypedModelProfile) -> None:
        os.environ["LLM_PROVIDER"] = active.provider
        os.environ["LLM_PROFILE_ID"] = active.profile_id
        os.environ["LLM_BASE_URL"] = active.base_url
        os.environ["LLM_MODEL"] = active.model
        os.environ["LLM_API_KEY"] = active.api_key
        if active.max_tokens is None:
            os.environ.pop("LLM_MAX_TOKENS", None)
        else:
            os.environ["LLM_MAX_TOKENS"] = str(active.max_tokens)
        if active.timeout is None:
            os.environ.pop("LLM_TIMEOUT", None)
        else:
            os.environ["LLM_TIMEOUT"] = str(active.timeout)
        if active.temperature is None:
            os.environ.pop("LLM_TEMPERATURE", None)
        else:
            os.environ["LLM_TEMPERATURE"] = str(active.temperature)
        if active.top_p is None:
            os.environ.pop("LLM_TOP_P", None)
        else:
            os.environ["LLM_TOP_P"] = str(active.top_p)
        provider_env = provider_api_key_env(active.provider)
        if active.api_key:
            os.environ[provider_env] = active.api_key

    def _validate_profile_runtime(self, profile: TypedModelProfile) -> None:
        if not profile_supports_model_type(profile, profile.model_type):
            raise ValueError(f"provider {profile.provider} does not support model_type {profile.model_type}")
        if self._provider_requires_custom_base_url(profile.provider) and not profile.base_url:
            raise ValueError("missing_base_url")
        if not profile.model.strip():
            raise ValueError("missing_model")
        if not profile.api_key.strip():
            raise ValueError("missing_api_key")

    def _compute_model_type_availability_locked(self, model_type: str, typed: Dict[str, Any]) -> Dict[str, Any]:
        active_id = typed["active"].get(model_type, "")
        if not active_id:
            return {"model_type": model_type, "available": False, "detail": f"missing_active_profile:{model_type}"}
        profile = typed["profiles"].get(model_type, {}).get(active_id)
        if profile is None:
            return {"model_type": model_type, "available": False, "detail": f"missing_active_profile:{model_type}"}
        try:
            self._validate_profile_runtime(profile)
        except Exception as exc:
            return {"model_type": model_type, "available": False, "detail": str(exc)}
        return {"model_type": model_type, "available": True, "detail": "ok"}

    def _build_runtime_info(self, model_type: str, profile: TypedModelProfile) -> Dict[str, Any]:
        valid = True
        error = ""
        if model_type == TEXT_MODEL_TYPE:
            error = validate_llm_config(
                provider=profile.provider,
                base_url=profile.base_url,
                api_key=profile.api_key,
                model=profile.model,
            ) or ""
            valid = not bool(error)
        else:
            availability = self._compute_model_type_availability_locked(model_type, {"active": {model_type: profile.profile_id}, "profiles": {model_type: {profile.profile_id: profile}}})
            valid = bool(availability.get("available"))
            error = "" if valid else str(availability.get("detail") or "")
        return {
            "model_type": model_type,
            "provider": profile.provider,
            "base_url": profile.base_url,
            "model": profile.model,
            "api_key_masked": _mask_secret(profile.api_key),
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "valid": valid,
            "error": error,
        }

    def _build_state_locked(self, typed: Dict[str, Any]) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        model_type_rows: List[Dict[str, Any]] = []
        runtime_by_type: Dict[str, Any] = {}

        for model_type in MODEL_TYPE_ORDER:
            type_profiles = typed["profiles"].get(model_type, {})
            active_id = typed["active"].get(model_type, "")
            availability = self._compute_model_type_availability_locked(model_type, typed)
            type_profile_rows: List[Dict[str, Any]] = []
            for pid, row in sorted(type_profiles.items()):
                connectivity = self._connectivity_cache.get(model_type, {}).get(
                    pid,
                    {"status": "untested", "detail": "", "checked_at": None},
                )
                rendered = {
                    "model_type": model_type,
                    "profile_id": pid,
                    "provider": row.provider,
                    "display_name": self._provider_map.get(row.provider, {}).get("display_name", row.provider),
                    "base_url": row.base_url,
                    "model": row.model,
                    "max_tokens": row.max_tokens,
                    "timeout": row.timeout,
                    "temperature": row.temperature,
                    "top_p": row.top_p,
                    "has_api_key": bool((row.api_key or "").strip()),
                    "api_key_masked": _mask_secret(row.api_key),
                    "active": pid == active_id,
                    "connectivity_status": connectivity.get("status", "untested"),
                    "connectivity_detail": connectivity.get("detail", ""),
                    "connectivity_checked_at": connectivity.get("checked_at"),
                }
                rows.append(rendered)
                type_profile_rows.append(rendered)
                if pid == active_id:
                    runtime_by_type[model_type] = self._build_runtime_info(model_type, row)

            model_type_rows.append(
                {
                    "model_type": model_type,
                    "display_name": MODEL_TYPE_LABELS.get(model_type, model_type),
                    "active_profile_id": active_id,
                    "profile_count": len(type_profiles),
                    "configured": bool(type_profiles),
                    "authorized": any(item["has_api_key"] for item in type_profile_rows),
                    "available": bool(availability.get("available")),
                    "availability_detail": str(availability.get("detail") or ""),
                    "profiles": type_profile_rows,
                }
            )

        provider_rows: List[Dict[str, Any]] = []
        for item in self._catalog:
            provider_name = item["provider"]
            matched = [p for p in rows if p["provider"] == provider_name]
            provider_rows.append(
                {
                    **item,
                    "authorized": any(p["has_api_key"] for p in matched),
                    "active": any(p["active"] for p in matched),
                    "profile_count": len(matched),
                }
            )

        return {
            "success": True,
            "active_profile_id": typed["active"].get(TEXT_MODEL_TYPE, ""),
            "active_profiles": dict(typed["active"]),
            "profiles": rows,
            "model_types": model_type_rows,
            "providers": provider_rows,
            "runtime": runtime_by_type,
            "runtime_current": runtime_by_type.get(TEXT_MODEL_TYPE, {}),
        }


def profile_supports_model_type(profile: TypedModelProfile, model_type: str) -> bool:
    return provider_supports_model_type(profile.provider, model_type)
