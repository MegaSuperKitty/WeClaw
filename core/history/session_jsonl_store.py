# -*- coding: utf-8 -*-
"""Append-only JSONL storage for session events."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
import json

from .session_event_types import (
    SESSION_EVENT_MESSAGE,
    SESSION_EVENT_SESSION_META,
    SESSION_EVENT_SESSION_PATCH,
    SESSION_EVENT_SUMMARY_CHECKPOINT,
    build_session_meta_event,
)


class SessionJsonlStore:
    """Read and append session events."""

    def __init__(self, session_path: str):
        self.path = Path(session_path).resolve()

    def ensure_created(
        self,
        *,
        session_id: str,
        session_name: str,
        agent_id: str = "",
        user_id: str = "",
        ts: str | None = None,
    ) -> None:
        if self.path.exists() and self.path.stat().st_size > 0:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.append_event(
            build_session_meta_event(
                session_id=session_id,
                name=session_name,
                agent_id=agent_id,
                user_id=user_id,
                ts=ts,
            )
        )

    def append_event(self, event: Dict[str, Any]) -> None:
        append_jsonl_line(str(self.path), event)

    def read_events(self) -> List[Dict[str, Any]]:
        return read_jsonl_events(str(self.path))

    def iter_events(self) -> Iterator[Dict[str, Any]]:
        yield from self.read_events()

    def iter_events_reverse(self) -> Iterator[Dict[str, Any]]:
        yield from iter_jsonl_events_reverse(str(self.path))

    def read_last_event(self, event_type: str) -> Optional[Dict[str, Any]]:
        for event in self.iter_events_reverse():
            if str(event.get("type") or "") == event_type:
                return event
        return None

    def has_event_type(self, event_type: str) -> bool:
        return self.read_last_event(event_type) is not None

    def next_message_id(self) -> str:
        count = 0
        for event in self.iter_events():
            if str(event.get("type") or "") == SESSION_EVENT_MESSAGE:
                count += 1
        return f"msg_{count + 1:06d}"

    def next_summary_id(self) -> str:
        count = 0
        for event in self.iter_events():
            if str(event.get("type") or "") == SESSION_EVENT_SUMMARY_CHECKPOINT:
                count += 1
        return f"sum_{count + 1:06d}"

    def latest_session_name(self) -> str:
        default_name = self.path.stem
        name = default_name
        for event in self.iter_events():
            event_type = str(event.get("type") or "")
            payload = event_payload(event)
            if event_type == SESSION_EVENT_SESSION_META:
                candidate = str(payload.get("name") or "").strip()
                if candidate:
                    name = candidate
            elif event_type == SESSION_EVENT_SESSION_PATCH and str(payload.get("patch_kind") or "") == "rename":
                candidate = str(payload.get("name") or "").strip()
                if candidate:
                    name = candidate
        return name


def read_jsonl_events(path: str) -> List[Dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    events: List[Dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            if isinstance(data, dict):
                events.append(data)
    return events


def iter_jsonl_events_reverse(path: str) -> Iterator[Dict[str, Any]]:
    events = read_jsonl_events(path)
    for event in reversed(events):
        yield event


def append_jsonl_line(path: str, event: Dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(event, ensure_ascii=False)
    with file_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)
        handle.write("\n")


def event_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}
