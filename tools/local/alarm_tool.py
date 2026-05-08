# -*- coding: utf-8 -*-
"""Unified alarm tool for once/daily/weekly task scheduling."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional

from integrations.mcp.openai_tool import Tool


class AlarmTool(Tool):
    """Create and manage alarms through the unified alarm service."""

    def __init__(self, on_trigger: Optional[Callable[[str, str], None]] = None):
        self._on_trigger = on_trigger
        self._active_user_id: Optional[str] = None
        self._schedule_alarm: Optional[Callable[..., Dict[str, object]]] = None
        self._session_path: Optional[str] = None
        super().__init__(
            name="alarm",
            description=(
                "Manage alarms in one unified scheduler. "
                "Use create for one-time, daily, or weekly alarms; use list to inspect alarms; "
                "use pause/resume/cancel to control an existing alarm."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "list", "pause", "resume", "cancel"],
                    },
                    "schedule_type": {
                        "type": "string",
                        "enum": ["once", "daily", "weekly"],
                    },
                    "run_at": {
                        "type": "string",
                        "description": "Absolute datetime for once alarms: YYYY-MM-DD HH:MM[:SS].",
                    },
                    "hour": {"type": "integer", "description": "Hour for daily/weekly alarms."},
                    "minute": {"type": "integer", "description": "Minute for daily/weekly alarms."},
                    "second": {"type": "integer", "description": "Optional second for daily/weekly alarms."},
                    "weekdays": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Weekdays for weekly alarms, such as mon/tue/fri.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "What should be executed when the alarm fires.",
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Optional target session name. Defaults to the current session.",
                    },
                    "alarm_id": {
                        "type": "string",
                        "description": "Alarm id used by pause/resume/cancel.",
                    },
                },
                "required": ["action"],
            },
        )

    def set_context(
        self,
        user_id: str,
        on_trigger: Optional[Callable[[str, str], None]] = None,
        *,
        schedule_alarm: Optional[Callable[..., Dict[str, object]]] = None,
        session_path: Optional[str] = None,
    ) -> None:
        self._active_user_id = str(user_id or "").strip() or None
        self._session_path = str(session_path or "").strip() or None
        if on_trigger is not None:
            self._on_trigger = on_trigger
        if schedule_alarm is not None:
            self._schedule_alarm = schedule_alarm

    def _execute(
        self,
        action: str,
        schedule_type: str = "",
        run_at: str = "",
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        weekdays: Optional[List[str]] = None,
        prompt: str = "",
        session_name: str = "",
        alarm_id: str = "",
    ):
        clean_action = str(action or "").strip().lower()
        if clean_action == "list":
            return "闹钟列表请在控制台定时任务页面查看。当前工具不直接返回完整列表。"

        if clean_action in {"pause", "resume", "cancel"}:
            clean_alarm_id = str(alarm_id or "").strip()
            if not clean_alarm_id:
                return "请提供 alarm_id。"
            # Current tool path creates alarms; UI/API handles later management.
            return f"当前轮次暂未把 {clean_action} 接到会话内管理回路，请在控制台页面执行。alarm_id={clean_alarm_id}"

        if clean_action != "create":
            return "action 必须是 create、list、pause、resume 或 cancel。"
        if not self._schedule_alarm:
            return "闹钟创建失败：统一闹钟服务尚未绑定。"
        if not self._active_user_id:
            return "闹钟创建失败：当前用户上下文缺失。"

        clean_schedule_type = str(schedule_type or "").strip().lower()
        clean_prompt = str(prompt or "").strip()
        if not clean_prompt:
            return "闹钟创建失败：prompt 不能为空。"

        payload: Dict[str, object] = {}
        if clean_schedule_type == "once":
            payload["run_at"] = str(run_at or "").strip()
        elif clean_schedule_type == "daily":
            payload["hour"] = hour
            payload["minute"] = minute
            payload["second"] = 0 if second is None else second
        elif clean_schedule_type == "weekly":
            payload["hour"] = hour
            payload["minute"] = minute
            payload["second"] = 0 if second is None else second
            payload["weekdays"] = list(weekdays or [])
        else:
            return "schedule_type 必须是 once、daily 或 weekly。"

        try:
            job = self._schedule_alarm(
                user_id=self._active_user_id,
                session_name=self._resolve_default_session_name(session_name),
                schedule_type=clean_schedule_type,
                schedule=payload,
                prompt=clean_prompt,
            )
        except Exception as exc:
            return f"闹钟创建失败：{exc}"

        return (
            f"闹钟已创建：id={job.get('id', '')}，"
            f"type={job.get('schedule_type', '')}，"
            f"next_run_at={job.get('next_run_at', '') or '-'}。"
        )

    def _resolve_default_session_name(self, provided: str) -> str:
        text = str(provided or "").strip()
        if text:
            return text
        if not self._session_path:
            return ""
        path = Path(self._session_path)
        if path.name.lower() == "history.jsonl":
            return path.parent.name
        return path.stem
