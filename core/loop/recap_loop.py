# -*- coding: utf-8 -*-
"""ReCAP: reflective plan-and-solve on top of ReAct."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import json

from core.context.lifecycle import ReActContextManager
from core.history.context_builder import build_request_frame
from core.history.session_event_types import iso_timestamp
from core.loop.react_loop import ReActAgent, ReActHooks
from core.task_runtime.plan_file import write_plan_file


class ReCAPAgent:
    """ReCAP planner + executor that wraps a base ReAct agent."""

    STATUS_DONE = "已完成"
    STATUS_FAILED = "失败"
    STATUS_PENDING = "未完成"
    SYSTEM_MESSAGE_REQUEST_KIND = "system_message"
    RUNTIME_MESSAGE_SOURCE = "runtime"
    RUNTIME_MESSAGE_LANGUAGE = "zh"

    _VALID_STATUSES = {STATUS_DONE, STATUS_FAILED, STATUS_PENDING}
    _META_MAX_STEPS = 6
    _META_MAX_RETRIES = 10

    def __init__(
        self,
        base_agent: ReActAgent,
        max_subtasks: int = 5,
        max_steps: int = 20,
        store_internal_messages: bool = True,
        context_manager: Optional[ReActContextManager] = None,
    ):
        self.base_agent = base_agent
        self.max_subtasks = max_subtasks
        self.max_steps = max_steps
        self.store_internal_messages = store_internal_messages
        self.context_manager = context_manager or base_agent.context_manager or ReActContextManager()
        self.system_prompt = base_agent.system_prompt

    def run(self, tools=None, cancel_checker=None) -> Tuple[str, List[Dict[str, str]]]:
        messages = self.context_manager.get_messages()
        task_text = self._latest_user_task(messages)
        if not task_text:
            return "", []

        final_text = self._solve(task_text, messages, tools, cancel_checker=cancel_checker)
        return final_text, []

    def _solve(
        self,
        task_text: str,
        messages: List[Dict[str, str]],
        tools,
        cancel_checker=None,
    ) -> str:
        if cancel_checker and cancel_checker():
            return ""

        plan, error_text = self._plan(
            task_text=task_text,
            messages=messages,
            tools=tools,
            cancel_checker=cancel_checker,
        )
        if cancel_checker and cancel_checker():
            return ""
        if error_text:
            self.context_manager.append_message(
                self._build_runtime_injected_user_message(error_text, write_through=True)
            )
            return error_text
        if not plan:
            final_text = "ReCAP planner returned no plan."
            self.context_manager.append_message(
                self._build_runtime_injected_user_message(final_text, write_through=True)
            )
            return final_text

        self.context_manager.append_message(
            self._build_runtime_injected_user_message(
                f"[ReCAP PLAN]\n{json.dumps(plan, ensure_ascii=False)}",
                write_through=True,
            )
        )
        self._sync_plan_file(plan)

        task_results: Dict[str, str] = {}
        last_result = ""
        step_count = 0

        while True:
            if cancel_checker and cancel_checker():
                return ""
            if self._all_done(plan):
                return last_result or "ReCAP completed all planned subtasks."

            current = self._next_pending_subtask(plan)
            if not current:
                final_text = "ReCAP plan stalled: no pending subtasks remain, but not all subtasks are 已完成。"
                self.context_manager.append_message(
                    self._build_runtime_injected_user_message(final_text, write_through=True)
                )
                return last_result or final_text

            step_count += 1
            if step_count > self.max_steps:
                final_text = "Reached ReCAP step limit; returning partial result."
                self.context_manager.append_message(
                    self._build_runtime_injected_user_message(final_text, write_through=True)
                )
                return last_result or final_text

            subtask_id = str(current.get("id") or "").strip()
            subtask = str(current.get("task") or "").strip()
            if not subtask_id or not subtask:
                current["status"] = self.STATUS_FAILED
                continue

            self.context_manager.append_message(
                self._build_runtime_injected_user_message(
                    f"[Subtask] ({subtask_id}) {subtask}",
                    write_through=True,
                )
            )
            result, _ = self.base_agent.run(tools=tools, cancel_checker=cancel_checker)
            if cancel_checker and cancel_checker():
                return ""

            last_result = result
            task_results[subtask_id] = result

            self.context_manager.append_message(
                self._build_runtime_injected_user_message(
                    self._format_reinject(task_text, plan, current, result),
                    write_through=True,
                )
            )

            refined, error_text = self._refine(
                task_text=task_text,
                previous_plan=plan,
                completed_records=self._completed_records(plan, task_results),
                current_record=self._record_for_task(current, result),
                messages=self.context_manager.get_messages(),
                tools=tools,
                cancel_checker=cancel_checker,
            )
            if cancel_checker and cancel_checker():
                return ""
            if error_text:
                self.context_manager.append_message(
                    self._build_runtime_injected_user_message(error_text, write_through=True)
                )
                return error_text
            if not refined:
                final_text = "ReCAP refiner returned no plan."
                self.context_manager.append_message(
                    self._build_runtime_injected_user_message(final_text, write_through=True)
                )
                return final_text

            plan = refined
            self._sync_plan_file(plan)
            self.context_manager.append_message(
                self._build_runtime_injected_user_message(
                    f"[ReCAP UPDATE]\n{json.dumps(plan, ensure_ascii=False)}",
                    write_through=True,
                )
            )

    def _plan(
        self,
        task_text: str,
        messages: List[Dict[str, str]],
        tools,
        cancel_checker=None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        tool_catalog = self._tool_catalog_text(tools)
        ask_human_available = self._has_ask_human(tools)
        prompt = (
            "你是 ReCAP 的任务规划器。\n"
            "你需要先判断是否真的缺少关键信息；只有在确实无法继续规划时，才允许调用 ask_human 工具追问一轮。\n"
            "系统工具目录（仅供理解整体能力，不可直接调用；唯一允许调用的工具是 ask_human）：\n"
            f"{tool_catalog}\n\n"
            f"ask_human 当前是否可用：{'可用' if ask_human_available else '不可用'}。\n"
            f"当前总任务：{task_text}\n\n"
            "请输出一份完整计划，要求：\n"
            f"- 子任务数量不超过 {self.max_subtasks}。\n"
            "- 仅输出 JSON，不要输出任何额外说明。\n"
            "- 顶层字段只能是 thought, subtasks。\n"
            "- subtasks 必须是完整计划，不是增量 patch。\n"
            '- 每个 subtask 只能包含 id, task, status。\n'
            '- id 必须唯一，优先使用稳定短 id（如 s1, s2, s3）。\n'
            f'- status 必须统一写成 "{self.STATUS_PENDING}"。\n'
            "- 不要遗漏关键步骤。\n"
        )
        return self._run_meta_planner(
            mode="plan",
            prompt=prompt,
            messages=messages,
            tools=tools,
            previous_plan=None,
            cancel_checker=cancel_checker,
        )

    def _refine(
        self,
        task_text: str,
        previous_plan: Dict[str, Any],
        completed_records: List[Dict[str, str]],
        current_record: Dict[str, str],
        messages: List[Dict[str, str]],
        tools,
        cancel_checker=None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        tool_catalog = self._tool_catalog_text(tools)
        ask_human_available = self._has_ask_human(tools)
        prompt = (
            "你是 ReCAP 的反思式重规划器。\n"
            "你必须先反思“刚进行的子任务”是否真正成功，再决定新的完整计划。\n"
            "注意：已经执行结束的子任务不会重跑；如果需要补救，只能新增后续子任务，不能把旧子任务重新改回未执行。\n"
            "系统工具目录（仅供理解整体能力，不可直接调用；唯一允许调用的工具是 ask_human）：\n"
            f"{tool_catalog}\n\n"
            f"ask_human 当前是否可用：{'可用' if ask_human_available else '不可用'}。\n"
            f"当前总任务：{task_text}\n"
            f"上一版全量 plan 快照：{json.dumps(previous_plan, ensure_ascii=False)}\n"
            f"已完成子任务及结果：{json.dumps(completed_records, ensure_ascii=False)}\n"
            f"刚进行的子任务及结果：{json.dumps(current_record, ensure_ascii=False)}\n\n"
            "请输出一份新的完整计划，要求：\n"
            "- 仅输出 JSON，不要输出任何额外说明。\n"
            "- 顶层字段只能是 thought, subtasks。\n"
            "- subtasks 必须是当前有效计划的完整快照，不是增量 patch。\n"
            '- 每个 subtask 只能包含 id, task, status。\n'
            f'- status 只能是 "{self.STATUS_DONE}"、"{self.STATUS_FAILED}"、"{self.STATUS_PENDING}"。\n'
            "- 对于仍然有效的旧子任务，尽量保留原有 id。\n"
            "- 只有新增的补充子任务才分配新 id。\n"
            f'- 如果总任务尚未完成，计划中必须至少保留一个 "{self.STATUS_PENDING}" 子任务。\n'
            f'- 如果总任务已经完成，计划中的所有 subtask 都必须是 "{self.STATUS_DONE}"。\n'
        )
        return self._run_meta_planner(
            mode="refine",
            prompt=prompt,
            messages=messages,
            tools=tools,
            previous_plan=previous_plan,
            cancel_checker=cancel_checker,
        )

    def _run_meta_planner(
        self,
        mode: str,
        prompt: str,
        messages: List[Dict[str, Any]],
        tools,
        previous_plan: Optional[Dict[str, Any]],
        cancel_checker=None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        if cancel_checker and cancel_checker():
            return None, ""

        seed_messages = [dict(msg) for msg in (messages or []) if msg.get("role") != "system"]
        meta_context = self._create_meta_context()
        meta_context.set_messages(seed_messages)
        meta_context.append_message(self._build_runtime_injected_user_message(prompt, write_through=False))

        hooks = self._build_meta_hooks()
        meta_agent = ReActAgent(
            max_steps=self._META_MAX_STEPS,
            context_manager=meta_context,
            system_prompt=self.system_prompt,
            hooks=hooks,
            hook_error_mode=getattr(self.base_agent, "hook_error_mode", "isolate"),
        )

        for attempt in range(1, self._META_MAX_RETRIES + 1):
            if cancel_checker and cancel_checker():
                return None, ""
            final_text, _ = meta_agent.run(tools=self._meta_tools(tools), cancel_checker=cancel_checker)
            if cancel_checker and cancel_checker():
                return None, ""
            try:
                plan = self._parse_plan(
                    content=final_text,
                    mode=mode,
                    previous_plan=previous_plan,
                )
                return plan, None
            except ValueError as exc:
                if attempt >= self._META_MAX_RETRIES:
                    break
                meta_context.append_message(
                    self._build_runtime_injected_user_message(
                        self._format_meta_retry_prompt(mode, attempt, str(exc)),
                        write_through=False,
                    )
                )

        return None, self._meta_failure_message(mode)

    def _parse_plan(
        self,
        content: Optional[str],
        mode: str,
        previous_plan: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (content or "").strip()
        if not text:
            raise ValueError("empty output")

        data = _extract_json(text)
        if not isinstance(data, dict):
            raise ValueError("output is not valid JSON")

        raw_subtasks = data.get("subtasks")
        if not isinstance(raw_subtasks, list) or not raw_subtasks:
            raise ValueError("subtasks must be a non-empty list")

        previous_items = []
        previous_by_id: Dict[str, Dict[str, Any]] = {}
        previous_by_task: Dict[str, Dict[str, Any]] = {}
        if isinstance(previous_plan, dict):
            previous_items = previous_plan.get("subtasks", []) or []
        for item in previous_items:
            if not isinstance(item, dict):
                continue
            pid = str(item.get("id") or "").strip()
            task = str(item.get("task") or "").strip()
            if pid:
                previous_by_id[pid] = item
            if task and task not in previous_by_task:
                previous_by_task[task] = item

        subtasks: List[Dict[str, str]] = []
        used_ids = set()
        next_index = 1
        for item in raw_subtasks:
            if not isinstance(item, dict):
                raise ValueError("each subtask must be an object")

            task = str(item.get("task") or "").strip()
            if not task:
                raise ValueError("subtask.task is required")

            subtask_id = self._normalize_subtask_id(
                raw_id=item.get("id"),
                task=task,
                used_ids=used_ids,
                next_index_ref=[next_index],
                previous_by_id=previous_by_id,
                previous_by_task=previous_by_task,
            )
            next_index = max(next_index, self._extract_numeric_suffix(subtask_id) + 1)

            raw_status = item.get("status")
            if mode == "plan":
                status = self.STATUS_PENDING
            else:
                status = self._normalize_status(raw_status)
                if status not in self._VALID_STATUSES:
                    raise ValueError("invalid subtask.status")

            used_ids.add(subtask_id)
            subtasks.append({"id": subtask_id, "task": task, "status": status})

        if len(subtasks) > self.max_subtasks:
            subtasks = subtasks[: self.max_subtasks]

        thought = str(data.get("thought", "") or "").strip()
        plan = {"thought": thought, "subtasks": subtasks}

        if mode == "refine":
            if not self._all_done(plan) and not self._next_pending_subtask(plan):
                raise ValueError("refine plan must contain a 未完成 subtask unless all subtasks are 已完成")

        return plan

    def _normalize_subtask_id(
        self,
        raw_id: Any,
        task: str,
        used_ids: set,
        next_index_ref: List[int],
        previous_by_id: Dict[str, Dict[str, Any]],
        previous_by_task: Dict[str, Dict[str, Any]],
    ) -> str:
        candidate = str(raw_id or "").strip()
        if candidate and candidate in previous_by_id and candidate not in used_ids:
            return candidate

        previous_item = previous_by_task.get(task)
        if previous_item:
            previous_id = str(previous_item.get("id") or "").strip()
            if previous_id and previous_id not in used_ids:
                return previous_id

        if candidate and candidate not in used_ids:
            return candidate

        index = max(1, int(next_index_ref[0]))
        while True:
            generated = f"s{index}"
            if generated not in used_ids:
                next_index_ref[0] = index + 1
                return generated
            index += 1

    def _normalize_status(self, value: Any) -> str:
        text = str(value or "").strip()
        mapping = {
            self.STATUS_DONE: self.STATUS_DONE,
            self.STATUS_FAILED: self.STATUS_FAILED,
            self.STATUS_PENDING: self.STATUS_PENDING,
            "done": self.STATUS_DONE,
            "completed": self.STATUS_DONE,
            "complete": self.STATUS_DONE,
            "success": self.STATUS_DONE,
            "failed": self.STATUS_FAILED,
            "error": self.STATUS_FAILED,
            "pending": self.STATUS_PENDING,
            "todo": self.STATUS_PENDING,
            "not_started": self.STATUS_PENDING,
            "未开始": self.STATUS_PENDING,
        }
        return mapping.get(text.lower(), mapping.get(text, ""))

    def _build_meta_hooks(self) -> ReActHooks:
        state = {"ask_used": False}

        def after_llm(event):
            messages = [dict(message) for message in (event.messages or [])]
            last = self._last_assistant_message(messages)
            if not last:
                return messages, event.system_prompt

            tool_calls = last.get("tool_calls")
            if not isinstance(tool_calls, list) or not tool_calls:
                return messages, event.system_prompt

            allowed_calls = []
            for call in tool_calls:
                if self._tool_call_name(call) != "ask_human":
                    continue
                if state["ask_used"]:
                    continue
                if allowed_calls:
                    continue
                allowed_calls.append(call)
                state["ask_used"] = True

            if allowed_calls:
                if len(allowed_calls) != len(tool_calls):
                    last["tool_calls"] = allowed_calls
                return messages, event.system_prompt

            last.pop("tool_calls", None)
            if not str(last.get("content") or "").strip():
                last["content"] = "ask_human 已经使用过一次，必须立刻输出合法 plan JSON。"
            messages.append(
                self._build_runtime_injected_user_message(
                    "[system message] ask_human 已经使用过一次，禁止再次追问，必须立刻输出合法 plan JSON。",
                    write_through=False,
                )
            )
            return messages, event.system_prompt

        return ReActHooks(after_llm=after_llm)

    def _create_meta_context(self) -> ReActContextManager:
        return ReActContextManager(
            context_path=self.context_manager.get_context_path(),
            write_through=False,
            max_tokens=10**9,
            min_keep=1,
            summarizer=None,
        )

    def _meta_tools(self, tools) -> List[Any]:
        allowed = []
        for tool in tools or []:
            if getattr(tool, "name", "") == "ask_human" and hasattr(tool, "run"):
                allowed.append(tool)
        return allowed

    def _has_ask_human(self, tools) -> bool:
        return bool(self._meta_tools(tools))

    def _tool_catalog_text(self, tools) -> str:
        rows = []
        for tool in tools or []:
            name = ""
            description = ""
            if hasattr(tool, "name"):
                name = str(getattr(tool, "name", "") or "")
                description = str(getattr(tool, "description", "") or "")
            elif isinstance(tool, dict):
                function = tool.get("function") or {}
                if isinstance(function, dict):
                    name = str(function.get("name") or "")
                    description = str(function.get("description") or "")
            if not name:
                continue
            rows.append(f"- {name}: {description or '(no description)'}")
        return "\n".join(rows) if rows else "- (no tools registered)"

    def _format_meta_retry_prompt(self, mode: str, attempt: int, reason: str) -> str:
        return (
            f"[system message] 上一轮{mode}输出不符合格式（第 {attempt} 次失败）：{reason}。"
            "请立刻输出合法 JSON plan，只能包含 thought 和 subtasks。"
        )

    def _meta_failure_message(self, mode: str) -> str:
        return (
            f"ReCAP {mode} 连续多次未能输出合法 plan，已停止继续尝试。"
            "当前存在格式不规范故障，可能是模型能力不足或当前提示/上下文冲突导致的；建议切换更强的 LLM 后重试。"
        )

    def _all_done(self, plan: Optional[Dict[str, Any]]) -> bool:
        if not isinstance(plan, dict):
            return False
        subtasks = plan.get("subtasks")
        if not isinstance(subtasks, list) or not subtasks:
            return False
        return all(str(item.get("status") or "") == self.STATUS_DONE for item in subtasks if isinstance(item, dict))

    def _next_pending_subtask(self, plan: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not isinstance(plan, dict):
            return None
        for item in plan.get("subtasks", []) or []:
            if isinstance(item, dict) and str(item.get("status") or "") == self.STATUS_PENDING:
                return item
        return None

    def _completed_records(self, plan: Dict[str, Any], task_results: Dict[str, str]) -> List[Dict[str, str]]:
        records: List[Dict[str, str]] = []
        for item in plan.get("subtasks", []) or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status") or "") != self.STATUS_DONE:
                continue
            subtask_id = str(item.get("id") or "").strip()
            records.append(
                {
                    "id": subtask_id,
                    "task": str(item.get("task") or "").strip(),
                    "status": self.STATUS_DONE,
                    "result": task_results.get(subtask_id, ""),
                }
            )
        return records

    def _record_for_task(self, task: Dict[str, Any], result: str) -> Dict[str, str]:
        return {
            "id": str(task.get("id") or "").strip(),
            "task": str(task.get("task") or "").strip(),
            "status": str(task.get("status") or self.STATUS_PENDING),
            "result": result,
        }

    def _format_reinject(
        self,
        task_text: str,
        previous_plan: Dict[str, Any],
        current_task: Dict[str, Any],
        result: str,
    ) -> str:
        return (
            "[ReCAP REINJECT]\n"
            f"Task: {task_text}\n"
            f"Executed: {json.dumps(self._record_for_task(current_task, result), ensure_ascii=False)}\n"
            f"PreviousPlan: {json.dumps(previous_plan, ensure_ascii=False)}"
        )

    def _latest_user_task(self, messages: List[Dict[str, str]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return (msg.get("content") or "").strip()
        return ""

    def _last_assistant_message(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for message in reversed(messages or []):
            if isinstance(message, dict) and message.get("role") == "assistant":
                return message
        return None

    def _tool_call_name(self, call: Any) -> str:
        if isinstance(call, dict):
            function = call.get("function") or {}
            if isinstance(function, dict):
                return str(function.get("name") or "")
            return ""
        function = getattr(call, "function", None)
        return str(getattr(function, "name", "") or "")

    def _extract_numeric_suffix(self, value: str) -> int:
        if not isinstance(value, str):
            return 0
        digits = ""
        for ch in reversed(value):
            if not ch.isdigit():
                break
            digits = ch + digits
        return int(digits) if digits else 0

    def _runtime_injected_user_turn_meta(self) -> Dict[str, Any]:
        return {
            "source": self.RUNTIME_MESSAGE_SOURCE,
            "preferred_response_language": self.RUNTIME_MESSAGE_LANGUAGE,
            "request_kind": self.SYSTEM_MESSAGE_REQUEST_KIND,
            "message_time": iso_timestamp(),
            "attachments": [],
        }

    def _build_runtime_injected_user_message(self, content: str, *, write_through: bool) -> Dict[str, Any]:
        text = str(content or "")
        meta = self._runtime_injected_user_turn_meta()
        if write_through:
            return {"role": "user", "content": text, "user_turn_meta": meta}
        frame = build_request_frame(
            message_id="",
            content=text,
            user_turn_meta=meta,
        )
        return {"role": "user", "content": json.dumps(frame, ensure_ascii=False)}

    def _sync_plan_file(self, plan: Dict[str, Any]) -> None:
        if not isinstance(plan, dict):
            return
        try:
            write_plan_file(
                self.context_manager.get_context_path(),
                self._format_plan_markdown(plan),
            )
        except Exception:
            return

    def _format_plan_markdown(self, plan: Dict[str, Any]) -> str:
        thought = str(plan.get("thought") or "").strip()
        lines = ["# Agent Plan", ""]
        if thought:
            lines.extend(["## Thought", thought, ""])
        lines.append("## Subtasks")
        for item in list(plan.get("subtasks") or []):
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- [{str(item.get('status') or '').strip() or self.STATUS_PENDING}] "
                f"{str(item.get('id') or '').strip()}: {str(item.get('task') or '').strip()}"
            )
        return "\n".join(lines).strip() + "\n"


def _extract_json(text: str):
    if not text:
        return None
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") and part.endswith("}"):
                try:
                    return json.loads(part)
                except Exception:
                    pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None
