# -*- coding: utf-8 -*-
"""Session indexer for scanning workspace-private history files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.history.render_reader import replay_render_rows, replay_session_summary


@dataclass
class SessionSummary:
    agent_id: str
    user_id: str
    channel_prefix: str
    session_name: str
    file_name: str
    file_path: str
    updated_at: str
    created_at: str
    rounds: int
    message_count: int
    is_sub_session: bool


class SessionIndexer:
    """Build metadata views over workspace-private history storage."""

    def __init__(self, history_dir: str):
        self.history_dir = Path(history_dir).resolve()

    def list_sessions(self) -> List[SessionSummary]:
        sessions: List[SessionSummary] = []
        if not self.history_dir.exists():
            return sessions
        for session_dir in self.history_dir.iterdir():
            if not session_dir.is_dir():
                continue
            history_path = session_dir / "history.jsonl"
            if not history_path.is_file():
                continue
            summary = replay_session_summary(str(history_path))
            session_id = session_dir.name
            user_id = str(summary.get("user_id") or "")
            sessions.append(
                SessionSummary(
                    agent_id=str(summary.get("agent_id") or ""),
                    user_id=user_id,
                    channel_prefix=self._channel_prefix(user_id),
                    session_name=str(summary.get("name") or session_id),
                    file_name=session_id,
                    file_path=str(history_path),
                    updated_at=str(summary.get("updated_at") or ""),
                    created_at=str(summary.get("created_at") or ""),
                    rounds=int(summary.get("rounds", 0) or 0),
                    message_count=int(summary.get("message_count", 0) or 0),
                    is_sub_session="-sub" in session_id,
                )
            )
        sessions.sort(key=lambda item: (item.updated_at or "", item.file_name), reverse=True)
        return sessions

    def get_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        path = self.find_session_path(user_id, session_name)
        if not path:
            return []
        return replay_render_rows(path)

    def find_session_path(self, user_id: str, session_name: str) -> Optional[str]:
        _ = user_id
        if not self.history_dir.exists() or not session_name:
            return None
        target = session_name.strip()
        for file_path in self.history_dir.glob("*/history.jsonl"):
            display_name = self._display_name(file_path, {})
            session_id = file_path.parent.name
            if target in {file_path.name, file_path.stem, display_name, session_id}:
                return str(file_path)
        return None

    def _display_name(self, file_path: Path, payload: Any) -> str:
        summary = replay_session_summary(str(file_path))
        name = summary.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
        return file_path.stem

    def _channel_prefix(self, user_id: str) -> str:
        if not user_id:
            return "unknown"
        if ":" not in user_id:
            return "unknown"
        return user_id.split(":", 1)[0] or "unknown"

def split_session_ref(session_ref: str) -> Tuple[str, str]:
    """Split '<user_id>::<session_name>' format."""
    text = (session_ref or "").strip()
    if "::" not in text:
        return "", ""
    user_id, session_name = text.split("::", 1)
    return user_id.strip(), session_name.strip()
