# -*- coding: utf-8 -*-
"""Replay JSONL session events into console-facing rows."""

from __future__ import annotations

from typing import Any, Dict, List

from .session_event_types import (
    SESSION_EVENT_MESSAGE,
    SESSION_EVENT_SESSION_META,
    SESSION_EVENT_SESSION_PATCH,
)
from .session_jsonl_store import SessionJsonlStore, event_payload


def replay_session_summary(path: str) -> Dict[str, Any]:
    store = SessionJsonlStore(path)
    events = store.read_events()
    created_at = ""
    updated_at = ""
    session_id = store.path.parent.name if store.path.name == "history.jsonl" else store.path.stem
    name = session_id
    agent_id = ""
    user_id = ""
    message_count = 0
    user_count = 0
    assistant_count = 0
    renamed = False

    for event in events:
        ts = str(event.get("ts") or "")
        event_type = str(event.get("type") or "")
        payload = event_payload(event)
        if ts:
            updated_at = ts
        if event_type == SESSION_EVENT_SESSION_META:
            created_at = str(payload.get("created_at") or ts or created_at)
            candidate = str(payload.get("name") or "").strip()
            if candidate:
                name = candidate
            meta_agent_id = str(payload.get("agent_id") or "").strip()
            if meta_agent_id:
                agent_id = meta_agent_id
            meta_user_id = str(payload.get("user_id") or "").strip()
            if meta_user_id:
                user_id = meta_user_id
        elif event_type == SESSION_EVENT_SESSION_PATCH and str(payload.get("patch_kind") or "") == "rename":
            candidate = str(payload.get("name") or "").strip()
            if candidate:
                name = candidate
                renamed = True
        elif event_type == SESSION_EVENT_MESSAGE:
            role = str(payload.get("role") or "")
            message_count += 1
            if role == "user":
                user_count += 1
            elif role == "assistant":
                assistant_count += 1

    return {
        "session_id": session_id,
        "name": name,
        "agent_id": agent_id,
        "user_id": user_id,
        "created_at": created_at,
        "updated_at": updated_at,
        "rounds": min(user_count, assistant_count),
        "message_count": message_count,
        "renamed": renamed,
    }


def replay_render_rows(path: str) -> List[Dict[str, Any]]:
    store = SessionJsonlStore(path)
    rows: List[Dict[str, Any]] = []
    for event in store.iter_events():
        if str(event.get("type") or "") != SESSION_EVENT_MESSAGE:
            continue
        payload = event_payload(event)
        role = str(payload.get("role") or "")
        if role not in {"user", "assistant", "tool", "system"}:
            continue
        row: Dict[str, Any] = {
            "id": str(payload.get("id") or ""),
            "role": role,
            "content": str(payload.get("content") or ""),
            "ts": str(event.get("ts") or ""),
        }
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            row["tool_calls"] = tool_calls
        tool_call_id = str(payload.get("tool_call_id") or "")
        if tool_call_id:
            row["tool_call_id"] = tool_call_id
        user_turn_meta = payload.get("user_turn_meta")
        if isinstance(user_turn_meta, dict) and role == "user":
            row["user_turn_meta"] = user_turn_meta
        extras = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
        reasoning = str(payload.get("reasoning_content") or extras.get("reasoning_content") or "")
        if reasoning:
            row["reasoning_content"] = reasoning
        name = str(payload.get("name") or extras.get("name") or "")
        if name:
            row["name"] = name
        message_origin = str(extras.get("message_origin") or "")
        if message_origin:
            row["message_origin"] = message_origin
        message_kind = str(extras.get("message_kind") or "")
        if message_kind:
            row["message_kind"] = message_kind
        task_ref = extras.get("task_ref")
        if isinstance(task_ref, dict) and task_ref:
            row["task_ref"] = task_ref
        subagent_ref = extras.get("subagent_ref")
        if isinstance(subagent_ref, dict) and subagent_ref:
            row["subagent_ref"] = subagent_ref
        rows.append(row)
    return rows
