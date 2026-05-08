# -*- coding: utf-8 -*-
"""Search workspace history files for lightweight MCP lookup."""

from __future__ import annotations

import json
import os

from core.history.context_builder import build_model_messages_from_session
from core.history.render_reader import replay_session_summary


class WorkspaceHistorySearchService:
    """Search session history payloads stored under one workspace history root."""

    def __init__(self, history_root: str):
        self.history_root = os.path.abspath(history_root)

    def query(self, text: str, limit: int = 5, session_name: str = "", user_id: str = "") -> list[dict[str, object]]:
        """Return matching excerpts from workspace history files."""
        needle = str(text or "").strip().lower()
        if not needle:
            return []
        max_results = max(1, min(int(limit or 5), 20))
        target_session = str(session_name or "").strip()
        target_user = str(user_id or "").strip()
        results: list[dict[str, object]] = []

        for path in self._iter_history_files(target_user):
            payload = self._load_payload(path)
            if not payload and not path.endswith(".jsonl"):
                continue
            session_id = self._session_id_from_path(path)
            display_name = str(payload.get("name") or session_id)
            summary_user_id = self._user_id_from_path(path)
            if target_user and target_user != summary_user_id:
                continue
            if target_session and target_session not in {session_id, display_name, os.path.basename(path)}:
                continue
            messages = self._extract_messages(path, payload)
            for index, message in enumerate(messages):
                if not isinstance(message, dict):
                    continue
                content = str(message.get("content") or "")
                lowered = content.lower()
                if needle not in lowered:
                    continue
                results.append(
                    {
                        "session_id": session_id,
                        "session_name": display_name,
                        "history_file": path,
                        "matched_role": str(message.get("role") or ""),
                        "matched_excerpt": self._build_excerpt(content, lowered.index(needle), len(needle)),
                        "message_index": index,
                        "updated_at": str(payload.get("updated_at") or ""),
                        "user_id": summary_user_id,
                    }
                )
                if len(results) >= max_results:
                    return results
        return results

    def _iter_history_files(self, user_id: str):
        if not os.path.isdir(self.history_root):
            return []
        paths: list[str] = []
        for root, _, files in os.walk(self.history_root):
            for name in sorted(files):
                if name == "state.json":
                    continue
                if name.endswith(".json") or name == "history.jsonl":
                    path = os.path.join(root, name)
                    normalized = os.path.abspath(path)
                    marker = f"{os.sep}task_state{os.sep}tasks{os.sep}"
                    if marker in normalized:
                        continue
                    paths.append(path)
        return paths

    def _user_id_from_path(self, path: str) -> str:
        normalized = os.path.abspath(path)
        if os.path.basename(normalized).lower() == "history.jsonl":
            summary = replay_session_summary(normalized)
            return str(summary.get("user_id") or "")
        return os.path.basename(os.path.dirname(normalized))

    def _extract_messages(self, path: str, payload: dict[str, object]) -> list[dict[str, object]]:
        if path.endswith(".jsonl"):
            messages = build_model_messages_from_session(session_path=path)
            rows: list[dict[str, object]] = []
            for item in messages:
                role = str(item.get("role") or "")
                content = str(item.get("content") or "")
                if role == "user":
                    try:
                        parsed = json.loads(content)
                        content = str(parsed.get("content") or "")
                    except Exception:
                        pass
                rows.append({"role": role, "content": content})
            return rows
        messages = payload.get("messages") or []
        return messages if isinstance(messages, list) else []

    def _load_payload(self, path: str) -> dict[str, object]:
        if path.endswith(".jsonl"):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _session_id_from_path(self, path: str) -> str:
        normalized = os.path.abspath(path)
        if os.path.basename(normalized).lower() == "history.jsonl":
            return os.path.basename(os.path.dirname(normalized)) or "default"
        return os.path.splitext(os.path.basename(normalized))[0]

    def _build_excerpt(self, content: str, start: int, length: int) -> str:
        left = max(0, start - 60)
        right = min(len(content), start + length + 80)
        excerpt = content[left:right].replace("\n", " ").strip()
        if left > 0:
            excerpt = "..." + excerpt
        if right < len(content):
            excerpt = excerpt + "..."
        return excerpt
