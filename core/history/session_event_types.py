# -*- coding: utf-8 -*-
"""Typed event helpers for session JSONL storage."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


SESSION_EVENT_SESSION_META = "session_meta"
SESSION_EVENT_SESSION_PROMPT = "session_prompt"
SESSION_EVENT_MESSAGE = "message"
SESSION_EVENT_SUMMARY_CHECKPOINT = "summary_checkpoint"
SESSION_EVENT_SESSION_PATCH = "session_patch"
SESSION_EVENT_TASK_CREATED = "task_created"
SESSION_EVENT_TASK_UPDATED = "task_updated"
SESSION_EVENT_TASK_STATUS_CHANGED = "task_status_changed"
SESSION_EVENT_TASK_MESSAGE_ENQUEUED = "task_message_enqueued"
SESSION_EVENT_TASK_RESULT_RECEIVED = "task_result_received"
SESSION_EVENT_TASK_WAITING_HUMAN = "task_waiting_human"
SESSION_EVENT_TASK_CLOSED = "task_closed"


def iso_timestamp() -> str:
    """Return local ISO-8601 timestamp with timezone and seconds precision."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_session_meta_event(
    *,
    session_id: str,
    name: str,
    agent_id: str = "",
    user_id: str = "",
    ts: str | None = None,
) -> Dict[str, Any]:
    event_ts = ts or iso_timestamp()
    payload = {
        "schema_version": 4,
        "format": "weclaw_session_jsonl_v2",
        "session_id": session_id,
        "name": name,
        "created_at": event_ts,
    }
    if str(agent_id or "").strip():
        payload["agent_id"] = str(agent_id).strip()
    if str(user_id or "").strip():
        payload["user_id"] = str(user_id).strip()
    return {
        "ts": event_ts,
        "type": SESSION_EVENT_SESSION_META,
        "payload": payload,
    }


def build_session_prompt_event(
    *,
    prompt_text: str,
    source_hash: str,
    source_parts: Dict[str, Any],
    ts: str | None = None,
) -> Dict[str, Any]:
    return {
        "ts": ts or iso_timestamp(),
        "type": SESSION_EVENT_SESSION_PROMPT,
        "payload": {
            "prompt_kind": "base_session_prompt",
            "frozen": True,
            "source_hash": str(source_hash or ""),
            "prompt_text": str(prompt_text or ""),
            "source_parts": dict(source_parts or {}),
        },
    }


def build_message_event(
    *,
    message_id: str,
    role: str,
    author: str,
    content: str,
    visibility: str = "render_and_context",
    user_turn_meta: Dict[str, Any] | None = None,
    tool_call_id: str = "",
    tool_calls: list | None = None,
    extras: Dict[str, Any] | None = None,
    ts: str | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": message_id,
        "role": str(role or ""),
        "author": str(author or ""),
        "visibility": str(visibility or "render_and_context"),
        "content": str(content or ""),
        "tool_call_id": str(tool_call_id or ""),
        "tool_calls": list(tool_calls or []),
        "extras": dict(extras or {}),
    }
    if user_turn_meta:
        payload["user_turn_meta"] = dict(user_turn_meta)
    return {
        "ts": ts or iso_timestamp(),
        "type": SESSION_EVENT_MESSAGE,
        "payload": payload,
    }


def build_summary_checkpoint_event(
    *,
    summary_id: str,
    summary_text: str,
    covers_until_message_id: str,
    covered_message_count: int,
    ts: str | None = None,
) -> Dict[str, Any]:
    return {
        "ts": ts or iso_timestamp(),
        "type": SESSION_EVENT_SUMMARY_CHECKPOINT,
        "payload": {
            "id": summary_id,
            "summary_format": "weclaw_structured_summary_v1",
            "summary_role": "assistant",
            "summary_text": str(summary_text or ""),
            "covers_until_message_id": str(covers_until_message_id or ""),
            "covered_message_count": int(covered_message_count or 0),
        },
    }


def build_session_patch_event(
    *,
    patch_kind: str,
    patch_payload: Dict[str, Any],
    ts: str | None = None,
) -> Dict[str, Any]:
    payload = {"patch_kind": str(patch_kind or "").strip()}
    payload.update(dict(patch_payload or {}))
    return {
        "ts": ts or iso_timestamp(),
        "type": SESSION_EVENT_SESSION_PATCH,
        "payload": payload,
    }


def build_task_event(
    *,
    event_type: str,
    task_id: str,
    parent_session_id: str,
    status: str = "",
    summary: str = "",
    run_phase: str = "",
    message_kind: str = "",
    payload: Dict[str, Any] | None = None,
    ts: str | None = None,
) -> Dict[str, Any]:
    return {
        "ts": ts or iso_timestamp(),
        "type": str(event_type or "").strip(),
        "payload": {
            "task_id": str(task_id or "").strip(),
            "parent_session_id": str(parent_session_id or "").strip(),
            "status": str(status or "").strip(),
            "summary": str(summary or "").strip(),
            "run_phase": str(run_phase or "").strip(),
            "message_kind": str(message_kind or "").strip(),
            "payload": dict(payload or {}),
        },
    }
