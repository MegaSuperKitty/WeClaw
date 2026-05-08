# -*- coding: utf-8 -*-
"""Background runner for ephemeral subagent workers."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any, Dict, List

from core.loop.react_loop import ReActAgent
from .models import SubagentResult, SubagentStartRequest
from .registry import InMemorySubagentRegistry
from .store import build_final_result, build_subagent_prompt


class _InMemoryMessageContext:
    def __init__(self, messages: List[Dict[str, Any]]):
        self._lock = Lock()
        self._messages = list(messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(item) for item in self._messages]

    def append_message(self, message: Dict[str, Any]) -> None:
        with self._lock:
            self._messages.append(dict(message))

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._messages.extend(dict(item) for item in messages)

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._messages = [dict(item) for item in messages]


class SubagentRunner:
    """Run ephemeral subagents in background threads."""

    def __init__(self, registry: InMemorySubagentRegistry | None = None):
        self.registry = registry or InMemorySubagentRegistry()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="subagent")

    def build_initial_messages(self, request: SubagentStartRequest) -> List[Dict[str, Any]]:
        return [
            {"role": "system", "content": _subagent_runtime_instruction()},
            {"role": "user", "content": build_subagent_prompt(request)},
        ]

    def start_async(
        self,
        *,
        parent_session_id: str,
        parent_run_id: str = "",
        request: SubagentStartRequest,
        tools: List[object],
    ) -> Dict[str, Any]:
        record = self.registry.create(
            parent_session_id=parent_session_id,
            parent_run_id=parent_run_id,
            worker_kind=str(request.get("worker_kind") or "worker"),
        )
        self.registry.update_status(record["subagent_id"], "running")
        self._executor.submit(self._run_worker, record["subagent_id"], request, list(tools or []))
        return {
            "ok": True,
            "subagent_id": record["subagent_id"],
            "worker_kind": record["worker_kind"],
            "status": "running",
            "summary": "Subagent started.",
        }

    def _run_worker(self, subagent_id: str, request: SubagentStartRequest, tools: List[object]) -> None:
        if self.registry.is_cancel_requested(subagent_id):
            return
        try:
            if not tools:
                result = self._build_structured_result(
                    subagent_id=subagent_id,
                    worker_kind=str(request.get("worker_kind") or "worker"),
                    final_text=_build_local_completion_text(str(request.get("task_description") or "").strip()),
                )
                if not self.registry.is_cancel_requested(subagent_id):
                    self.registry.set_result(subagent_id, result)
                return
            context = _InMemoryMessageContext(self.build_initial_messages(request))
            agent = ReActAgent(
                max_steps=int(request.get("max_steps") or 8),
                context_manager=context,  # duck-typed minimal in-memory context
                system_prompt=_subagent_runtime_instruction(),
            )
            final_text, _events = agent.run(
                tools=list(tools or []),
                cancel_checker=lambda: self.registry.is_cancel_requested(subagent_id),
            )
            if self.registry.is_cancel_requested(subagent_id):
                return
            result = self._build_structured_result(
                subagent_id=subagent_id,
                worker_kind=str(request.get("worker_kind") or "worker"),
                final_text=final_text,
            )
            if not self.registry.is_cancel_requested(subagent_id):
                self.registry.set_result(subagent_id, result)
        except Exception as exc:
            if not self.registry.is_cancel_requested(subagent_id):
                self.registry.set_error(subagent_id, str(exc))

    def _build_structured_result(self, *, subagent_id: str, worker_kind: str, final_text: str) -> SubagentResult:
        text = str(final_text or "").strip()
        if not text:
            return self._finalize_with_no_tools(subagent_id=subagent_id, worker_kind=worker_kind)
        summary = text.splitlines()[0][:200]
        return build_final_result(
            subagent_id=subagent_id,
            status="completed",
            worker_kind=worker_kind,
            summary=summary,
            final_text=text,
        )

    def _finalize_with_no_tools(self, *, subagent_id: str, worker_kind: str) -> SubagentResult:
        return build_final_result(
            subagent_id=subagent_id,
            status="completed",
            worker_kind=worker_kind,
            summary="Subagent finished without a detailed final text.",
            final_text="Completed: partial progress recorded.\nIncomplete: final narrative missing.\nNext: review from parent agent.",
        )


def _subagent_runtime_instruction() -> str:
    return (
        "You are an ephemeral subagent worker. "
        "You are not a persistent task session. "
        "Focus only on the assigned task. "
        "Use tools only when they help complete that scoped work. "
        "Return a concise structured final result for the parent session."
    )


def _build_local_completion_text(task_description: str) -> str:
    text = str(task_description or "").strip() or "No task description provided."
    return f"Completed: {text}\nIncomplete: none\nNext: return result to parent agent."
