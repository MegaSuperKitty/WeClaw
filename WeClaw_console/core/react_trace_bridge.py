# -*- coding: utf-8 -*-
"""Build ReAct hook bridge for runtime event streaming."""

from __future__ import annotations

from typing import Callable, Dict, Any, Set, Tuple

from core.loop.react_loop import ReActHooks, ReActHookEvent


def build_react_hooks(emit: Callable[[str, Dict[str, Any]], None]) -> ReActHooks:
    """Create ReAct hooks that forward tool traces into SSE events."""

    seen_reason: Set[Tuple[int, str]] = set()

    def _reasoning_content(message: Dict[str, Any]) -> str:
        if not isinstance(message, dict):
            return ""
        return str(message.get("reasoning_content") or "").strip()

    def _before_tool(event: ReActHookEvent):
        message = event.message or {}
        reason = _reasoning_content(message)
        key = (event.step, reason)
        if reason and key not in seen_reason:
            emit(
                "assistant_thinking_delta",
                {
                    "step": event.step,
                    "content": reason,
                    "reasoning_type": "tool",
                },
            )
            emit(
                "assistant_thinking_done",
                {
                    "step": event.step,
                    "reasoning_type": "tool",
                    "keep": True,
                },
            )
            seen_reason.add(key)

        emit(
            "tool_before",
            {
                "step": event.step,
                "tool_name": event.tool_name,
                "arguments": (event.extra or {}).get("arguments", ""),
                "tool_call_id": (event.extra or {}).get("tool_call_id", ""),
            },
        )
        return None

    def _after_tool(event: ReActHookEvent):
        extra = event.extra or {}
        emit(
            "tool_after",
            {
                "step": event.step,
                "tool_name": event.tool_name,
                "tool_call_id": extra.get("tool_call_id", ""),
                "result_preview": extra.get("result_preview", ""),
                "error": bool(extra.get("error", False)),
            },
        )
        return None

    return ReActHooks(before_tool=_before_tool, after_tool=_after_tool)
