# -*- coding: utf-8 -*-
"""Sub-agent tool: start an ephemeral async worker with a limited skill set."""

from typing import Callable, List, Optional

from core.subagent_runtime.runner import SubagentRunner
from integrations.mcp.openai_tool import Tool
from .skill_tool import SkillRuntime, SkillTool


class SubAgentTool(Tool):
    def __init__(self, available_tools: List[object], skill_runtime: SkillRuntime, max_steps: int = 8):
        self.available_tools = available_tools
        self.skill_runtime = skill_runtime
        self.max_steps = max_steps
        self._user_id: Optional[str] = None
        self._parent_context_path: Optional[str] = None
        self._parent_session_id: Optional[str] = None
        self._on_trigger: Optional[Callable[[str, str], None]] = None
        self._runner = SubagentRunner()
        super().__init__(
            name="sub_agent",
            description=(
                "Manage one temporary async subagent worker for short-lived delegated work. "
                "This worker is not a persistent task session: it does not keep a session transcript and only returns a structured result to the parent session. "
                "Use action=start to launch, action=query to inspect status/result, and action=cancel to stop cooperatively."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "One of start, query, cancel. Defaults to start.",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Scoped task for the temporary subagent worker to complete.",
                    },
                    "subagent_id": {
                        "type": "string",
                        "description": "Existing subagent id used by query/cancel.",
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Allowed skill names for this temporary worker.",
                    },
                },
            },
        )

    def set_context(
        self,
        user_id: str,
        parent_context_path: Optional[str] = None,
        session_path: Optional[str] = None,
        on_trigger: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self._user_id = user_id
        self._parent_context_path = parent_context_path or session_path
        self._parent_session_id = _session_id_from_history_path(self._parent_context_path or "")
        self._on_trigger = on_trigger

    @property
    def registry(self):
        return self._runner.registry

    def _execute(
        self,
        action: str = "start",
        task_description: str = "",
        subagent_id: str = "",
        skills: Optional[List[str]] = None,
    ):
        clean_action = str(action or "start").strip().lower() or "start"
        if clean_action == "query":
            return self._query(subagent_id)
        if clean_action == "cancel":
            return self._cancel(subagent_id)
        if clean_action != "start":
            return {"ok": False, "error": "invalid_action"}
        task = (task_description or "").strip()
        if not task:
            return {"ok": False, "error": "task_description_required"}
        if not self._parent_session_id:
            return {"ok": False, "error": "parent_session_id_missing"}

        allowlist = _normalize_skills(skills)
        tools = _prepare_tools(self.available_tools, self.skill_runtime, allowlist)
        return self._runner.start_async(
            parent_session_id=self._parent_session_id,
            request={
                "task_description": task,
                "worker_kind": "worker",
                "instruction_text": task,
                "allowed_tools": allowlist,
                "max_steps": self.max_steps,
            },
            tools=tools,
        )

    def _query(self, subagent_id: str):
        clean_id = str(subagent_id or "").strip()
        if not clean_id:
            return {"ok": False, "error": "subagent_id_required"}
        record = self._runner.registry.get(clean_id)
        if not record:
            return {"ok": False, "error": "subagent_not_found"}
        result = dict(record.get("result") or {})
        return {
            "ok": True,
            "subagent_id": clean_id,
            "status": str(record.get("status") or ""),
            "worker_kind": str(record.get("worker_kind") or ""),
            "summary": str(record.get("summary") or ""),
            "result": result,
            "error": str(record.get("error") or ""),
        }

    def _cancel(self, subagent_id: str):
        clean_id = str(subagent_id or "").strip()
        if not clean_id:
            return {"ok": False, "error": "subagent_id_required"}
        record = self._runner.registry.cancel(clean_id)
        if not record:
            return {"ok": False, "error": "subagent_not_found"}
        return {
            "ok": True,
            "subagent_id": clean_id,
            "status": str(record.get("status") or ""),
            "summary": str(record.get("summary") or ""),
            "cancel_requested": bool(record.get("cancel_requested")),
        }


def _normalize_skills(skills: Optional[List[str]]) -> List[str]:
    if skills is None:
        return []
    if isinstance(skills, list):
        return [str(s).strip() for s in skills if str(s).strip()]
    return [str(skills).strip()]


def _prepare_tools(available_tools: List[object], skill_runtime: SkillRuntime, allowlist: Optional[List[str]]):
    tools = []
    for tool in available_tools or []:
        if getattr(tool, "name", "") == "sub_agent":
            continue
        if isinstance(tool, SkillTool):
            continue
        tools.append(tool)

    allowed = allowlist or []
    if allowed:
        tools.append(skill_runtime.create_tool(allowed_skills=allowed))
    return tools


def _session_id_from_history_path(session_path: str) -> str:
    text = str(session_path or "").strip()
    if not text:
        return ""
    normalized = text.replace("\\", "/").rstrip("/")
    if normalized.endswith("/history.jsonl"):
        return normalized.split("/")[-2]
    return normalized.split("/")[-1]
