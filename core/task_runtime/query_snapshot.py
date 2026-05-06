# -*- coding: utf-8 -*-
"""Read-only task-session snapshot helpers."""

from __future__ import annotations

from typing import Any, Dict, List

from core.history.render_reader import replay_render_rows
from .models import TaskQuerySnapshot, TaskState


class TaskQuerySnapshotBuilder:
    """Build grounded read-only snapshots from task state and task history."""

    def build_snapshot(self, task_state: TaskState, task_history_path: str, max_messages: int = 12) -> TaskQuerySnapshot:
        messages = replay_render_rows(task_history_path)
        return TaskQuerySnapshot(
            {
                "task_id": str(task_state.get("task_id") or ""),
                "title": str(task_state.get("title") or ""),
                "status": str(task_state.get("status") or ""),
                "run_phase": str(task_state.get("run_phase") or ""),
                "instruction_text": str(task_state.get("instruction_text") or ""),
                "latest_progress_summary": str(task_state.get("latest_progress_summary") or ""),
                "messages": messages[-max_messages:],
            }
        )


class TaskQuerySnapshotRunner:
    """Return grounded answers from a read-only snapshot."""

    def run_query(self, snapshot: TaskQuerySnapshot, question: str) -> Dict[str, Any]:
        _ = self._build_query_only_prompt(snapshot=snapshot, question=question)
        status = str(snapshot.get("status") or "").strip() or "unknown"
        phase = str(snapshot.get("run_phase") or "").strip()
        progress = str(snapshot.get("latest_progress_summary") or "").strip()
        title = str(snapshot.get("title") or snapshot.get("task_id") or "").strip()
        message_count = len(snapshot.get("messages") or [])
        if not progress and message_count == 0:
            answer = "当前信息不足，无法可靠判断更多进展。"
        else:
            parts: List[str] = []
            if title:
                parts.append(f"任务“{title}”")
            parts.append(f"状态是 {status}")
            if phase:
                parts.append(f"运行阶段是 {phase}")
            if progress:
                parts.append(f"当前进展：{progress}")
            if message_count:
                parts.append(f"已可见最近 {message_count} 条任务消息")
            answer = "，".join(parts) + "。"
        return {
            "answer_source": "snapshot_agent",
            "answer": answer,
        }

    def _build_query_only_prompt(self, *, snapshot: TaskQuerySnapshot, question: str) -> str:
        return (
            "You are a read-only snapshot agent. "
            "Do not advance the task. "
            "Answer only from the provided snapshot. "
            f"Question: {str(question or '').strip()} "
            f"Snapshot task_id: {str(snapshot.get('task_id') or '').strip()}"
        )
