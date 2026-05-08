# -*- coding: utf-8 -*-
"""Build model-facing messages from session JSONL events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

from .session_event_types import (
    SESSION_EVENT_MESSAGE,
    SESSION_EVENT_SUMMARY_CHECKPOINT,
)
from .session_jsonl_store import SessionJsonlStore, event_payload


RUNTIME_SYSTEM_MESSAGE_SOURCE = "runtime"
RUNTIME_SYSTEM_MESSAGE_LANGUAGE = "zh"
RUNTIME_SYSTEM_MESSAGE_KIND = "system_message"


def build_request_frame(
    *,
    message_id: str = "",
    content: str,
    user_turn_meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    meta = dict(user_turn_meta or {})
    frame = {
        "id": str(message_id or ""),
        "source": str(meta.get("source") or "web"),
        "preferred_response_language": str(meta.get("preferred_response_language") or "zh"),
        "request_kind": str(meta.get("request_kind") or "user_message"),
        "message_time": str(meta.get("message_time") or ""),
        "content": str(content or ""),
        "attachments": list(meta.get("attachments") or []),
    }
    message_kind = str(meta.get("message_kind") or "").strip()
    if message_kind:
        frame["message_kind"] = message_kind
    referenced_messages = meta.get("referenced_messages")
    if isinstance(referenced_messages, list) and referenced_messages:
        frame["referenced_messages"] = referenced_messages
    return frame


def build_runtime_system_request_frame(*, content: str, message_id: str = "") -> Dict[str, Any]:
    """Build a request frame for runtime-injected control messages."""
    return build_request_frame(
        message_id=message_id,
        content=content,
        user_turn_meta={
            "source": RUNTIME_SYSTEM_MESSAGE_SOURCE,
            "preferred_response_language": RUNTIME_SYSTEM_MESSAGE_LANGUAGE,
            "request_kind": RUNTIME_SYSTEM_MESSAGE_KIND,
            "message_time": "",
            "attachments": [],
        },
    )


def build_model_messages_from_session(*, session_path: str) -> List[Dict[str, Any]]:
    store = SessionJsonlStore(session_path)
    events = store.read_events()
    latest_summary = _latest_summary_checkpoint(events)
    started = latest_summary is None
    messages: List[Dict[str, Any]] = []

    if latest_summary is not None:
        summary_text = str(event_payload(latest_summary).get("summary_text") or "").strip()
        if summary_text:
            frame = build_runtime_system_request_frame(content=f"[SummaryCheckpoint]\n{summary_text}")
            messages.append({"role": "user", "content": json.dumps(frame, ensure_ascii=False)})

    cover_id = str(event_payload(latest_summary or {}).get("covers_until_message_id") or "")
    for event in events:
        if str(event.get("type") or "") != SESSION_EVENT_MESSAGE:
            continue
        payload = event_payload(event)
        message_id = str(payload.get("id") or "")
        if not started:
            if message_id == cover_id:
                started = True
            continue

        role = str(payload.get("role") or "")
        content = str(payload.get("content") or "")
        if role == "user":
            frame = build_request_frame(
                message_id=message_id,
                content=content,
                user_turn_meta=payload.get("user_turn_meta"),
            )
            messages.append({"role": "user", "content": json.dumps(frame, ensure_ascii=False)})
            continue

        item: Dict[str, Any] = {"role": role, "content": content}
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            item["tool_calls"] = tool_calls
        tool_call_id = str(payload.get("tool_call_id") or "")
        if tool_call_id:
            item["tool_call_id"] = tool_call_id
        extras = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
        name = str(payload.get("name") or extras.get("name") or "")
        if name:
            item["name"] = name
        reasoning = str(payload.get("reasoning_content") or extras.get("reasoning_content") or "")
        if reasoning:
            item["reasoning_content"] = reasoning
        messages.append(item)

    return messages


def _latest_summary_checkpoint(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for event in reversed(events):
        if str(event.get("type") or "") == SESSION_EVENT_SUMMARY_CHECKPOINT:
            return event
    return None
