# -*- coding: utf-8 -*-
"""Best-effort local token estimation when provider usage is unavailable."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence

from .types import CallUsage
from .utils import compact_json, normalize_text

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_CJK_RE = re.compile(r"[\u3400-\u9fff]")


def estimate_text_tokens(text: Any) -> int:
    raw = normalize_text(text)
    if not raw.strip():
        return 0

    cjk = len(_CJK_RE.findall(raw))
    words = len(_WORD_RE.findall(raw))
    rest = len(raw) - cjk

    # Practical approximation across mixed Chinese/English text.
    estimated = cjk + words + max(0, rest - words) // 4
    return max(1, int(estimated))


def _flatten_content(content: Any) -> str:
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
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(compact_json(item))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if isinstance(content, dict):
        return compact_json(content)
    return str(content)


def _flatten_messages(messages: Sequence[Dict[str, Any]]) -> str:
    rows: List[str] = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", ""))
        rows.append(f"{role}: {_flatten_content(item.get('content'))}")

        tool_calls = item.get("tool_calls") or item.get("toolCalls") or []
        if isinstance(tool_calls, list):
            for call in tool_calls:
                if not isinstance(call, dict):
                    continue
                fn = call.get("function") if isinstance(call.get("function"), dict) else {}
                rows.append(compact_json({"tool_call": fn}))
    return "\n".join(rows)


def estimate_prompt_tokens(
    messages: Sequence[Dict[str, Any]],
    tools: Sequence[Dict[str, Any]] | None = None,
    model_params: Dict[str, Any] | None = None,
) -> int:
    base = estimate_text_tokens(_flatten_messages(messages))
    tools_tokens = estimate_text_tokens(compact_json(list(tools or [])))
    params_tokens = estimate_text_tokens(compact_json(dict(model_params or {})))
    return base + tools_tokens + params_tokens


def estimate_completion_tokens(content: Any, tool_calls: Iterable[Dict[str, Any]] | None = None) -> int:
    base = estimate_text_tokens(_flatten_content(content))
    extra = estimate_text_tokens(compact_json(list(tool_calls or [])))
    return base + extra


def estimate_usage(
    prompts: Sequence[Dict[str, Any]],
    tools: Sequence[Dict[str, Any]] | None,
    model_params: Dict[str, Any] | None,
    response_content: Any,
    response_tool_calls: Iterable[Dict[str, Any]] | None,
) -> CallUsage:
    prompt_tokens = estimate_prompt_tokens(prompts, tools=tools, model_params=model_params)
    completion_tokens = estimate_completion_tokens(response_content, response_tool_calls)
    return CallUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        source="estimated",
    )
