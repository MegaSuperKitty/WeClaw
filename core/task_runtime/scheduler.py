# -*- coding: utf-8 -*-
"""Minimal cooperative scheduler for task-session runtime."""

from __future__ import annotations

from typing import Callable, List

from core.history.session_event_types import build_message_event, iso_timestamp
from core.history.session_event_types import (
    SESSION_EVENT_TASK_RESULT_RECEIVED,
    SESSION_EVENT_TASK_WAITING_HUMAN,
)
from core.history.session_jsonl_store import SessionJsonlStore
from core.workspace.layout import WorkspaceLayout
from .models import TaskPendingMessage, TaskQueueItem, TaskState
from .store import TaskRuntimeStore


class TaskScheduler:
    """Pump task sessions cooperatively around one main-session run."""

    def __init__(self, layout: WorkspaceLayout, store: TaskRuntimeStore):
        self.layout = layout
        self.store = store

    def pump_once(self, session_id: str, task_executor: Callable[[str, str], dict] | None = None) -> List[str]:
        completed: List[str] = []
        for state in self._load_runnable_tasks(session_id):
            task_id = str(state.get("task_id") or "").strip()
            if not task_id:
                continue
            consumed = self._consume_queued_messages(session_id, task_id, state)
            refreshed = self.store.read_task_state(session_id, task_id)
            self._run_task_session_once(session_id, task_id, refreshed, task_executor=task_executor, consumed_message_count=consumed)
            refreshed = self.store.read_task_state(session_id, task_id)
            self._enqueue_result_to_main_session(session_id, task_id, refreshed)
            self._enqueue_waiting_human_to_main_session(session_id, task_id, refreshed)
            completed.append(task_id)
        return completed

    def _load_runnable_tasks(self, session_id: str) -> List[TaskState]:
        return [
            row for row in self.store.list_task_states(session_id)
            if str(row.get("status") or "").strip() in {"active", "waiting", "finished"}
        ]

    def _consume_queued_messages(self, session_id: str, task_id: str, state: TaskState) -> int:
        queued = list(state.get("queued_messages") or [])
        if not queued:
            return 0
        history_store = SessionJsonlStore(self.layout.task_session_history_path(session_id, task_id))
        for item in queued:
            queue_item = TaskQueueItem(item)
            history_store.append_event(
                build_message_event(
                    message_id=history_store.next_message_id(),
                    role="user",
                    author="task_controller",
                    content=str(queue_item.get("instruction_text") or ""),
                    user_turn_meta={
                        "source": "task_controller",
                        "preferred_response_language": "zh",
                        "request_kind": "task_controller_message",
                        "message_time": iso_timestamp(),
                        "attachments": [],
                        "message_kind": str(queue_item.get("message_kind") or ""),
                        "referenced_messages": list(queue_item.get("referenced_messages") or []),
                    },
                    extras={
                        "message_origin": "task_controller",
                        "message_kind": str(queue_item.get("message_kind") or ""),
                        "referenced_messages": list(queue_item.get("referenced_messages") or []),
                    },
                )
            )
        state["queued_messages"] = []
        state["latest_progress_summary"] = f"已接收 {len(queued)} 条控制消息。"
        self.store.write_task_state(session_id, task_id, state)
        return len(queued)

    def _run_task_session_once(
        self,
        session_id: str,
        task_id: str,
        state: TaskState,
        *,
        task_executor: Callable[[str, str], dict] | None,
        consumed_message_count: int,
    ) -> None:
        if task_executor is None:
            return
        if str(state.get("status") or "").strip() != "active":
            return
        if consumed_message_count <= 0:
            return
        result = dict(task_executor(self.layout.task_session_history_path(session_id, task_id), task_id) or {})
        if not result:
            return
        state["status"] = str(result.get("status") or state.get("status") or "").strip() or "active"
        state["run_phase"] = str(result.get("run_phase") or state.get("run_phase") or "").strip()
        if str(result.get("result_summary") or "").strip():
            state["result_summary"] = str(result.get("result_summary") or "").strip()
        if str(result.get("latest_progress_summary") or "").strip():
            state["latest_progress_summary"] = str(result.get("latest_progress_summary") or "").strip()
        if isinstance(result.get("pending_questions"), list):
            state["pending_questions"] = list(result.get("pending_questions") or [])
        self.store.write_task_state(session_id, task_id, state)

    def _enqueue_result_to_main_session(self, session_id: str, task_id: str, state: TaskState) -> None:
        result_summary = str(state.get("result_summary") or "").strip()
        if not result_summary or str(state.get("status") or "").strip() != "finished":
            return
        self._append_pending_once(
            session_id,
            TaskPendingMessage(
                {
                    "message_id": f"{task_id}:task_result",
                    "origin": "task_session",
                    "task_id": task_id,
                    "kind": "task_result",
                    "content": result_summary,
                    "payload": {
                        "task_id": task_id,
                        "task_title": str(state.get("title") or ""),
                        "status": str(state.get("status") or ""),
                        "result_summary": result_summary,
                    },
                    "created_at": iso_timestamp(),
                }
            ),
        )
        self.store.append_task_event(
            session_id,
            task_id,
            event_type=SESSION_EVENT_TASK_RESULT_RECEIVED,
            status=str(state.get("status") or ""),
            summary="任务结果已入主会话 deferred queue。",
            message_kind="task_result",
            payload={"message_id": f"{task_id}:task_result"},
        )

    def _enqueue_waiting_human_to_main_session(self, session_id: str, task_id: str, state: TaskState) -> None:
        questions = list(state.get("pending_questions") or [])
        if not questions or str(state.get("run_phase") or "").strip() != "waiting_human_or_external":
            return
        first = questions[0] if isinstance(questions[0], dict) else {}
        content = str(first.get("question") or first.get("content") or "").strip()
        if not content:
            return
        self._append_pending_once(
            session_id,
            TaskPendingMessage(
                {
                    "message_id": f"{task_id}:task_waiting_human",
                    "origin": "task_session",
                    "task_id": task_id,
                    "kind": "task_waiting_human",
                    "content": content,
                    "payload": {
                        "task_id": task_id,
                        "task_title": str(state.get("title") or ""),
                        "status": str(state.get("status") or ""),
                    },
                    "created_at": iso_timestamp(),
                }
            ),
        )
        self.store.append_task_event(
            session_id,
            task_id,
            event_type=SESSION_EVENT_TASK_WAITING_HUMAN,
            status=str(state.get("status") or ""),
            run_phase=str(state.get("run_phase") or ""),
            summary="任务正在等待主会话转问用户。",
            message_kind="task_waiting_human",
            payload={"message_id": f"{task_id}:task_waiting_human"},
        )

    def _append_pending_once(self, session_id: str, payload: TaskPendingMessage) -> None:
        rows = self.store.read_pending_messages(session_id)
        message_id = str(payload.get("message_id") or "").strip()
        if any(str(row.get("message_id") or "").strip() == message_id for row in rows):
            return
        self.store.append_pending_message(session_id, payload)
