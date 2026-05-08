# -*- coding: utf-8 -*-
"""WeClaw: compose ReAct/ReCAP, context, session manager, and tools."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
import os

from core.context.lifecycle import LlmSummarizer, ReActContextManager
from core.history.session_event_types import iso_timestamp
from core.history.session_jsonl_store import SessionJsonlStore
from core.loop.react_loop import ReActAgent, ReActHooks
from core.loop.recap_loop import ReCAPAgent
from core.session.manager import SessionManager
from core.task_runtime.plan_file import ensure_plan_file
from integrations.browser import BrowserService
from integrations.llm.provider import get_response
from integrations.mcp.runtime import MCPRuntime
from integrations.mcp.sync import sync_mcp_runtime
from tools.local.alarm_tool import AlarmTool
from tools.local.ask_human_tool import AskHumanManager, AskHumanTool
from tools.local.skill_tool import SkillRuntime
from tools.local.sub_agent_tool import SubAgentTool
from tools.local.thinking_tool import ThinkingTool
from tools.local.wait_for_update_tool import WaitForUpdateTool
from core.task_runtime.controller_tools import build_task_runtime_tools
from core.prompts import (
    build_main_session_runtime_constraints,
    build_task_session_runtime_constraints,
    build_workspace_runtime_block,
    load_or_build_system_prompt,
    load_memory_for_prompt,
    load_workspace_prompt_bundle,
    render_system_prompt,
)
from core.workspace.layout import (
    ensure_workspace_layout,
    ensure_workspace_layout_for_source,
    extract_session_id_from_path,
)
from core.workspace.state_paths import resolve_current_agent_id


class WeClawBot:
    """Unified chatbot entry class."""

    _TASK_CONTROLLER_TOOL_NAMES = {
        "task_create",
        "task_list",
        "task_query",
        "task_update",
        "task_finish",
    }
    SYSTEM_MESSAGE_REQUEST_KIND = "system_message"
    RUNTIME_MESSAGE_SOURCE = "runtime"
    RUNTIME_MESSAGE_LANGUAGE = "zh"
    WAIT_FOR_UPDATE_TOOL_NAME = "wait_for_update"
    WAIT_FOR_UPDATE_FINAL_PROMPT = (
        "[system message]\n"
        "You chose to wait for a future update.\n"
        "End the current turn now.\n"
        "Do not call any more tools.\n"
        "Reply to the user with one brief assistant message saying the task is continuing in the background "
        "and that you will update them when there is meaningful progress."
    )
    WAIT_FOR_UPDATE_FALLBACK_REPLY = "任务正在后台继续，有新进展时我会告诉你。请问你还有别的需要吗？"

    def __init__(
        self,
        history_dir: str,
        max_rounds: int = 20,
        max_steps: int = 4,
        system_prompt: Optional[str] = None,
        agent_id: Optional[str] = None,
        agent_root: Optional[str] = None,
    ):
        self._system_handler = None
        self.project_root = str(Path(__file__).resolve().parents[2])
        self.agent_id = resolve_current_agent_id(agent_id)
        self.workspace_layout = ensure_workspace_layout_for_source(self.project_root, agent_id=self.agent_id)
        if agent_root:
            normalized_agent_root = os.path.abspath(agent_root)
            if os.path.abspath(self.workspace_layout.agent_root) != normalized_agent_root:
                raise ValueError("agent_root does not match resolved agent_id")
            self.workspace_layout = ensure_workspace_layout(normalized_agent_root, source_root=self.project_root, agent_id=self.agent_id)
        self.agent_id = self.workspace_layout.agent_id
        self.agent_root = self.workspace_layout.agent_root
        self.workspace_root = self.workspace_layout.workspace_root

        self.max_steps = max_steps
        self.summarizer = LlmSummarizer()
        self.session_manager = SessionManager(history_dir, max_rounds=max_rounds, agent_id=self.agent_id)
        self.context_manager: Optional[ReActContextManager] = None
        self.ask_human_manager = AskHumanManager()

        self.skill_runtime = SkillRuntime(project_root=self.project_root, workspace_root=self.agent_root)
        self.skill_tool = self.skill_runtime.create_tool(register=True)
        self.browser_service = BrowserService(workspace_root=self.agent_root, source_root=self.project_root)
        self.mcp_runtime = MCPRuntime(
            self.project_root,
            client_dir=self.workspace_layout.mcp_clients_root,
            secrets_path=self.workspace_layout.mcp_secrets_path,
        )
        self._base_system_prompt = system_prompt or self._default_system_prompt()
        self._dynamic_mcp_prompt_block = ""
        self.system_prompt = self._compose_runtime_system_prompt()

        self._react_hooks = ReActHooks()
        self._react_hook_error_mode = "isolate"
        self._alarm_scheduler = None

        self._direct_tools = self._load_tools()
        self._mcp_tools = []
        self.tools = list(self._direct_tools)
        self.refresh_mcp()

    def handle_message(self, user_id: str, content: str, user_turn_meta: Optional[dict] = None) -> Optional[str]:
        """Process one user message and return assistant text."""
        return self.run_task(user_id, content, user_turn_meta=user_turn_meta)

    def set_react_hooks(self, hooks: ReActHooks) -> None:
        """Set bot-level ReAct hooks; applied to each run-created ReActAgent."""
        self._react_hooks = hooks

    def get_react_hooks(self) -> ReActHooks:
        """Get current bot-level ReAct hooks."""
        return self._react_hooks

    def set_react_hook_error_mode(self, mode: str) -> None:
        """Set ReAct hook error strategy for future runs."""
        self._react_hook_error_mode = mode if mode in {"isolate", "strict"} else "isolate"

    def run_task(
        self,
        user_id: str,
        content: str,
        cancel_checker=None,
        stream: bool = False,
        on_token=None,
        on_reasoning=None,
        user_turn_meta: Optional[dict] = None,
    ) -> Optional[str]:
        """Run one task with optional cancel checks."""
        content = (content or "").strip()
        if not content:
            return None

        command_reply = self._handle_command(user_id, content)
        if command_reply is not None:
            return command_reply

        session_path = self.session_manager.get_or_create_session_path(user_id)
        self.refresh_mcp()
        self._refresh_session_system_prompt(session_path)
        context_manager = self._create_context_manager(session_path)
        self.context_manager = context_manager
        react_agent, _recap_agent = self._create_agents_for_run(context_manager)
        cancel_recorded = False

        main_tools = self._tools_for_session_kind("main_session")
        self._bind_tool_user_context(
            main_tools,
            user_id,
            session_path=session_path,
            cancel_checker=cancel_checker,
        )
        self._bind_thinking_context(main_tools)

        user_message = {"role": "user", "content": content}
        if user_turn_meta:
            user_message["user_turn_meta"] = dict(user_turn_meta)
        context_manager.append_message(user_message)

        if cancel_checker and cancel_checker():
            if not cancel_recorded:
                self._record_cancel_dialog(context_manager)
                cancel_recorded = True
            return None

        reply_text, tool_events = react_agent.run(
            tools=main_tools,
            cancel_checker=cancel_checker,
            stream=bool(stream),
            on_token=on_token,
            on_reasoning=on_reasoning,
        )
        if self._last_run_requested_wait_for_update(tool_events):
            reply_text = self._finalize_wait_for_update_turn(
                context_manager,
                react_agent,
                cancel_checker=cancel_checker,
            )

        if cancel_checker and cancel_checker():
            if not cancel_recorded:
                self._record_cancel_dialog(context_manager)
                cancel_recorded = True
            return None

        self.session_manager.maybe_rename_after_rounds(user_id, context_manager.get_context_path())
        return reply_text

    def run_task_in_task_session(
        self,
        session_path: str,
        *,
        task_id: str = "",
        cancel_checker=None,
    ) -> dict:
        task_session_path = str(session_path or "").strip()
        if not task_session_path:
            return {"status": "failed", "error": "task_session_path_required"}

        self.refresh_mcp()
        self._refresh_session_system_prompt(task_session_path)
        ensure_plan_file(task_session_path)
        context_manager = self._create_context_manager(task_session_path)
        self.context_manager = context_manager
        react_agent, recap_agent = self._create_agents_for_run(context_manager)
        react_agent.system_prompt = self._build_task_session_system_prompt()
        recap_agent.system_prompt = react_agent.system_prompt

        task_user_id = f"task:{str(task_id or extract_session_id_from_path(task_session_path)).strip() or 'default'}"
        pending_questions: list[dict] = []

        def _capture_task_question(_user_id: str, question: str) -> None:
            clean_question = str(question or "").strip()
            if not clean_question:
                return
            pending_questions.append(
                {
                    "question": clean_question,
                    "created_at": iso_timestamp(),
                }
            )

        task_tools = self._tools_for_session_kind("task_session")
        self._bind_tool_user_context(
            task_tools,
            task_user_id,
            session_path=task_session_path,
            cancel_checker=cancel_checker,
            ask_handler_override=_capture_task_question,
            ask_non_blocking=True,
        )
        self._bind_thinking_context(task_tools)

        messages = context_manager.get_messages()
        if not messages:
            return {"status": "active", "run_phase": "idle_waiting_scheduler", "result_summary": ""}

        use_recap = self._should_use_recap_for_task_session(messages)
        if use_recap:
            reply_text, _ = recap_agent.run(tools=task_tools, cancel_checker=cancel_checker)
        else:
            reply_text, _ = react_agent.run(tools=task_tools, cancel_checker=cancel_checker)

        result_text = str(reply_text or "").strip()
        if pending_questions:
            return {
                "status": "waiting",
                "run_phase": "waiting_human_or_external",
                "result_summary": "",
                "latest_progress_summary": result_text[:200] if result_text else pending_questions[0]["question"],
                "pending_questions": pending_questions,
            }
        return {
            "status": "finished" if result_text else "active",
            "run_phase": "idle_waiting_scheduler" if result_text else "llm_generating",
            "result_summary": result_text,
            "latest_progress_summary": result_text[:200],
        }

    def _refresh_session_system_prompt(self, session_path: str, force_refresh: bool = False) -> str:
        """Load or render the effective system prompt for one session."""
        session_id = extract_session_id_from_path(session_path)
        bundle = load_workspace_prompt_bundle(self.workspace_layout)
        self.skill_runtime.refresh("")
        skills_runtime = self.skill_runtime._snapshot.skills_prompt_block.strip() or "No active skills."
        workspace_runtime = build_workspace_runtime_block(self.workspace_layout, session_id)
        rendered_prompt = render_system_prompt(
            template_text=bundle["SYSTEM_PROMPT.md"],
            fields={
                "highest_priority_runtime_constraints": build_main_session_runtime_constraints(),
                "soul_content": bundle["SOUL.md"],
                "identity_content": bundle["IDENTITY.md"],
                "user_content": bundle["USER.md"],
                "agent_content": bundle["AGENT.md"],
                "memory_content": load_memory_for_prompt(
                    os.path.join(self.workspace_layout.prompt_root, "MEMORY.md")
                ),
                "workspace_runtime": workspace_runtime,
                "skills_runtime": skills_runtime,
            },
        )
        source_hash = str(hash(rendered_prompt))
        resolved_prompt = load_or_build_system_prompt(
            history_path=session_path,
            rendered_prompt=rendered_prompt,
            source_hash=source_hash,
            force_refresh=force_refresh,
        )
        self._base_system_prompt = resolved_prompt
        self.system_prompt = self._compose_runtime_system_prompt()
        return resolved_prompt

    def _refresh_dynamic_mcp_prompt_block(self, snapshot=None) -> str:
        """Rebuild the MCP runtime overlay without mutating the frozen session prompt."""
        current_snapshot = snapshot if snapshot is not None else self.mcp_runtime.snapshot()
        lines = ["\n\n[MCP Runtime]"]

        active_clients = list(getattr(current_snapshot, "active_clients", []) or [])
        if active_clients:
            lines.append("Active clients:")
            for client in active_clients:
                client_id = str(getattr(client, "client_id", "") or getattr(client, "server_id", "") or "").strip()
                client_name = str(getattr(client, "name", "") or "").strip()
                label = client_name or client_id or "unknown"
                if client_name and client_id and client_name != client_id:
                    label = f"{client_name} ({client_id})"
                lines.append(f"- {label}")
        else:
            lines.append("Active clients: none")

        active_tool_names = []
        seen_tool_names = set()
        for tool in list(getattr(current_snapshot, "active_tools", []) or []):
            name = str(getattr(tool, "name", "") or "").strip()
            if not name or name in seen_tool_names:
                continue
            active_tool_names.append(name)
            seen_tool_names.add(name)
        if active_tool_names:
            lines.append("Active tools:")
            lines.extend(f"- {name}" for name in active_tool_names)
        else:
            lines.append("Active tools: none")

        configured_rows = []
        if hasattr(current_snapshot, "configured_rows"):
            configured_rows = list(current_snapshot.configured_rows() or [])
        blocked_clients = []
        for row in configured_rows:
            if not isinstance(row, dict):
                continue
            if not row.get("blocks_chat"):
                continue
            if str(row.get("mode") or "").strip() != "local":
                continue
            blocked_clients.append(str(row.get("client_id") or row.get("name") or "").strip())
        if blocked_clients:
            lines.append("Blocked local clients:")
            lines.extend(f"- {client_id}" for client_id in blocked_clients if client_id)

        self._dynamic_mcp_prompt_block = "\n".join(lines)
        self.system_prompt = self._compose_runtime_system_prompt()
        return self._dynamic_mcp_prompt_block

    def _compose_runtime_system_prompt(self) -> str:
        base_prompt = str(getattr(self, "_base_system_prompt", "") or "")
        overlay = str(getattr(self, "_dynamic_mcp_prompt_block", "") or "")
        return base_prompt + overlay

    def _strip_highest_priority_constraints_section(self, prompt_text: str) -> str:
        text = str(prompt_text or "")
        marker = "# Highest-Priority Runtime Constraints\n"
        if not text.startswith(marker):
            return text
        body = text[len(marker):]
        next_heading = body.find("\n# ")
        if next_heading == -1:
            return ""
        return body[next_heading + 1 :]

    def _create_context_manager(self, session_path: str) -> ReActContextManager:
        session_dir = os.path.dirname(os.path.abspath(session_path))
        return ReActContextManager(
            context_path=session_path,
            agent_root=self.agent_root,
            workspace_root=self.workspace_root,
            tool_output_dir=os.path.join(session_dir, "tool_outputs"),
            summarizer=self.summarizer,
        )

    def current_workspace_session_id(self) -> str:
        """Map the current context file to one stable workspace session id."""
        if self.context_manager is not None:
            context_path = self.context_manager.get_context_path()
            return extract_session_id_from_path(context_path)
        return "default"

    def _create_agents_for_run(
        self,
        context_manager: ReActContextManager,
    ) -> tuple[ReActAgent, ReCAPAgent]:
        react_agent = ReActAgent(
            max_steps=self.max_steps,
            context_manager=context_manager,
            system_prompt=self.system_prompt,
            hooks=self._react_hooks,
            hook_error_mode=self._react_hook_error_mode,
        )
        recap_agent = ReCAPAgent(
            base_agent=react_agent,
            context_manager=context_manager,
        )
        recap_agent.system_prompt = self.system_prompt
        return react_agent, recap_agent

    def _record_cancel_dialog(self, context_manager: ReActContextManager) -> None:
        context_manager.append_messages(
            [
                {
                    "role": "user",
                    "content": "[cancelled]",
                    "user_turn_meta": {
                        "source": self.RUNTIME_MESSAGE_SOURCE,
                        "preferred_response_language": self.RUNTIME_MESSAGE_LANGUAGE,
                        "request_kind": self.SYSTEM_MESSAGE_REQUEST_KIND,
                        "message_time": iso_timestamp(),
                        "attachments": [],
                    },
                },
                {"role": "assistant", "content": "ok"},
            ]
        )

    def _last_run_requested_wait_for_update(self, tool_events) -> bool:
        for event in list(tool_events or []):
            if not isinstance(event, dict):
                continue
            if str(event.get("tool") or "") == self.WAIT_FOR_UPDATE_TOOL_NAME and str(event.get("wait_for_update") or "") == "1":
                return True
        return False

    def _finalize_wait_for_update_turn(
        self,
        context_manager: ReActContextManager,
        react_agent: ReActAgent,
        *,
        cancel_checker=None,
    ) -> str:
        context_manager.append_message(
            {
                "role": "user",
                "content": self.WAIT_FOR_UPDATE_FINAL_PROMPT,
                "user_turn_meta": self._runtime_system_user_turn_meta(),
            }
        )
        for _ in range(3):
            if cancel_checker and cancel_checker():
                return ""
            final_text, tried_tool = react_agent.run_final_without_tools(
                cancel_checker=cancel_checker,
            )
            if not tried_tool:
                return str(final_text or "").strip()
        context_manager.append_message({"role": "assistant", "content": self.WAIT_FOR_UPDATE_FALLBACK_REPLY})
        return self.WAIT_FOR_UPDATE_FALLBACK_REPLY

    def _runtime_system_user_turn_meta(self) -> dict:
        return {
            "source": self.RUNTIME_MESSAGE_SOURCE,
            "preferred_response_language": self.RUNTIME_MESSAGE_LANGUAGE,
            "request_kind": self.SYSTEM_MESSAGE_REQUEST_KIND,
            "message_time": iso_timestamp(),
            "attachments": [],
        }

    def _handle_command(self, user_id: str, content: str) -> Optional[str]:
        if content.startswith("/listhistory"):
            names = self.session_manager.list_sessions(user_id)
            return "No history sessions found." if not names else "History sessions:\n" + "\n".join(names)

        if content.startswith("/history"):
            parts = content.split(maxsplit=1)
            if len(parts) < 2:
                return "Usage: /history <session-name>"
            target = self.session_manager.switch_session(user_id, parts[1].strip())
            if target:
                name = self.session_manager.get_display_name(target)
                return f"Switched to history session: {name}"
            return "History session not found."

        if content.startswith("/newhistory"):
            path = self.session_manager.create_new_session(user_id)
            name = self.session_manager.get_display_name(path)
            return f"Created new history session: {name}"

        return None

    def _should_use_recap(self, messages) -> bool:
        """Compatibility wrapper for task-session routing."""
        return self._should_use_recap_for_task_session(messages)

    def _should_use_recap_for_task_session(self, messages) -> bool:
        """Use a small LLM router to choose ReCAP for complex task-session work."""
        prompt = (
            "你是 task session 的执行路由器。判断当前最新任务是否属于复杂任务。"
            "如果完成它预计需要两步以上的 LLM 调用，或者明显需要多阶段规划、执行、反思与重规划，输出 RECAP；"
            "否则输出 REACT。只输出 RECAP 或 REACT。"
        )
        inputs = [{"role": "system", "content": self._build_task_session_system_prompt()}]
        inputs.extend(list(messages or [])[-12:])
        inputs.append({"role": "user", "content": prompt})
        try:
            resp = get_response(inputs, tools=None, stream=False)
            text = str(getattr(resp, "content", "") or "").strip().upper()
            if "RECAP" in text:
                return True
        except Exception:
            pass
        return False

    def _default_system_prompt(self) -> str:
        return (
            "# WeClaw System Prompt\n\n"
            "You are WeClaw, an assistant running inside the local runtime.\n\n"
            "Rules:\n"
            "- Use tools carefully and only when needed.\n"
            "- Keep changes inside the allowed workspace.\n"
            "- Prefer concise, accurate answers unless deeper reasoning is required.\n"
        )

    def _build_task_session_system_prompt(self) -> str:
        return (
            "# Highest-Priority Runtime Constraints\n"
            f"{build_task_session_runtime_constraints()}\n\n"
            f"{self._strip_highest_priority_constraints_section(self.system_prompt)}\n\n"
            "[Task Session Runtime]\n"
            "You are operating inside a persistent task session.\n"
            "Do not create or modify tasks from inside this session.\n"
            "Focus only on the assigned task and produce concrete progress or a final result for the parent session.\n"
        )

    def _tools_for_session_kind(self, session_kind: str):
        kind = str(session_kind or "main_session").strip() or "main_session"
        if kind == "task_session":
            return list(getattr(self, "_mcp_tools", []) or [])
        return list(getattr(self, "_direct_tools", []) or [])

    def _load_tools(self):
        return (
            build_task_runtime_tools(layout=self.workspace_layout)
            + [
                AskHumanTool(self.ask_human_manager),
                WaitForUpdateTool(),
            ]
        )

    def refresh_skills(self):
        return self.refresh_mcp()

    def refresh_mcp(self):
        return sync_mcp_runtime(self)

    def _bind_tool_user_context(
        self,
        tools,
        user_id: str,
        session_path: str,
        cancel_checker=None,
        ask_handler_override=None,
        ask_non_blocking: bool = False,
    ) -> None:
        for tool in list(tools or []):
            if not hasattr(tool, "set_context"):
                continue
            if isinstance(tool, ThinkingTool):
                continue
            if isinstance(tool, AlarmTool):
                tool.set_context(
                    user_id=user_id,
                    on_trigger=self._handle_system_message,
                    schedule_alarm=self._alarm_scheduler,
                    session_path=session_path,
                )
            elif isinstance(tool, AskHumanTool):
                tool.set_context(
                    user_id,
                    on_ask=ask_handler_override or self._handle_ask_human,
                    cancel_checker=cancel_checker,
                    non_blocking=ask_non_blocking,
                )
            elif isinstance(tool, SubAgentTool):
                tool.set_context(
                    user_id=user_id,
                    parent_context_path=session_path,
                    on_trigger=self._handle_system_message,
                )
            else:
                try:
                    tool.set_context(user_id, session_path=session_path, on_trigger=self._handle_system_message)
                except TypeError:
                    try:
                        tool.set_context(user_id, self._handle_system_message)
                    except TypeError:
                        tool.set_context(user_id)

    def _bind_thinking_context(self, tools) -> None:
        if self.context_manager is None:
            return
        for tool in list(tools or []):
            if isinstance(tool, ThinkingTool):
                tool.set_context(self.context_manager.get_messages)
                break

    def _handle_system_message(self, user_id: str, content: str) -> Optional[str]:
        handler = self._system_handler
        if handler:
            return handler(user_id, content)
        return self.handle_message(user_id, content)

    def set_system_handler(self, handler) -> None:
        self._system_handler = handler

    def set_alarm_scheduler(self, scheduler) -> None:
        self._alarm_scheduler = scheduler

    def _handle_ask_human(self, user_id: str, question: str) -> None:
        handler = getattr(self, "_ask_handlers", {}).get(user_id)
        if handler:
            handler(user_id, question)

    def set_ask_handler(self, user_id: str, handler) -> None:
        if not hasattr(self, "_ask_handlers"):
            self._ask_handlers = {}
        self._ask_handlers[user_id] = handler

    def clear_ask_handler(self, user_id: str) -> None:
        if hasattr(self, "_ask_handlers"):
            self._ask_handlers.pop(user_id, None)

    def has_pending_human(self, user_id: str) -> bool:
        return self.ask_human_manager.has_pending(user_id)

    def provide_human_input(self, user_id: str, content: str) -> bool:
        return self.ask_human_manager.provide(user_id, content)

    def cancel_pending_human(self, user_id: str) -> None:
        self.ask_human_manager.cancel(user_id)

    def _load_config(self) -> dict:
        config_path = os.getenv("WE_CLAW_CONFIG")
        if not config_path:
            default_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
            config_path = default_path if os.path.exists(default_path) else None
        if not config_path or not os.path.exists(config_path):
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}
