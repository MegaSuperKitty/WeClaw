# -*- coding: utf-8 -*-
"""Unified LLM provider layer for chat completion style calls."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Dict, List, Optional, Sequence, Tuple
import json
import os
import threading
import time
import urllib.error
import urllib.request

from openai import OpenAI

from integrations.metering import get_default_engine
from integrations.metering.token_estimator import estimate_usage


@dataclass(frozen=True)
class LLMConfig:
    provider_kind: str
    provider_name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: Optional[int]
    request_timeout: float = 60.0

    def cache_key(self) -> Tuple[str, str, str, str, str, Optional[int], float]:
        return (
            self.provider_kind,
            self.provider_name,
            self.api_key,
            self.base_url,
            self.model,
            self.max_tokens,
            self.request_timeout,
        )


@dataclass
class LLMFunctionCall:
    name: str
    arguments: str


@dataclass
class LLMToolCall:
    id: str
    type: str
    function: LLMFunctionCall


@dataclass
class LLMMessage:
    content: str
    tool_calls: Optional[List[LLMToolCall]] = None
    reasoning_content: str = ""
    usage_prompt_tokens: Optional[int] = None
    usage_completion_tokens: Optional[int] = None
    usage_total_tokens: Optional[int] = None
    usage_source: str = ""
    response_id: str = ""
    finish_reason: str = ""
    latency_ms: Optional[int] = None


_PROVIDER_CACHE: Dict[Tuple[str, str, str, str, str, Optional[int], float], "_BaseProvider"] = {}

_PROVIDER_API_KEY_ENV: Dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
    "openai_custom": "LLM_API_KEY",
    "anthropic_custom": "LLM_API_KEY",
}

_PROVIDER_DISPLAY_NAME: Dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "dashscope": "DashScope",
    "openai_custom": "OpenAI Compatible Endpoint",
    "anthropic_custom": "Anthropic Compatible Endpoint",
}

_MODEL_TYPE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "openai": {
        "text_generation": "gpt-4o-mini",
        "vision": "gpt-4.1-mini",
        "image_generation": "gpt-image-1",
        "video_generation": "gpt-4.1-mini",
        "speech_to_text": "gpt-4o-mini-transcribe",
        "text_to_speech": "gpt-4o-mini-tts",
        "multimodal_embedding": "text-embedding-3-small",
        "text_embedding": "text-embedding-3-small",
    },
    "anthropic": {
        "text_generation": "claude-3-5-sonnet-latest",
        "vision": "claude-3-5-sonnet-latest",
    },
    "dashscope": {
        "text_generation": "qwen3-max",
        "vision": "qwen-vl-max",
        "image_generation": "wanx2.1-t2i-turbo",
        "speech_to_text": "paraformer-realtime-v2",
        "text_embedding": "text-embedding-v4",
    },
    "openai_custom": {
        "text_generation": "gpt-4o-mini",
        "vision": "gpt-4.1-mini",
        "image_generation": "gpt-image-1",
        "video_generation": "gpt-4.1-mini",
        "speech_to_text": "gpt-4o-mini-transcribe",
        "text_to_speech": "gpt-4o-mini-tts",
        "multimodal_embedding": "text-embedding-3-small",
        "text_embedding": "text-embedding-3-small",
    },
    "anthropic_custom": {
        "text_generation": "claude-3-5-sonnet-latest",
        "vision": "claude-3-5-sonnet-latest",
    },
}

_PROVIDER_MODEL_TYPE_SUPPORTS: Dict[str, List[str]] = {
    "openai": [
        "text_generation",
        "vision",
        "image_generation",
        "video_generation",
        "speech_to_text",
        "text_to_speech",
        "multimodal_embedding",
        "text_embedding",
    ],
    "anthropic": [
        "text_generation",
        "vision",
    ],
    "dashscope": [
        "text_generation",
        "vision",
        "image_generation",
        "speech_to_text",
        "text_embedding",
    ],
    "openai_custom": [
        "text_generation",
        "vision",
        "image_generation",
        "video_generation",
        "speech_to_text",
        "text_to_speech",
        "multimodal_embedding",
        "text_embedding",
    ],
    "anthropic_custom": [
        "text_generation",
        "vision",
    ],
}


def _strip(value: Optional[str]) -> str:
    return (value or "").strip()


def _first_non_empty(*values: Optional[str]) -> str:
    for value in values:
        text = _strip(value)
        if text:
            return text
    return ""


def _parse_int(value: Optional[str]) -> Optional[int]:
    text = _strip(value)
    if not text:
        return None
    try:
        return int(text)
    except Exception:
        return None


def _parse_float(value: Optional[str], default: float) -> float:
    text = _strip(value)
    if not text:
        return default
    try:
        return float(text)
    except Exception:
        return default


def _parse_int_like(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _normalize_provider_name(value: str) -> str:
    text = _strip(value).lower()
    if text in {"anthropic_custom", "anthropic-compatible", "anthropic_compatible"}:
        return "anthropic_custom"
    if text in {"anthropic", "claude"}:
        return "anthropic"
    if text in {"openai_custom", "openai-compatible", "openai_compatible"}:
        return "openai_custom"
    if text in {"dashscope", "qwen"}:
        return "dashscope"
    if text in {"openai", "openai_compatible"}:
        return "openai"
    return ""


def _infer_provider_name(provider_hint: str, base_url: str, api_key: str, model: str) -> str:
    explicit = _normalize_provider_name(provider_hint)
    if explicit:
        return explicit

    clue = " ".join([_strip(base_url).lower(), _strip(model).lower()])
    if "anthropic" in clue or "claude" in clue or _strip(api_key).lower().startswith("sk-ant-"):
        return "anthropic"
    if "dashscope" in clue:
        return "dashscope"
    if "openai" in clue:
        return "openai"

    return "openai"


def _provider_kind(provider_name: str) -> str:
    if provider_name in {"anthropic", "anthropic_custom"}:
        return "anthropic"
    return "openai_compatible"


def provider_api_key_env(provider_name: str) -> str:
    return _PROVIDER_API_KEY_ENV.get(_normalize_provider_name(provider_name), "LLM_API_KEY")


def list_provider_catalog() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for provider_name in ["openai", "anthropic", "dashscope", "openai_custom", "anthropic_custom"]:
        default_base_url = _default_base_url(provider_name)
        rows.append(
            {
                "provider": provider_name,
                "display_name": _PROVIDER_DISPLAY_NAME.get(provider_name, provider_name),
                "api_key_env": provider_api_key_env(provider_name),
                "default_base_url": default_base_url,
                "default_model": _default_model(provider_name, default_base_url),
                "default_models": dict(_MODEL_TYPE_DEFAULTS.get(provider_name, {})),
                "supports": list(_PROVIDER_MODEL_TYPE_SUPPORTS.get(provider_name, ["text_generation"])),
                "is_custom": provider_name in {"openai_custom", "anthropic_custom"},
            }
        )
    return rows


def _default_base_url(provider_name: str) -> str:
    if provider_name == "openai":
        return "https://api.openai.com/v1"
    if provider_name == "anthropic":
        return "https://api.anthropic.com"
    if provider_name == "dashscope":
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if provider_name in {"openai_custom", "anthropic_custom"}:
        return ""
    return "https://api.openai.com/v1"


def _default_model(provider_name: str, base_url: str) -> str:
    lower_url = _strip(base_url).lower()
    if provider_name in {"anthropic", "anthropic_custom"} or "anthropic" in lower_url:
        return "claude-3-5-sonnet-latest"
    if provider_name == "dashscope" or "dashscope" in lower_url:
        return "qwen3-max"
    return "gpt-4o-mini"


def default_model_for_type(provider_name: str, model_type: str, base_url: str = "") -> str:
    normalized_provider = _normalize_provider_name(provider_name) or "openai"
    normalized_type = _strip(model_type) or "text_generation"
    defaults = _MODEL_TYPE_DEFAULTS.get(normalized_provider, {})
    if normalized_type in defaults:
        return defaults[normalized_type]
    return _default_model(normalized_provider, base_url or _default_base_url(normalized_provider))


def provider_supports_model_type(provider_name: str, model_type: str) -> bool:
    normalized_provider = _normalize_provider_name(provider_name) or "openai"
    normalized_type = _strip(model_type) or "text_generation"
    supported = _PROVIDER_MODEL_TYPE_SUPPORTS.get(normalized_provider, ["text_generation"])
    return normalized_type in supported


def resolve_llm_config(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMConfig:
    provider_hint = _first_non_empty(provider, os.getenv("LLM_PROVIDER", ""))
    base_url_hint = _first_non_empty(base_url, os.getenv("LLM_BASE_URL", ""))
    api_key_hint = _first_non_empty(api_key, os.getenv("LLM_API_KEY", ""))
    model_hint = _first_non_empty(model, os.getenv("LLM_MODEL", ""))

    provider_name = _infer_provider_name(provider_hint, base_url_hint, api_key_hint, model_hint)
    # If no explicit hints are given, try provider-specific keys before defaulting.
    if not _strip(provider_hint) and not _strip(base_url_hint) and not _strip(model_hint) and not _strip(api_key_hint):
        for candidate in ["openai", "anthropic", "dashscope"]:
            env_name = provider_api_key_env(candidate)
            if _strip(os.getenv(env_name, "")):
                provider_name = candidate
                break
    provider_kind = _provider_kind(provider_name)

    resolved_base_url = _first_non_empty(base_url, os.getenv("LLM_BASE_URL", ""), _default_base_url(provider_name))
    provider_env_name = provider_api_key_env(provider_name)
    resolved_api_key = _first_non_empty(api_key, os.getenv("LLM_API_KEY", ""), os.getenv(provider_env_name, ""))

    resolved_model = _first_non_empty(model, os.getenv("LLM_MODEL", ""))
    if not resolved_model:
        resolved_model = _default_model(provider_name, resolved_base_url)

    resolved_max_tokens = max_tokens if max_tokens is not None else _parse_int(os.getenv("LLM_MAX_TOKENS", ""))
    if provider_kind == "anthropic" and resolved_max_tokens is None:
        resolved_max_tokens = 2048

    timeout = _parse_float(os.getenv("LLM_TIMEOUT", ""), 60.0)
    return LLMConfig(
        provider_kind=provider_kind,
        provider_name=provider_name,
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        model=resolved_model,
        max_tokens=resolved_max_tokens,
        request_timeout=timeout,
    )


def validate_llm_config(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    config = resolve_llm_config(provider=provider, base_url=base_url, api_key=api_key, model=model)
    if not _strip(config.api_key):
        return "missing api_key (set LLM_API_KEY)"
    return None


def is_llm_configured(
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    return validate_llm_config(provider=provider, base_url=base_url, api_key=api_key, model=model) is None


def _jsonable(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        return str(value)


def _clip_text(value: Any, limit: int = 600) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _tool_calls_to_dict(tool_calls: Optional[List[LLMToolCall]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for call in tool_calls or []:
        if isinstance(call, dict):
            rows.append(_jsonable(call))
            continue
        fn = getattr(call, "function", None)
        rows.append(
            {
                "id": str(getattr(call, "id", "") or ""),
                "type": str(getattr(call, "type", "function") or "function"),
                "function": {
                    "name": str(getattr(fn, "name", "") or ""),
                    "arguments": str(getattr(fn, "arguments", "") or ""),
                },
            }
        )
    return rows


def _resolve_caller() -> Dict[str, Any]:
    try:
        for frame in inspect.stack()[1:]:
            path = os.path.abspath(frame.filename)
            if os.path.abspath(__file__) == path:
                continue
            return {
                "file": path,
                "func": frame.function,
                "line": int(frame.lineno),
            }
    except Exception:
        pass
    return {"file": "", "func": "", "line": 0}


def _resolve_profile_id() -> str:
    return _strip(os.getenv("LLM_PROFILE_ID", ""))


def _metering_enabled() -> bool:
    flag = _strip(os.getenv("MODEL_METERING_ENABLED", "1")).lower()
    return flag not in {"0", "false", "off", "no"}


def _metering_engine():
    if not _metering_enabled():
        return None
    try:
        return get_default_engine()
    except Exception:
        return None


def _sanitize_prompt_messages(messages: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sanitized: List[Dict[str, Any]] = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        clean = dict(item)
        clean.pop("reasoning_content", None)
        sanitized.append(clean)
    return sanitized


def get_response(
    prompts: Sequence[Dict[str, Any]],
    tools: Optional[Sequence[Dict[str, Any]]] = None,
    key_word: str = "",
    stream: bool = False,
    on_token=None,
    on_reasoning=None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> LLMMessage:
    started_at = time.time()
    prompts_list = list(prompts or [])
    sanitized_prompts = _sanitize_prompt_messages(prompts_list)
    tools_list = list(tools or [])
    config = resolve_llm_config(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
    )
    error = validate_llm_config(
        provider=config.provider_name,
        base_url=config.base_url,
        api_key=config.api_key,
        model=config.model,
    )
    if error:
        exc = RuntimeError(f"Invalid LLM config: {error}")
        engine = _metering_engine()
        if engine is not None:
            finished_at = time.time()
            caller = _resolve_caller()
            engine.record_call(
                {
                    "call_id": engine.build_call_id(started_at),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                    "success": False,
                    "latency_ms": int(max(0.0, (finished_at - started_at) * 1000)),
                    "provider": config.provider_name,
                    "provider_kind": config.provider_kind,
                    "model": config.model,
                    "base_url": config.base_url,
                    "profile_id": _resolve_profile_id(),
                    "stream": bool(stream),
                    "key_word": key_word,
                    "message_count": len(sanitized_prompts),
                    "tool_count": len(tools_list),
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "source": "estimated",
                    },
                    "request_payload": {
                        "messages": _jsonable(sanitized_prompts),
                        "tools": _jsonable(tools_list),
                        "model_params": _jsonable(
                            {
                                "temperature": temperature,
                                "top_p": top_p,
                                "max_tokens": max_tokens,
                                "stream": bool(stream),
                                "key_word": key_word,
                            }
                        ),
                    },
                    "response_payload": {
                        "content": "",
                        "tool_calls": [],
                        "reasoning_content": "",
                        "finish_reason": "",
                        "response_id": "",
                    },
                    "input_preview": _clip_text(
                        " ".join(str((m or {}).get("content", "")) for m in sanitized_prompts if isinstance(m, dict))
                    ),
                    "output_preview": "",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "caller_file": caller["file"],
                    "caller_func": caller["func"],
                    "caller_line": caller["line"],
                    "process_id": os.getpid(),
                    "thread_id": threading.get_ident(),
                }
            )
        raise exc

    resolved_temperature = float(temperature) if temperature is not None else _parse_float(os.getenv("LLM_TEMPERATURE", ""), 0.0)
    resolved_top_p = float(top_p) if top_p is not None else _parse_float(os.getenv("LLM_TOP_P", ""), 0.1)
    resolved_model = model or config.model
    resolved_max_tokens = max_tokens if max_tokens is not None else config.max_tokens
    caller = _resolve_caller()
    profile_id = _resolve_profile_id()
    engine = _metering_engine()
    call_id = ""
    if engine is not None:
        try:
            call_id = engine.build_call_id(started_at)
        except Exception:
            call_id = ""

    model_params = {
        "temperature": resolved_temperature,
        "top_p": resolved_top_p,
        "max_tokens": resolved_max_tokens,
        "stream": bool(stream),
        "key_word": key_word,
    }

    backend = _get_provider(config)
    try:
        message = backend.chat(
            prompts=sanitized_prompts,
            tools=tools_list,
            key_word=key_word,
            stream=stream,
            on_token=on_token,
            on_reasoning=on_reasoning,
            temperature=resolved_temperature,
            top_p=resolved_top_p,
            model=resolved_model,
            max_tokens=resolved_max_tokens,
        )
    except Exception as exc:
        finished_at = time.time()
        if engine is not None:
            engine.record_call(
                {
                    "call_id": call_id or engine.build_call_id(started_at),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                    "success": False,
                    "latency_ms": int(max(0.0, (finished_at - started_at) * 1000)),
                    "provider": config.provider_name,
                    "provider_kind": config.provider_kind,
                    "model": resolved_model,
                    "base_url": config.base_url,
                    "profile_id": profile_id,
                    "stream": bool(stream),
                    "key_word": key_word,
                    "message_count": len(sanitized_prompts),
                    "tool_count": len(tools_list),
                    "temperature": resolved_temperature,
                    "top_p": resolved_top_p,
                    "max_tokens": resolved_max_tokens,
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "source": "estimated",
                    },
                    "request_payload": {
                        "messages": _jsonable(sanitized_prompts),
                        "tools": _jsonable(tools_list),
                        "model_params": _jsonable(model_params),
                    },
                    "response_payload": {
                        "content": "",
                        "tool_calls": [],
                        "reasoning_content": "",
                        "finish_reason": "",
                        "response_id": "",
                    },
                    "input_preview": _clip_text(
                        " ".join(str((m or {}).get("content", "")) for m in sanitized_prompts if isinstance(m, dict))
                    ),
                    "output_preview": "",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "caller_file": caller["file"],
                    "caller_func": caller["func"],
                    "caller_line": caller["line"],
                    "process_id": os.getpid(),
                    "thread_id": threading.get_ident(),
                }
            )
        raise

    finished_at = time.time()
    message.latency_ms = int(max(0.0, (finished_at - started_at) * 1000))

    usage_missing = (
        message.usage_prompt_tokens is None
        or message.usage_completion_tokens is None
        or message.usage_total_tokens is None
    )
    if usage_missing:
        estimated = estimate_usage(
            prompts=sanitized_prompts,
            tools=tools_list,
            model_params=model_params,
            response_content=message.content,
            response_tool_calls=_tool_calls_to_dict(message.tool_calls),
        )
        message.usage_prompt_tokens = estimated.prompt_tokens
        message.usage_completion_tokens = estimated.completion_tokens
        message.usage_total_tokens = estimated.total_tokens
        message.usage_source = "estimated"
    else:
        if not message.usage_source:
            message.usage_source = "provider"
        if message.usage_total_tokens is None:
            message.usage_total_tokens = int(message.usage_prompt_tokens or 0) + int(message.usage_completion_tokens or 0)

    if engine is not None:
        engine.record_call(
            {
                "call_id": call_id or engine.build_call_id(started_at),
                "started_at": started_at,
                "finished_at": finished_at,
                "day": time.strftime("%Y-%m-%d", time.localtime(started_at)),
                "success": True,
                "latency_ms": int(message.latency_ms or 0),
                "provider": config.provider_name,
                "provider_kind": config.provider_kind,
                "model": resolved_model,
                "base_url": config.base_url,
                "profile_id": profile_id,
                "stream": bool(stream),
                "key_word": key_word,
                "message_count": len(sanitized_prompts),
                "tool_count": len(tools_list),
                "temperature": resolved_temperature,
                "top_p": resolved_top_p,
                "max_tokens": resolved_max_tokens,
                "usage": {
                    "prompt_tokens": int(message.usage_prompt_tokens or 0),
                    "completion_tokens": int(message.usage_completion_tokens or 0),
                    "total_tokens": int(message.usage_total_tokens or 0),
                    "source": message.usage_source or "estimated",
                },
                "request_payload": {
                    "messages": _jsonable(sanitized_prompts),
                    "tools": _jsonable(tools_list),
                    "model_params": _jsonable(model_params),
                },
                "response_payload": {
                    "content": message.content or "",
                    "tool_calls": _tool_calls_to_dict(message.tool_calls),
                    "reasoning_content": message.reasoning_content or "",
                    "finish_reason": message.finish_reason or "",
                    "response_id": message.response_id or "",
                },
                "input_preview": _clip_text(
                    " ".join(str((m or {}).get("content", "")) for m in sanitized_prompts if isinstance(m, dict))
                ),
                "output_preview": _clip_text(message.content or ""),
                "error_type": "",
                "error_message": "",
                "caller_file": caller["file"],
                "caller_func": caller["func"],
                "caller_line": caller["line"],
                "process_id": os.getpid(),
                "thread_id": threading.get_ident(),
            }
        )

    return message


def _get_provider(config: LLMConfig) -> "_BaseProvider":
    cache_key = config.cache_key()
    cached = _PROVIDER_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if config.provider_kind == "anthropic":
        instance: _BaseProvider = _AnthropicProvider(config)
    else:
        instance = _OpenAICompatibleProvider(config)
    _PROVIDER_CACHE[cache_key] = instance
    return instance


class _BaseProvider:
    def __init__(self, config: LLMConfig):
        self.config = config

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        on_reasoning,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        raise NotImplementedError


class _OpenAICompatibleProvider(_BaseProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        kwargs: Dict[str, Any] = {"api_key": config.api_key}
        if _strip(config.base_url):
            kwargs["base_url"] = config.base_url
        self.client = OpenAI(**kwargs)

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        on_reasoning,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": prompts,
            "stream": bool(stream),
            "temperature": temperature,
            "top_p": top_p,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if key_word:
            payload["stop"] = key_word
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if not stream:
            response = self.client.chat.completions.create(**payload)
            message = response.choices[0].message
            normalized = _normalize_openai_message(message)
            normalized.response_id = _normalize_content_text(getattr(response, "id", ""))
            normalized.finish_reason = _normalize_content_text(getattr(response.choices[0], "finish_reason", ""))
            usage = getattr(response, "usage", None)
            if usage is not None:
                normalized.usage_prompt_tokens = _parse_int_like(getattr(usage, "prompt_tokens", 0))
                normalized.usage_completion_tokens = _parse_int_like(getattr(usage, "completion_tokens", 0))
                normalized.usage_total_tokens = _parse_int_like(getattr(usage, "total_tokens", 0))
                normalized.usage_source = "provider"
            return normalized

        stream_response = self.client.chat.completions.create(**payload)
        text_parts: List[str] = []
        reasoning_parts: List[str] = []
        tool_calls_map: Dict[int, Dict[str, Any]] = {}
        response_id = ""
        finish_reason = ""
        usage_prompt_tokens: Optional[int] = None
        usage_completion_tokens: Optional[int] = None
        usage_total_tokens: Optional[int] = None
        usage_source = ""

        for chunk in stream_response:
            if not response_id:
                response_id = _normalize_content_text(getattr(chunk, "id", ""))
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                usage = getattr(chunk, "usage", None)
                if usage is not None:
                    usage_prompt_tokens = _parse_int_like(getattr(usage, "prompt_tokens", 0))
                    usage_completion_tokens = _parse_int_like(getattr(usage, "completion_tokens", 0))
                    usage_total_tokens = _parse_int_like(getattr(usage, "total_tokens", 0))
                    usage_source = "provider"
                continue

            choice0 = choices[0]
            finish_reason = finish_reason or _normalize_content_text(getattr(choice0, "finish_reason", ""))
            delta = getattr(choice0, "delta", None)
            if delta is None:
                continue

            text_delta = _normalize_content_text(getattr(delta, "content", ""))
            if text_delta:
                text_parts.append(text_delta)
                if on_token:
                    try:
                        on_token(text_delta)
                    except Exception:
                        pass

            reasoning_delta = _normalize_content_text(getattr(delta, "reasoning_content", ""))
            if reasoning_delta:
                reasoning_parts.append(reasoning_delta)
                if on_reasoning:
                    try:
                        on_reasoning(reasoning_delta)
                    except Exception:
                        pass

            for tool_delta in getattr(delta, "tool_calls", None) or []:
                try:
                    idx = int(getattr(tool_delta, "index", 0) or 0)
                except Exception:
                    idx = 0
                row = tool_calls_map.setdefault(
                    idx,
                    {
                        "id": "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    },
                )
                delta_id = _normalize_content_text(getattr(tool_delta, "id", ""))
                if delta_id:
                    row["id"] = delta_id
                delta_type = _normalize_content_text(getattr(tool_delta, "type", ""))
                if delta_type:
                    row["type"] = delta_type
                fn = getattr(tool_delta, "function", None)
                if fn is not None:
                    fn_name = _normalize_content_text(getattr(fn, "name", ""))
                    if fn_name:
                        row["function"]["name"] += fn_name
                    fn_args = _normalize_content_text(getattr(fn, "arguments", ""))
                    if fn_args:
                        row["function"]["arguments"] += fn_args

        normalized_tool_calls: List[LLMToolCall] = []
        for idx in sorted(tool_calls_map.keys()):
            row = tool_calls_map[idx]
            fn = row.get("function") or {}
            normalized_tool_calls.append(
                LLMToolCall(
                    id=str(row.get("id") or f"call_{idx + 1}"),
                    type=str(row.get("type") or "function"),
                    function=LLMFunctionCall(
                        name=str(fn.get("name") or ""),
                        arguments=str(fn.get("arguments") or "{}"),
                    ),
                )
            )

        return LLMMessage(
            content="".join(text_parts),
            tool_calls=normalized_tool_calls or None,
            reasoning_content="".join(reasoning_parts),
            usage_prompt_tokens=usage_prompt_tokens,
            usage_completion_tokens=usage_completion_tokens,
            usage_total_tokens=usage_total_tokens,
            usage_source=usage_source,
            response_id=response_id,
            finish_reason=finish_reason,
        )


class _AnthropicProvider(_BaseProvider):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.endpoint = _build_anthropic_endpoint(config.base_url)

    def chat(
        self,
        prompts: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        key_word: str,
        stream: bool,
        on_token,
        on_reasoning,
        temperature: float,
        top_p: float,
        model: str,
        max_tokens: Optional[int],
    ) -> LLMMessage:
        if stream:
            raise RuntimeError("Anthropic streaming is not implemented in this project.")

        system_text, converted_messages = _to_anthropic_messages(prompts)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": converted_messages,
            "max_tokens": max_tokens or self.config.max_tokens or 2048,
            "temperature": temperature,
            "top_p": top_p,
        }
        if system_text:
            payload["system"] = system_text

        converted_tools = _to_anthropic_tools(tools)
        if converted_tools:
            payload["tools"] = converted_tools

        if key_word:
            payload["stop_sequences"] = [key_word]

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.request_timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Anthropic request failed ({exc.code}): {detail}") from exc
        except Exception as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc

        data = json.loads(raw)
        normalized = _normalize_anthropic_message(data)
        normalized.response_id = _normalize_content_text(data.get("id", ""))
        normalized.finish_reason = _normalize_content_text(data.get("stop_reason", ""))
        usage = data.get("usage", {})
        if isinstance(usage, dict):
            prompt_tokens = _parse_int_like(usage.get("input_tokens", usage.get("prompt_tokens", 0)))
            completion_tokens = _parse_int_like(usage.get("output_tokens", usage.get("completion_tokens", 0)))
            total_tokens = _parse_int_like(usage.get("total_tokens", prompt_tokens + completion_tokens))
            normalized.usage_prompt_tokens = prompt_tokens
            normalized.usage_completion_tokens = completion_tokens
            normalized.usage_total_tokens = total_tokens
            normalized.usage_source = "provider"
        return normalized


def _normalize_openai_message(message: Any) -> LLMMessage:
    content = _normalize_content_text(getattr(message, "content", ""))
    reasoning_content = _normalize_content_text(getattr(message, "reasoning_content", ""))
    tool_calls: List[LLMToolCall] = []
    for index, call in enumerate(getattr(message, "tool_calls", None) or []):
        function = getattr(call, "function", None)
        if function is None:
            continue
        name = _normalize_content_text(getattr(function, "name", ""))
        raw_arguments = getattr(function, "arguments", "")
        arguments = _stringify_arguments(raw_arguments)
        call_id = _normalize_content_text(getattr(call, "id", "")) or f"call_{index + 1}"
        call_type = _normalize_content_text(getattr(call, "type", "function")) or "function"
        tool_calls.append(
            LLMToolCall(
                id=call_id,
                type=call_type,
                function=LLMFunctionCall(name=name, arguments=arguments),
            )
        )
    return LLMMessage(
        content=content,
        tool_calls=tool_calls or None,
        reasoning_content=reasoning_content,
    )


def _normalize_anthropic_message(data: Dict[str, Any]) -> LLMMessage:
    text_parts: List[str] = []
    tool_calls: List[LLMToolCall] = []
    for index, block in enumerate(data.get("content", []) or []):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(_normalize_content_text(block.get("text", "")))
            continue
        if block_type == "tool_use":
            tool_id = _normalize_content_text(block.get("id", "")) or f"toolu_{index + 1}"
            name = _normalize_content_text(block.get("name", ""))
            arguments = _stringify_arguments(block.get("input", {}))
            tool_calls.append(
                LLMToolCall(
                    id=tool_id,
                    type="function",
                    function=LLMFunctionCall(name=name, arguments=arguments),
                )
            )
    return LLMMessage(content="".join(text_parts).strip(), tool_calls=tool_calls or None)


def _normalize_content_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(_normalize_content_text(item.get("text", "")))
                elif "text" in item:
                    parts.append(_normalize_content_text(item.get("text", "")))
        return "".join(parts)
    return str(content)


def _stringify_arguments(arguments: Any) -> str:
    if isinstance(arguments, str):
        return arguments
    if arguments is None:
        return "{}"
    try:
        return json.dumps(arguments, ensure_ascii=False)
    except Exception:
        return str(arguments)


def _to_anthropic_tools(tools: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted: List[Dict[str, Any]] = []
    for item in tools or []:
        if not isinstance(item, dict):
            continue
        if "name" in item and "input_schema" in item:
            converted.append(item)
            continue
        if item.get("type") != "function":
            continue
        fn = item.get("function")
        if not isinstance(fn, dict):
            continue
        name = _normalize_content_text(fn.get("name", ""))
        if not name:
            continue
        schema = fn.get("parameters")
        if not isinstance(schema, dict):
            schema = {"type": "object", "properties": {}}
        converted.append(
            {
                "name": name,
                "description": _normalize_content_text(fn.get("description", "")),
                "input_schema": schema,
            }
        )
    return converted


def _to_anthropic_messages(messages: Sequence[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    system_parts: List[str] = []
    converted: List[Dict[str, Any]] = []

    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = _normalize_content_text(item.get("role", "")).lower()
        if role == "system":
            text = _normalize_content_text(item.get("content", ""))
            if text:
                system_parts.append(text)
            continue

        if role == "tool":
            tool_call_id = _normalize_content_text(item.get("tool_call_id", "")) or "tool_call_id_missing"
            converted.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_call_id,
                            "content": _normalize_content_text(item.get("content", "")),
                        }
                    ],
                }
            )
            continue

        if role == "assistant":
            text = _normalize_content_text(item.get("content", ""))
            tool_calls = item.get("tool_calls") or []
            if tool_calls:
                blocks: List[Dict[str, Any]] = []
                if text:
                    blocks.append({"type": "text", "text": text})
                for index, call in enumerate(tool_calls):
                    call_id, name, arguments = _extract_tool_call(call, index)
                    blocks.append(
                        {
                            "type": "tool_use",
                            "id": call_id,
                            "name": name,
                            "input": _parse_tool_arguments(arguments),
                        }
                    )
                converted.append({"role": "assistant", "content": blocks})
            else:
                converted.append({"role": "assistant", "content": text})
            continue

        converted.append({"role": "user", "content": _normalize_content_text(item.get("content", ""))})

    return "\n\n".join(system_parts).strip(), converted


def _extract_tool_call(call: Any, index: int) -> Tuple[str, str, Any]:
    if isinstance(call, dict):
        fn = call.get("function", {})
        if not isinstance(fn, dict):
            fn = {}
        call_id = _normalize_content_text(call.get("id", "")) or f"call_{index + 1}"
        name = _normalize_content_text(fn.get("name", ""))
        arguments = fn.get("arguments", "{}")
        return call_id, name, arguments

    function = getattr(call, "function", None)
    call_id = _normalize_content_text(getattr(call, "id", "")) or f"call_{index + 1}"
    name = _normalize_content_text(getattr(function, "name", "")) if function is not None else ""
    arguments = getattr(function, "arguments", "{}") if function is not None else "{}"
    return call_id, name, arguments


def _parse_tool_arguments(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {"value": parsed}
        except Exception:
            return {"raw": raw}
    if raw is None:
        return {}
    return {"value": raw}


def _build_anthropic_endpoint(base_url: str) -> str:
    base = _strip(base_url)
    if not base:
        return "https://api.anthropic.com/v1/messages"
    lower = base.lower()
    if lower.endswith("/v1/messages"):
        return base
    if lower.endswith("/v1"):
        return base + "/messages"
    return base.rstrip("/") + "/v1/messages"
