# -*- coding: utf-8 -*-
"""Session routing for WeClaw agent runtime."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import re
import tempfile
import threading

from core.history.render_reader import replay_session_summary
from core.history.session_event_types import build_session_patch_event, iso_timestamp
from core.history.session_jsonl_store import SessionJsonlStore
from core.task_runtime.plan_file import ensure_plan_file


def _timestamp() -> str:
    return iso_timestamp().replace("-", "").replace(":", "").replace("T", "_")[:15]


class SessionManager:
    """Manage session file routing under one agent runtime root."""

    def __init__(self, base_dir: str, max_rounds: int = 100, agent_id: str = "main"):
        self.base_dir = os.path.abspath(base_dir)
        self.max_rounds = max_rounds
        self.agent_id = str(agent_id or "").strip() or "main"
        self._state_write_lock = threading.Lock()
        os.makedirs(self.base_dir, exist_ok=True)

    def get_or_create_session_path(self, user_id: str = "") -> str:
        current_path = self.get_current_session_path(user_id)
        if current_path:
            return current_path

        latest = self._latest_main_session(user_id)
        if latest:
            self._save_state(user_id, os.path.basename(latest))
            self._ensure_v2_session(latest)
            return latest

        return self.create_new_session(user_id)

    def create_new_session(self, user_id: str = "") -> str:
        stem = self._unique_stem(self.base_dir, _timestamp())
        session_dir = os.path.join(self.base_dir, stem)
        os.makedirs(session_dir, exist_ok=True)
        self._ensure_session_runtime_dirs(session_dir)
        path = os.path.join(session_dir, "history.jsonl")
        self.ensure_main_session_task_dirs(path)
        SessionJsonlStore(path).ensure_created(
            session_id=stem,
            session_name=stem,
            agent_id=self.agent_id,
            user_id=str(user_id or "").strip(),
        )
        self._save_state(user_id, stem)
        return path

    def ensure_main_session_task_dirs(self, session_path: str) -> None:
        """Materialize task-session control-plane dirs under one main session."""
        session_dir = os.path.dirname(os.path.abspath(session_path))
        task_state_dir = os.path.join(session_dir, "task_state")
        tasks_dir = os.path.join(task_state_dir, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)
        pending_path = os.path.join(task_state_dir, "pending_messages.json")
        if not os.path.exists(pending_path):
            self._atomic_write(pending_path, [])

    def create_task_session(
        self,
        parent_session_path: str,
        task_id: str,
        title: str,
        user_id: str = "",
    ) -> str:
        """Create one task-session history tree under a main session."""
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            raise ValueError("task_id_required")
        parent_path = os.path.abspath(parent_session_path)
        parent_session_id = self._session_id_from_path(parent_path)
        self.ensure_main_session_task_dirs(parent_path)
        task_dir = os.path.join(os.path.dirname(parent_path), "task_state", "tasks", clean_task_id)
        self._ensure_session_runtime_dirs(task_dir)
        task_state_path = os.path.join(task_dir, "task_state.json")
        if not os.path.exists(task_state_path):
            self._atomic_write(
                task_state_path,
                {
                    "task_id": clean_task_id,
                    "parent_session_id": parent_session_id,
                    "title": str(title or clean_task_id).strip() or clean_task_id,
                    "status": "active",
                    "created_at": iso_timestamp(),
                    "updated_at": iso_timestamp(),
                },
            )
        history_path = os.path.join(task_dir, "history.jsonl")
        SessionJsonlStore(history_path).ensure_created(
            session_id=clean_task_id,
            session_name=str(title or clean_task_id).strip() or clean_task_id,
            agent_id=self.agent_id,
            user_id=str(user_id or "").strip(),
        )
        ensure_plan_file(history_path)
        return history_path

    def get_or_create_task_session_path(
        self,
        parent_session_path: str,
        task_id: str,
        title: str = "",
        user_id: str = "",
    ) -> str:
        """Return existing task-session history path or create a new one."""
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            raise ValueError("task_id_required")
        history_path = os.path.join(
            os.path.dirname(os.path.abspath(parent_session_path)),
            "task_state",
            "tasks",
            clean_task_id,
            "history.jsonl",
        )
        if os.path.exists(history_path):
            self.ensure_main_session_task_dirs(parent_session_path)
            self._ensure_session_runtime_dirs(os.path.dirname(history_path))
            return history_path
        return self.create_task_session(parent_session_path, clean_task_id, title=title, user_id=user_id)

    def list_task_session_paths(self, parent_session_path: str) -> List[str]:
        """List task-session history paths under one main session."""
        parent_dir = os.path.dirname(os.path.abspath(parent_session_path))
        tasks_dir = os.path.join(parent_dir, "task_state", "tasks")
        if not os.path.isdir(tasks_dir):
            return []
        items: List[str] = []
        for name in sorted(os.listdir(tasks_dir)):
            task_dir = os.path.join(tasks_dir, name)
            if not os.path.isdir(task_dir):
                continue
            history_path = os.path.join(task_dir, "history.jsonl")
            if os.path.isfile(history_path):
                ensure_plan_file(history_path)
                items.append(history_path)
        return items

    def list_sessions(self, user_id: str = "") -> List[str]:
        _ = user_id
        if not os.path.exists(self.base_dir):
            return []

        items: List[str] = []
        for path in sorted(self._iter_main_session_paths()):
            summary = replay_session_summary(path)
            items.append(str(summary.get("name") or os.path.splitext(os.path.basename(path))[0]))
        return items

    def switch_session(self, user_id: str, name: str) -> Optional[str]:
        if not os.path.exists(self.base_dir):
            return None
        target_name = (name or "").strip()
        if not target_name:
            return None

        for path in self._iter_main_session_paths():
            filename = os.path.basename(path)
            stem = os.path.splitext(filename)[0]
            summary = replay_session_summary(path)
            display_name = str(summary.get("name") or "")
            session_id = self._session_id_from_path(path)
            if target_name in {filename, stem, display_name, session_id}:
                self._save_state(user_id, session_id)
                self._ensure_v2_session(path)
                return path
        return None

    def get_display_name(self, session_path: str) -> str:
        summary = replay_session_summary(session_path)
        return str(summary.get("name") or os.path.splitext(os.path.basename(session_path))[0])

    def maybe_rename_after_rounds(self, user_id: str, session_path: str) -> str:
        _ = user_id
        summary = replay_session_summary(session_path)
        if summary.get("renamed"):
            return session_path
        rounds = int(summary.get("rounds", 0))
        if rounds < 3:
            return session_path

        first_user = ""
        for message in SessionJsonlStore(session_path).read_events():
            if str(message.get("type") or "") != "message":
                continue
            payload = message.get("payload") if isinstance(message.get("payload"), dict) else {}
            if payload.get("role") == "user":
                first_user = str(payload.get("content", ""))
                break

        created_at = str(summary.get("created_at") or _timestamp()).replace(":", "").replace("-", "").replace("T", "_")[:15]
        slug = self._slugify(first_user) or "chat"
        new_name = f"{created_at}_{slug}"
        if new_name == self.get_display_name(session_path):
            return session_path

        SessionJsonlStore(session_path).append_event(
            build_session_patch_event(patch_kind="rename", patch_payload={"name": new_name})
        )
        self._save_state(user_id, self._session_id_from_path(session_path))
        return session_path

    def build_sub_session_path(self, parent_context_path: str, suffix: Optional[str] = None) -> str:
        base, ext = os.path.splitext(parent_context_path)
        raw = suffix.strip() if isinstance(suffix, str) else _timestamp()
        safe_suffix = self._slugify(raw) or _timestamp()
        candidate = f"{base}-sub{safe_suffix}{ext or '.jsonl'}"
        index = 1
        while os.path.exists(candidate):
            candidate = f"{base}-sub{safe_suffix}-{index}{ext or '.jsonl'}"
            index += 1
        return candidate

    def set_current_session(self, user_id: str, session_path: str) -> None:
        self._save_state(user_id, self._session_id_from_path(session_path))

    def get_current_session_path(self, user_id: str = "") -> str:
        current_file = self._current_file_for_user(user_id)
        if not current_file:
            return ""
        current_path = os.path.join(self.base_dir, current_file, "history.jsonl")
        if not os.path.exists(current_path):
            return ""
        self._ensure_v2_session(current_path)
        return current_path

    def resolve_session_path(self, user_id: str, session_name: str) -> Optional[str]:
        return self.switch_session(user_id, session_name)

    def _ensure_v2_session(self, path: str) -> None:
        stem = self._session_id_from_path(path)
        self._ensure_session_runtime_dirs(os.path.dirname(os.path.abspath(path)))
        self.ensure_main_session_task_dirs(path)
        SessionJsonlStore(path).ensure_created(session_id=stem, session_name=stem, agent_id=self.agent_id)

    def _ensure_session_runtime_dirs(self, session_dir: str) -> None:
        """Materialize the sibling runtime directories under one session."""
        resolved = os.path.abspath(session_dir)
        os.makedirs(resolved, exist_ok=True)
        for name in ("tool_outputs", "context", "events"):
            os.makedirs(os.path.join(resolved, name), exist_ok=True)

    def _iter_main_session_paths(self):
        for fname in os.listdir(self.base_dir):
            if fname == "state.json":
                continue
            session_dir = os.path.join(self.base_dir, fname)
            if not os.path.isdir(session_dir):
                continue
            history_path = os.path.join(session_dir, "history.jsonl")
            if not os.path.isfile(history_path):
                continue
            stem = fname
            if "-sub" in stem:
                continue
            yield history_path

    def _latest_main_session(self, user_id: str = "") -> Optional[str]:
        candidates = list(self._iter_main_session_paths())
        if not candidates:
            return None
        target_user_id = str(user_id or "").strip()
        if target_user_id:
            scoped = []
            for path in candidates:
                summary = replay_session_summary(path)
                if str(summary.get("user_id") or "").strip() == target_user_id:
                    scoped.append(path)
            if scoped:
                candidates = scoped
            else:
                return None
        return max(candidates, key=os.path.getmtime)

    def _state_path(self) -> str:
        return os.path.join(self.base_dir, "state.json")

    def _load_state(self) -> Dict[str, Any]:
        path = self._state_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_state(self, user_id: str, current_file: str) -> None:
        path = self._state_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with self._state_write_lock:
            state = self._normalize_state_payload(self._load_state())
            key = self._state_user_key(user_id)
            state.setdefault("current_by_user", {})
            state["current_by_user"][key] = str(current_file or "").strip()
            self._atomic_write(path, state)

    def _atomic_write(self, path: str, payload: Dict[str, Any]) -> None:
        directory = os.path.dirname(path) or "."
        fd, tmp_path = tempfile.mkstemp(prefix=f"{os.path.basename(path)}.", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _slugify(self, text: str) -> str:
        clean = re.sub(r"\s+", "_", (text or "").strip())[:20]
        clean = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff-]", "", clean)
        return clean.strip("_")

    def _unique_stem(self, directory: str, stem: str) -> str:
        candidate = stem
        index = 1
        while os.path.exists(os.path.join(directory, candidate)):
            candidate = f"{stem}_{index}"
            index += 1
        return candidate

    def _session_id_from_path(self, path: str) -> str:
        resolved = os.path.abspath(path)
        if os.path.basename(resolved).lower() == "history.jsonl":
            return os.path.basename(os.path.dirname(resolved)) or "default"
        return os.path.splitext(os.path.basename(resolved))[0] or "default"

    def _current_file_for_user(self, user_id: str) -> str:
        raw_state = self._load_state()
        legacy_current_file = str(raw_state.get("current_file") or "").strip() if isinstance(raw_state, dict) else ""
        state = self._normalize_state_payload(raw_state)
        current_by_user = state.get("current_by_user")
        if not isinstance(current_by_user, dict):
            return ""
        key = self._state_user_key(user_id)
        current_file = str(current_by_user.get(key) or "").strip()
        if current_file:
            return current_file
        default_current = str(current_by_user.get(self._state_user_key("")) or "").strip()
        if legacy_current_file and default_current == legacy_current_file:
            self._save_state(user_id, legacy_current_file)
        return default_current

    def _normalize_state_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        state = payload if isinstance(payload, dict) else {}
        current_by_user: Dict[str, str] = {}
        raw_current_by_user = state.get("current_by_user")
        if isinstance(raw_current_by_user, dict):
            for raw_key, raw_value in raw_current_by_user.items():
                key = str(raw_key or "").strip()
                value = str(raw_value or "").strip()
                if key and value:
                    current_by_user[key] = value
        legacy_current_file = str(state.get("current_file") or "").strip()
        if legacy_current_file and "default" not in current_by_user:
            current_by_user["default"] = legacy_current_file
        return {
            "schema_version": 2,
            "current_by_user": current_by_user,
        }

    def _state_user_key(self, user_id: str) -> str:
        return str(user_id or "").strip() or "default"
