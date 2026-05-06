# -*- coding: utf-8 -*-
"""File-backed store for task-session state and deferred delivery."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List
import json

from core.history.session_event_types import build_task_event, iso_timestamp
from core.history.session_jsonl_store import append_jsonl_line, read_jsonl_events
from core.workspace.layout import WorkspaceLayout, extract_session_id_from_path
from .models import TaskPendingMessage, TaskState


class TaskRuntimeStore:
    """Read and write task-session state under one main session tree."""

    def __init__(self, layout: WorkspaceLayout):
        self.layout = layout

    def ensure_main_session_task_dirs(self, session_id: str) -> None:
        session_task_dir = Path(self.layout.session_task_state_dir(session_id))
        tasks_dir = Path(self.layout.session_tasks_dir(session_id))
        pending_path = Path(self.layout.session_pending_messages_path(session_id))
        session_task_dir.mkdir(parents=True, exist_ok=True)
        tasks_dir.mkdir(parents=True, exist_ok=True)
        if not pending_path.exists():
            self._write_json(pending_path, [])

    def task_dir(self, session_id: str, task_id: str) -> str:
        return self.layout.task_session_dir(session_id, task_id)

    def task_history_path(self, session_id: str, task_id: str) -> str:
        return self.layout.task_session_history_path(session_id, task_id)

    def read_task_state(self, session_id: str, task_id: str) -> TaskState:
        path = Path(self.layout.task_session_state_path(session_id, task_id))
        data = self._read_json(path, default={})
        if not isinstance(data, dict):
            raise ValueError(f"invalid_task_state:{path}")
        return TaskState(data)

    def write_task_state(self, session_id: str, task_id: str, payload: TaskState) -> str:
        path = Path(self.layout.task_session_state_path(session_id, task_id))
        data = dict(payload or {})
        data["task_id"] = str(task_id or "").strip()
        data["parent_session_id"] = str(session_id or "").strip()
        ts = iso_timestamp()
        data["updated_at"] = ts
        if not str(data.get("created_at") or "").strip():
            data["created_at"] = ts
        self._write_json(path, data)
        return str(path)

    def list_task_states(self, session_id: str) -> List[TaskState]:
        tasks_dir = Path(self.layout.session_tasks_dir(session_id))
        if not tasks_dir.is_dir():
            return []
        items: List[TaskState] = []
        for entry in sorted(tasks_dir.iterdir(), key=lambda item: item.name):
            if not entry.is_dir():
                continue
            state_path = entry / "task_state.json"
            if not state_path.is_file():
                continue
            data = self._read_json(state_path, default={})
            if not isinstance(data, dict):
                raise ValueError(f"invalid_task_state:{state_path}")
            items.append(TaskState(data))
        return items

    def read_pending_messages(self, session_id: str) -> List[TaskPendingMessage]:
        path = Path(self.layout.session_pending_messages_path(session_id))
        data = self._read_json(path, default=[])
        if not isinstance(data, list):
            raise ValueError(f"invalid_pending_messages:{path}")
        items: List[TaskPendingMessage] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(f"invalid_pending_messages:{path}")
            items.append(TaskPendingMessage(item))
        return items

    def append_pending_message(self, session_id: str, payload: TaskPendingMessage) -> None:
        items = self.read_pending_messages(session_id)
        items.append(TaskPendingMessage(dict(payload or {})))
        self._write_json(Path(self.layout.session_pending_messages_path(session_id)), items)

    def mark_pending_message_delivered(self, session_id: str, message_id: str) -> bool:
        items = self.read_pending_messages(session_id)
        changed = False
        target_id = str(message_id or "").strip()
        for item in items:
            if str(item.get("message_id") or "").strip() != target_id:
                continue
            if str(item.get("delivered_at") or "").strip():
                return False
            item["delivered_at"] = iso_timestamp()
            changed = True
            break
        if changed:
            self._write_json(Path(self.layout.session_pending_messages_path(session_id)), items)
        return changed

    def mark_pending_message_responded(self, session_id: str, message_id: str) -> bool:
        items = self.read_pending_messages(session_id)
        changed = False
        target_id = str(message_id or "").strip()
        for item in items:
            if str(item.get("message_id") or "").strip() != target_id:
                continue
            if str(item.get("responded_at") or "").strip():
                return False
            item["responded_at"] = iso_timestamp()
            changed = True
            break
        if changed:
            self._write_json(Path(self.layout.session_pending_messages_path(session_id)), items)
        return changed

    def append_task_event(
        self,
        session_id: str,
        task_id: str,
        *,
        event_type: str,
        status: str = "",
        summary: str = "",
        run_phase: str = "",
        message_kind: str = "",
        payload: dict[str, Any] | None = None,
    ) -> str:
        path = Path(self.layout.task_session_events_log_path(session_id, task_id))
        append_jsonl_line(
            str(path),
            build_task_event(
                event_type=event_type,
                task_id=task_id,
                parent_session_id=session_id,
                status=status,
                summary=summary,
                run_phase=run_phase,
                message_kind=message_kind,
                payload=payload,
            ),
        )
        return str(path)

    def read_task_events(self, session_id: str, task_id: str) -> list[dict[str, Any]]:
        return read_jsonl_events(self.layout.task_session_events_log_path(session_id, task_id))

    def session_id_from_path(self, session_path: str) -> str:
        return extract_session_id_from_path(session_path)

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid_json:{path}") from exc

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        tmp_path.replace(path)
