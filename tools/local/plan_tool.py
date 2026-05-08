# -*- coding: utf-8 -*-
"""Tool for reading and writing the durable session plan file."""

from __future__ import annotations

from typing import Any, Optional

from core.task_runtime.plan_file import read_plan_file, write_plan_file
from integrations.mcp.openai_tool import Tool


class PlanTool(Tool):
    """Read or overwrite the durable `agent_plan.md` for the bound session."""

    def __init__(self):
        self._session_path: Optional[str] = None
        super().__init__(
            name="plan",
            description=(
                "Read or overwrite the durable plan file for the current session. "
                "Use after each new input message to inspect or update the task plan."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["read", "write"],
                        "description": "Whether to read the current plan or overwrite it.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The full new plan content when mode=write.",
                    },
                },
                "required": ["mode"],
            },
        )

    def set_context(self, user_id: str, session_path: Optional[str] = None, **_: Any) -> None:
        _ = user_id
        self._session_path = str(session_path or "").strip() or None

    def _execute(self, mode: str, content: str = ""):
        if not self._session_path:
            return {"ok": False, "error": "session_path_missing"}
        clean_mode = str(mode or "").strip()
        if clean_mode == "read":
            plan_text = read_plan_file(self._session_path)
            return {
                "ok": True,
                "mode": "read",
                "content": plan_text,
                "summary": "已读取当前 plan 文件。",
            }
        if clean_mode == "write":
            path = write_plan_file(self._session_path, content)
            return {
                "ok": True,
                "mode": "write",
                "content": str(content or ""),
                "plan_path": path,
                "summary": "已更新当前 plan 文件。",
            }
        return {"ok": False, "error": "invalid_mode"}
