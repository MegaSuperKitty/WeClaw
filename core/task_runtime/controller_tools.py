# -*- coding: utf-8 -*-
"""Main-session task controller tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.history.render_reader import replay_render_rows
from core.history.session_event_types import (
    SESSION_EVENT_TASK_CLOSED,
    SESSION_EVENT_TASK_CREATED,
    SESSION_EVENT_TASK_MESSAGE_ENQUEUED,
    SESSION_EVENT_TASK_STATUS_CHANGED,
    SESSION_EVENT_TASK_UPDATED,
    iso_timestamp,
)
from core.workspace.layout import WorkspaceLayout, extract_session_id_from_path
from integrations.mcp.openai_tool import Tool
from .models import ReferencedMainMessage, TaskQueueItem, TaskState
from .query_snapshot import TaskQuerySnapshotBuilder, TaskQuerySnapshotRunner
from .store import TaskRuntimeStore


def validate_referenced_message_ids(
    session_path: str,
    referenced_message_ids: Optional[List[str]],
    *,
    limit: int = 20,
) -> List[ReferencedMainMessage]:
    ids = [str(item or "").strip() for item in list(referenced_message_ids or []) if str(item or "").strip()]
    if len(ids) > limit:
        raise ValueError("referenced_message_ids_limit_exceeded")
    rows = replay_render_rows(session_path)
    row_map = {str(row.get("id") or "").strip(): row for row in rows if str(row.get("id") or "").strip()}
    expanded: List[ReferencedMainMessage] = []
    for message_id in ids:
        row = row_map.get(message_id)
        if row is None:
            raise ValueError(f"unknown_referenced_message_id:{message_id}")
        expanded.append(
            ReferencedMainMessage(
                {
                    "id": message_id,
                    "role": str(row.get("role") or ""),
                    "content": str(row.get("content") or ""),
                    "ts": str(row.get("ts") or ""),
                }
            )
        )
    return expanded


def expand_referenced_main_messages(session_path: str, referenced_message_ids: Optional[List[str]]) -> List[ReferencedMainMessage]:
    return validate_referenced_message_ids(session_path, referenced_message_ids)


def build_task_controller_message(
    *,
    message_kind: str,
    instruction_text: str,
    referenced_messages: List[ReferencedMainMessage],
) -> TaskQueueItem:
    return TaskQueueItem(
        {
            "message_kind": str(message_kind or "").strip(),
            "instruction_text": str(instruction_text or "").strip(),
            "referenced_messages": list(referenced_messages or []),
            "enqueued_at": iso_timestamp(),
        }
    )


class _BaseTaskTool(Tool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore, name: str, description: str, parameters: Dict[str, Any]):
        self.layout = layout
        self.store = store
        self._session_path: Optional[str] = None
        self._user_id: Optional[str] = None
        super().__init__(name=name, description=description, parameters=parameters)

    def set_context(self, user_id: str, session_path: Optional[str] = None, **_: Any) -> None:
        self._user_id = str(user_id or "").strip()
        self._session_path = str(session_path or "").strip() or None

    def _require_main_session_path(self) -> str:
        if not self._session_path:
            raise ValueError("main_session_path_missing")
        return self._session_path

    def _session_id(self) -> str:
        return extract_session_id_from_path(self._require_main_session_path())

    def _task_history_path(self, task_id: str) -> str:
        return self.layout.task_session_history_path(self._session_id(), task_id)

    def _read_state(self, task_id: str) -> TaskState:
        return self.store.read_task_state(self._session_id(), task_id)

    def _write_state(self, task_id: str, payload: TaskState) -> None:
        self.store.write_task_state(self._session_id(), task_id, payload)


class TaskCreateTool(_BaseTaskTool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore):
        super().__init__(
            layout=layout,
            store=store,
            name="task_create",
            description="Create one persistent task session under the current main session.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "instruction_text": {"type": "string"},
                    "referenced_message_ids": {"type": "array", "items": {"type": "string"}},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": "string"},
                },
                "required": ["title", "instruction_text"],
            },
        )

    def _execute(
        self,
        title: str,
        instruction_text: str,
        referenced_message_ids: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        priority: str = "normal",
    ):
        session_path = self._require_main_session_path()
        clean_title = str(title or "").strip()
        clean_instruction = str(instruction_text or "").strip()
        if not clean_title:
            return {"ok": False, "error": "title_required"}
        if not clean_instruction:
            return {"ok": False, "error": "instruction_text_required"}
        session_id = self._session_id()
        active_count = sum(
            1 for row in self.store.list_task_states(session_id)
            if str(row.get("status") or "") in {"active", "waiting"}
        )
        if active_count >= 3:
            return {"ok": False, "error": "active_task_limit_exceeded"}
        try:
            expanded = expand_referenced_main_messages(session_path, referenced_message_ids)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        task_id = f"task_{len(self.store.list_task_states(session_id)) + 1:06d}"
        history_path = self.store.task_history_path(session_id, task_id)
        manager = None
        from core.session.manager import SessionManager  # local import to avoid wider startup coupling
        manager = SessionManager(self.layout.sessions_root, agent_id="")
        manager.create_task_session(session_path, task_id, clean_title, user_id=self._user_id or "")
        state = TaskState(
            {
                "task_id": task_id,
                "parent_session_id": session_id,
                "title": clean_title,
                "status": "active",
                "instruction_text": clean_instruction,
                "acceptance_criteria": [str(item).strip() for item in list(acceptance_criteria or []) if str(item).strip()],
                "priority": str(priority or "normal").strip() or "normal",
                "queued_messages": [
                    build_task_controller_message(
                        message_kind="task_create",
                        instruction_text=clean_instruction,
                        referenced_messages=expanded,
                    )
                ],
                "referenced_main_message_ids": [msg["id"] for msg in expanded],
            }
        )
        self.store.write_task_state(session_id, task_id, state)
        self.store.append_task_event(
            session_id,
            task_id,
            event_type=SESSION_EVENT_TASK_CREATED,
            status="active",
            summary="任务已创建。",
            message_kind="task_create",
            payload={"title": clean_title},
        )
        self.store.append_task_event(
            session_id,
            task_id,
            event_type=SESSION_EVENT_TASK_MESSAGE_ENQUEUED,
            status="active",
            summary="初始控制消息已入队。",
            message_kind="task_create",
            payload={"queued_count": 1},
        )
        return {
            "ok": True,
            "task_id": task_id,
            "title": clean_title,
            "status": "active",
            "created_at": self.store.read_task_state(session_id, task_id).get("created_at", ""),
            "summary": "任务已创建，并已加入后台异步调度。主会话现在可以先回复用户，稍后等待 task session 回流结果。",
            "task_history_path": history_path,
        }


class TaskListTool(_BaseTaskTool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore):
        super().__init__(
            layout=layout,
            store=store,
            name="task_list",
            description="List task sessions under the current main session.",
            parameters={
                "type": "object",
                "properties": {
                    "status_filter": {"type": "array", "items": {"type": "string"}},
                    "include_finished": {"type": "boolean"},
                },
            },
        )

    def _execute(self, status_filter: Optional[List[str]] = None, include_finished: bool = False):
        rows = self.store.list_task_states(self._session_id())
        filters = {str(item or "").strip() for item in list(status_filter or []) if str(item or "").strip()}
        items = []
        for row in rows:
            status = str(row.get("status") or "").strip()
            if filters and status not in filters:
                continue
            if not include_finished and status == "finished":
                continue
            items.append(
                {
                    "task_id": str(row.get("task_id") or ""),
                    "title": str(row.get("title") or ""),
                    "status": status,
                    "priority": str(row.get("priority") or ""),
                    "latest_progress_summary": str(row.get("latest_progress_summary") or ""),
                    "pending_questions": list(row.get("pending_questions") or []),
                    "updated_at": str(row.get("updated_at") or ""),
                }
            )
        return {"ok": True, "tasks": items}


class TaskUpdateTool(_BaseTaskTool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore):
        super().__init__(
            layout=layout,
            store=store,
            name="task_update",
            description="Queue one control message into an existing task session.",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "update_kind": {"type": "string"},
                    "instruction_text": {"type": "string"},
                    "referenced_message_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["task_id", "update_kind", "instruction_text"],
            },
        )

    def _execute(
        self,
        task_id: str,
        update_kind: str,
        instruction_text: str,
        referenced_message_ids: Optional[List[str]] = None,
    ):
        session_path = self._require_main_session_path()
        clean_task_id = str(task_id or "").strip()
        clean_kind = str(update_kind or "").strip()
        clean_instruction = str(instruction_text or "").strip()
        if not clean_task_id:
            return {"ok": False, "error": "task_id_required"}
        if clean_kind not in {"append_requirement", "append_note", "resume"}:
            return {"ok": False, "error": "invalid_update_kind"}
        if not clean_instruction:
            return {"ok": False, "error": "instruction_text_required"}
        state = self._read_state(clean_task_id)
        try:
            expanded = expand_referenced_main_messages(session_path, referenced_message_ids)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        queue = list(state.get("queued_messages") or [])
        queue.append(
            build_task_controller_message(
                message_kind=clean_kind,
                instruction_text=clean_instruction,
                referenced_messages=expanded,
            )
        )
        state["queued_messages"] = queue
        state["referenced_main_message_ids"] = [msg["id"] for msg in expanded]
        previous_status = str(state.get("status") or "")
        if previous_status in {"waiting", "finished"}:
            state["status"] = "active"
            state["run_phase"] = "idle_waiting_scheduler"
            state["wake_reason"] = "task_update"
            if previous_status == "waiting":
                state["pending_questions"] = []
        self._write_state(clean_task_id, state)
        self.store.append_task_event(
            self._session_id(),
            clean_task_id,
            event_type=SESSION_EVENT_TASK_UPDATED,
            status=str(self._read_state(clean_task_id).get("status") or ""),
            summary="新控制消息已入队。",
            message_kind=clean_kind,
            payload={"queued_count": len(queue)},
        )
        self.store.append_task_event(
            self._session_id(),
            clean_task_id,
            event_type=SESSION_EVENT_TASK_MESSAGE_ENQUEUED,
            status=str(self._read_state(clean_task_id).get("status") or ""),
            summary="任务输入队列已追加消息。",
            message_kind=clean_kind,
            payload={"queued_count": len(queue)},
        )
        if previous_status in {"waiting", "finished"}:
            self.store.append_task_event(
                self._session_id(),
                clean_task_id,
                event_type=SESSION_EVENT_TASK_STATUS_CHANGED,
                status="active",
                summary="任务因 update 被重新唤醒。",
                payload={"from_status": previous_status, "to_status": "active"},
            )
        return {
            "ok": True,
            "task_id": clean_task_id,
            "status": str(self._read_state(clean_task_id).get("status") or ""),
            "update_kind": clean_kind,
            "summary": "新要求已加入任务输入队列，任务会在后台继续异步推进。主会话无需在当前轮同步等待。",
        }


class TaskFinishTool(_BaseTaskTool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore):
        super().__init__(
            layout=layout,
            store=store,
            name="task_finish",
            description="Finish one task session cooperatively.",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "finish_mode": {"type": "string"},
                },
                "required": ["task_id", "finish_mode"],
            },
        )

    def _execute(self, task_id: str, finish_mode: str):
        clean_task_id = str(task_id or "").strip()
        clean_mode = str(finish_mode or "").strip()
        if not clean_task_id:
            return {"ok": False, "error": "task_id_required"}
        if clean_mode not in {"complete", "cancel", "force_stop"}:
            return {"ok": False, "error": "invalid_finish_mode"}
        state = self._read_state(clean_task_id)
        state["status"] = "finished"
        state["closed_by"] = clean_mode
        state["closed_at"] = iso_timestamp()
        self._write_state(clean_task_id, state)
        self.store.append_task_event(
            self._session_id(),
            clean_task_id,
            event_type=SESSION_EVENT_TASK_STATUS_CHANGED,
            status="finished",
            summary="任务状态变为 finished。",
            payload={"from_status": "", "to_status": "finished"},
        )
        self.store.append_task_event(
            self._session_id(),
            clean_task_id,
            event_type=SESSION_EVENT_TASK_CLOSED,
            status="finished",
            summary="任务已关闭。",
            payload={"finish_mode": clean_mode},
        )
        return {
            "ok": True,
            "task_id": clean_task_id,
            "status": "finished",
            "finish_mode": clean_mode,
            "summary": "任务已结束。",
        }


class TaskQueryTool(_BaseTaskTool):
    def __init__(self, *, layout: WorkspaceLayout, store: TaskRuntimeStore):
        super().__init__(
            layout=layout,
            store=store,
            name="task_query",
            description="Read task progress through a read-only snapshot. Use this to inspect already-materialized task progress, not to synchronously wait for a task that was just created or updated in the same main-session turn.",
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "query_kind": {"type": "string"},
                    "question": {"type": "string"},
                },
                "required": ["task_id", "question"],
            },
        )
        self.snapshot_builder = TaskQuerySnapshotBuilder()
        self.snapshot_runner = TaskQuerySnapshotRunner()

    def _execute(self, task_id: str, query_kind: str = "progress", question: str = ""):
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            return {"ok": False, "error": "task_id_required"}
        state = self._read_state(clean_task_id)
        snapshot = self.snapshot_builder.build_snapshot(state, self._task_history_path(clean_task_id))
        result = self.snapshot_runner.run_query(snapshot, question)
        return {
            "ok": True,
            "task_id": clean_task_id,
            "status": str(state.get("status") or ""),
            "query_kind": str(query_kind or "progress"),
            "answer_source": str(result.get("answer_source") or "snapshot_agent"),
            "answer": str(result.get("answer") or ""),
            "summary": "这是只读快照结果，不应用于在当前主会话同一轮里同步等待刚创建或刚更新的任务完成。",
            "snapshot_created_at": iso_timestamp(),
            "task_updated_at": str(state.get("updated_at") or ""),
        }


def build_task_runtime_tools(*, layout: WorkspaceLayout) -> List[Tool]:
    store = TaskRuntimeStore(layout)
    return [
        TaskCreateTool(layout=layout, store=store),
        TaskListTool(layout=layout, store=store),
        TaskQueryTool(layout=layout, store=store),
        TaskUpdateTool(layout=layout, store=store),
        TaskFinishTool(layout=layout, store=store),
    ]
