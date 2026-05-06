# -*- coding: utf-8 -*-
"""Persist the frozen base session prompt inside the session JSONL history."""

from __future__ import annotations

from core.history.session_event_types import build_session_prompt_event, iso_timestamp
from core.history.session_jsonl_store import SessionJsonlStore


def _timestamp() -> str:
    return iso_timestamp()


def load_or_build_system_prompt(
    *,
    history_path: str,
    rendered_prompt: str,
    source_hash: str,
    force_refresh: bool = False,
) -> str:
    """Load the saved system prompt or persist a newly rendered one."""
    store = SessionJsonlStore(history_path)
    prompt_event = store.read_last_event("session_prompt")
    saved_prompt = ""
    if prompt_event:
        payload = prompt_event.get("payload") if isinstance(prompt_event.get("payload"), dict) else {}
        saved_prompt = str(payload.get("prompt_text") or "").strip()
    if saved_prompt:
        if force_refresh:
            raise ValueError("session_prompt_frozen")
        return saved_prompt

    prompt = str(rendered_prompt or "").strip()
    store.append_event(
        build_session_prompt_event(
            prompt_text=prompt,
            source_hash=str(source_hash or "").strip(),
            source_parts={
                "highest_priority_runtime_constraints_included": True,
                "soul": "SOUL.md",
                "identity": "IDENTITY.md",
                "user": "USER.md",
                "agent": "AGENT.md",
                "memory": "MEMORY.md",
                "workspace_runtime_included": True,
                "skills_runtime_included": True,
            },
            ts=_timestamp(),
        )
    )
    return prompt
