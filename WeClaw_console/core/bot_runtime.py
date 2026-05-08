# -*- coding: utf-8 -*-
"""Runtime adapter for WeClaw with SSE-friendly event streaming."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid

from core.history.session_event_types import build_message_event
from core.history.render_reader import replay_render_rows
from core.history.session_jsonl_store import SessionJsonlStore
from core.prompts import load_workspace_prompt_bundle, render_system_prompt
from core.task_runtime.plan_file import read_plan_file
from core.task_runtime.scheduler import TaskScheduler
from core.task_runtime.store import TaskRuntimeStore
from core.agent.bot_runtime import WeClawBot
from integrations.mcp.schema import MCPClientConfig
from tools.local.sub_agent_tool import SubAgentTool

from .file_ingest import FileIngestStore
from .react_trace_bridge import build_react_hooks
from .session_indexer import SessionIndexer
from .stream_bus import EventStreamBus


class BotRuntime:
    """Single runtime coordinating bot execution, traces, and SSE queues."""

    _CONSOLE_HIDDEN_PREFIXES = (
        "[system message]",
        "[recap plan]",
        "[recap update]",
        "[recap reinject]",
        "[subtask]",
    )

    def __init__(
        self,
        history_dir: str,
        agent_root: str,
        agent_id: str = "main",
        max_rounds: int = 20,
        max_steps: int = 20,
        web_user_id: str = "web:local",
        runtime_config_store: Any | None = None,
    ):
        self.history_dir = str(Path(history_dir).resolve())
        self.agent_root = str(Path(agent_root).resolve())
        self.web_user_id = web_user_id

        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.agent_root, exist_ok=True)

        self.bot = WeClawBot(
            history_dir=self.history_dir,
            max_rounds=max_rounds,
            max_steps=max_steps,
            agent_id=agent_id,
            agent_root=self.agent_root,
        )
        self.indexer = SessionIndexer(self.history_dir)
        self.files = FileIngestStore()
        self.bus = EventStreamBus()
        self.runtime_config_store = runtime_config_store

        self._lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._cancel_flags: Dict[str, threading.Event] = {}
        self._request_user: Dict[str, str] = {}

    def _build_react_hooks(self, emitter):
        """Create runtime hooks for an external gateway/controller."""
        return build_react_hooks(emitter)

    def _resolve_reply_language(self, value: Any) -> str:
        text = str(value or "").strip().lower()
        if text in {"zh", "en"}:
            return text
        store = self.runtime_config_store
        if store is not None:
            try:
                return "en" if store.preferred_response_language() == "en" else "zh"
            except Exception:
                pass
        return "zh"

    # ---- MCP management ----

    def list_mcp_discovered(self) -> List[Dict[str, Any]]:
        return self.bot.mcp_runtime.discover_rows()

    def list_mcp_clients(self) -> List[Dict[str, Any]]:
        return self.bot.mcp_runtime.configured_rows()

    def sync_mcp(self) -> Dict[str, Any]:
        with self._run_lock:
            snapshot = self.bot.refresh_mcp()
        return self._mcp_payload(snapshot)

    def upsert_mcp_client(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        config = MCPClientConfig(
            client_id=str(payload.get("client_id") or "").strip(),
            name=str(payload.get("name") or "").strip(),
            description=str(payload.get("description") or "").strip(),
            enabled=bool(payload.get("enabled", True)),
            mode=str(payload.get("mode") or "local"),
            transport=str(payload.get("transport") or ""),
            server_id=str(payload.get("server_id") or ""),
            endpoint=str(payload.get("endpoint") or ""),
            command=str(payload.get("command") or "").strip(),
            args=[str(item) for item in (payload.get("args") or [])],
            cwd=str(payload.get("cwd") or "").strip(),
            enabled_tools=list(payload.get("enabled_tools") or []),
            env=dict(payload.get("env") or {}),
            headers=dict(payload.get("headers") or {}),
            secret_refs=dict(payload.get("secret_refs") or {}),
            metadata=dict(payload.get("metadata") or {}),
        ).normalized()
        if not config.client_id:
            raise ValueError("client_id is required.")
        if config.mode == "local" and not config.server_id and not config.command:
            raise ValueError("local client requires server_id or command.")
        if config.mode == "remote" and not config.endpoint:
            raise ValueError("remote client requires endpoint.")
        original_client_id = str(payload.get("original_client_id") or "").strip()
        secret_values = dict(payload.get("secret_values") or {})
        with self._run_lock:
            snapshot = self.bot.mcp_runtime.upsert_client(
                config,
                target=self.bot,
                original_client_id=original_client_id,
                secret_values=secret_values,
            )
        return self._mcp_payload(snapshot)

    def toggle_mcp_client(self, client_id: str, enabled: bool) -> Dict[str, Any]:
        with self._run_lock:
            snapshot = self.bot.mcp_runtime.toggle_client(client_id, enabled=enabled, target=self.bot)
        return self._mcp_payload(snapshot)

    def delete_mcp_client(self, client_id: str) -> Dict[str, Any]:
        with self._run_lock:
            snapshot = self.bot.mcp_runtime.delete_client(client_id, target=self.bot)
        return self._mcp_payload(snapshot)

    def _mcp_payload(self, snapshot) -> Dict[str, Any]:
        client_rows = snapshot.configured_rows()
        blocking_clients = [
            row for row in client_rows
            if bool(row.get("blocks_chat")) and str(row.get("mode") or "").strip() == "local"
        ]
        return {
            "discovered": snapshot.discovered_rows(),
            "clients": client_rows,
            "active_tools": snapshot.tool_rows(),
            "chat_guard": {
                "blocked": bool(blocking_clients),
                "reason": "local_mcp_not_ready" if blocking_clients else "",
                "client_ids": [str(row.get("client_id") or "").strip() for row in blocking_clients if str(row.get("client_id") or "").strip()],
            },
        }

    # ---- Session view helpers ----

    def list_sessions(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for item in self.indexer.list_sessions():
            row = asdict(item)
            external_user_id = str(row.get("user_id", "")).strip() or self.web_user_id
            row["user_id"] = external_user_id
            row["channel_prefix"] = self._detect_channel_prefix(external_user_id)
            rows.append(row)
        return rows

    def create_web_session(self) -> Dict[str, Any]:
        path = self.bot.session_manager.create_new_session(self.web_user_id)
        name = self.bot.session_manager.get_display_name(path)
        return {
            "user_id": self.web_user_id,
            "session_name": name,
            "path": path,
        }

    def select_session(self, user_id: str, session_name: str) -> Dict[str, Any]:
        external_uid = (user_id or "").strip() or self.web_user_id
        target = self.bot.session_manager.switch_session(external_uid, session_name)
        if not target:
            return {"success": False, "message": "session not found"}
        return {
            "success": True,
            "user_id": external_uid,
            "session_name": self.bot.session_manager.get_display_name(target),
            "path": target,
        }

    def get_session_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        external_uid = (user_id or "").strip() or self.web_user_id
        return self.indexer.get_messages(external_uid, session_name)

    def get_session_render_messages(self, user_id: str, session_name: str) -> List[Dict[str, Any]]:
        raw = self.get_session_messages(user_id, session_name)
        return self._normalize_messages_for_console(raw)

    def get_task_events(self, user_id: str, session_name: str, task_id: str) -> Dict[str, Any]:
        session_path = self._resolve_session_path(user_id, session_name, update_current=False)
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            raise ValueError("task_id_required")
        session_id = self.bot.session_manager._session_id_from_path(session_path)
        store, _scheduler = self._build_task_runtime_controller()
        task_state = store.read_task_state(session_id, clean_task_id)
        events = store.read_task_events(session_id, clean_task_id)
        return {
            "user_id": str(user_id or "").strip() or self.web_user_id,
            "session_name": self.bot.session_manager.get_display_name(session_path),
            "session_id": session_id,
            "task_id": clean_task_id,
            "task_title": str(task_state.get("title") or ""),
            "events": events,
        }

    def list_tasks(self, user_id: str, session_name: str) -> Dict[str, Any]:
        session_path = self._resolve_session_path(user_id, session_name, update_current=False)
        session_id = self.bot.session_manager._session_id_from_path(session_path)
        store, _scheduler = self._build_task_runtime_controller()
        items: List[Dict[str, Any]] = []
        for row in store.list_task_states(session_id):
            items.append(
                {
                    "task_id": str(row.get("task_id") or ""),
                    "title": str(row.get("title") or ""),
                    "status": str(row.get("status") or ""),
                    "priority": str(row.get("priority") or ""),
                    "latest_progress_summary": str(row.get("latest_progress_summary") or ""),
                    "pending_questions": list(row.get("pending_questions") or []),
                    "updated_at": str(row.get("updated_at") or ""),
                }
            )
        items.sort(key=lambda item: (str(item.get("updated_at") or ""), str(item.get("task_id") or "")), reverse=True)
        return {
            "user_id": str(user_id or "").strip() or self.web_user_id,
            "session_name": self.bot.session_manager.get_display_name(session_path),
            "session_id": session_id,
            "tasks": items,
        }

    def get_task_detail(self, user_id: str, session_name: str, task_id: str) -> Dict[str, Any]:
        session_path = self._resolve_session_path(user_id, session_name, update_current=False)
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            raise ValueError("task_id_required")
        session_id = self.bot.session_manager._session_id_from_path(session_path)
        store, _scheduler = self._build_task_runtime_controller()
        task_state = store.read_task_state(session_id, clean_task_id)
        task_history_path = self.bot.workspace_layout.task_session_history_path(session_id, clean_task_id)
        return {
            "user_id": str(user_id or "").strip() or self.web_user_id,
            "session_name": self.bot.session_manager.get_display_name(session_path),
            "session_id": session_id,
            "task": {
                "task_id": clean_task_id,
                "title": str(task_state.get("title") or ""),
                "status": str(task_state.get("status") or ""),
                "priority": str(task_state.get("priority") or ""),
                "instruction_text": str(task_state.get("instruction_text") or ""),
                "latest_progress_summary": str(task_state.get("latest_progress_summary") or ""),
                "pending_questions": list(task_state.get("pending_questions") or []),
                "result_summary": str(task_state.get("result_summary") or ""),
                "created_at": str(task_state.get("created_at") or ""),
                "updated_at": str(task_state.get("updated_at") or ""),
                "plan_content": read_plan_file(task_history_path),
            },
        }

    def get_task_messages(self, user_id: str, session_name: str, task_id: str) -> Dict[str, Any]:
        session_path = self._resolve_session_path(user_id, session_name, update_current=False)
        clean_task_id = str(task_id or "").strip()
        if not clean_task_id:
            raise ValueError("task_id_required")
        session_id = self.bot.session_manager._session_id_from_path(session_path)
        store, _scheduler = self._build_task_runtime_controller()
        task_state = store.read_task_state(session_id, clean_task_id)
        task_history_path = self.bot.workspace_layout.task_session_history_path(session_id, clean_task_id)
        raw_messages = replay_render_rows(task_history_path)
        return {
            "user_id": str(user_id or "").strip() or self.web_user_id,
            "session_name": self.bot.session_manager.get_display_name(session_path),
            "session_id": session_id,
            "task": {
                "task_id": clean_task_id,
                "title": str(task_state.get("title") or ""),
                "status": str(task_state.get("status") or ""),
            },
            "messages": raw_messages,
            "render_messages": self._normalize_messages_for_console(raw_messages),
        }

    # ---- Workspace prompt files ----

    def list_workspace_prompt_files(self) -> Dict[str, Any]:
        layout = self.bot.workspace_layout
        bundle = load_workspace_prompt_bundle(layout)
        files = []
        for name in ["SOUL.md", "IDENTITY.md", "USER.md", "AGENT.md", "MEMORY.md"]:
            path = str((Path(layout.prompt_root) / name).resolve())
            files.append(
                {
                    "name": name,
                    "path": path,
                    "editable": True,
                    "size": len(bundle.get(name, "")),
                }
            )
        return {"root": str(Path(layout.prompt_root).resolve()), "files": files}

    def get_workspace_prompt_file(self, name: str) -> Dict[str, Any]:
        path = self._workspace_prompt_path(name)
        return {
            "name": os.path.basename(path),
            "path": path,
            "content": Path(path).read_text(encoding="utf-8"),
        }

    def save_workspace_prompt_file(self, name: str, content: str) -> Dict[str, Any]:
        path = self._workspace_prompt_path(name)
        text = str(content or "")
        if os.path.basename(path) == "SYSTEM_PROMPT.md":
            self._validate_system_prompt_template(text)
        Path(path).write_text(text, encoding="utf-8")
        return {
            "name": os.path.basename(path),
            "path": path,
            "saved": True,
            "size": len(text),
        }

    def list_workspace_files(self, query: str = "") -> Dict[str, Any]:
        root = Path(self.agent_root).resolve()
        tree = self._build_workspace_tree(root, root, self._normalize_workspace_query(query))
        return {"root": str(root), "tree": tree}

    def get_workspace_file(self, path: str) -> Dict[str, Any]:
        target = self._resolve_workspace_file_path(path)
        return {
            "path": str(target.relative_to(Path(self.agent_root).resolve()).as_posix()),
            "content": target.read_text(encoding="utf-8"),
            "kind": "markdown",
            "editable": True,
        }

    def save_workspace_file(self, path: str, content: str) -> Dict[str, Any]:
        target = self._resolve_workspace_file_path(path)
        text = str(content or "")
        target.write_text(text, encoding="utf-8")
        return {
            "path": str(target.relative_to(Path(self.agent_root).resolve()).as_posix()),
            "saved": True,
            "size": len(text),
        }

    def get_current_session_prompt(self, user_id: str = "web:local", session_name: str = "") -> Dict[str, Any]:
        path = self._resolve_session_path(user_id, session_name)
        prompt_event = SessionJsonlStore(path).read_last_event("session_prompt")
        payload = prompt_event.get("payload") if isinstance(prompt_event, dict) and isinstance(prompt_event.get("payload"), dict) else {}
        return {
            "user_id": user_id,
            "session_name": self.bot.session_manager.get_display_name(path),
            "session_id": self.bot.session_manager._session_id_from_path(path),
            "path": path,
            "system_prompt": str(payload.get("prompt_text") or ""),
            "system_prompt_updated_at": str((prompt_event or {}).get("ts") or ""),
            "system_prompt_source_hash": str(payload.get("source_hash") or ""),
        }

    def refresh_current_session_prompt(self, user_id: str = "web:local", session_name: str = "") -> Dict[str, Any]:
        path = self._resolve_session_path(user_id, session_name)
        raise ValueError("session_prompt_frozen")

    # ---- File ingestion ----

    def register_uploaded_file(self, user_id: str, path: str, name: str, size: int) -> Dict[str, Any]:
        external_uid = (user_id or "").strip() or self.web_user_id
        item = self.files.add_file(external_uid, path=path, name=name, size=size)
        return {
            "user_id": external_uid,
            "path": item.path,
            "name": item.name,
            "size": item.size,
            "ts": item.ts,
        }

    # ---- Chat stream lifecycle ----

    def start_chat_stream(self, req: Any, loop: asyncio.AbstractEventLoop):
        request_id = (getattr(req, "request_id", "") or "").strip() or str(uuid.uuid4())
        queue = self.bus.create_stream(request_id, loop)
        cancel_event = threading.Event()

        with self._lock:
            self._cancel_flags[request_id] = cancel_event
            self._request_user[request_id] = self._normalize_user_id(getattr(req, "user_id", ""))

        t = threading.Thread(
            target=self._run_chat_task,
            args=(request_id, req, cancel_event),
            daemon=True,
            name=f"angel-chat-{request_id[:8]}",
        )
        t.start()
        return request_id, queue

    def cancel_request(self, request_id: str) -> bool:
        rid = (request_id or "").strip()
        with self._lock:
            flag = self._cancel_flags.get(rid)
            user_id = self._request_user.get(rid)
        if not flag:
            return False
        flag.set()
        if user_id:
            self.bot.cancel_pending_human(user_id)
        self.bus.emit(rid, "status", {"state": "cancel_requested"})
        return True

    def provide_human_input(self, user_id: str, content: str) -> bool:
        uid = self._normalize_user_id(user_id)
        ok = self.bot.provide_human_input(uid, content)
        if ok:
            # Notify all active streams for the same user.
            with self._lock:
                targets = [rid for rid, r_uid in self._request_user.items() if r_uid == uid]
            for rid in targets:
                self.bus.emit(rid, "status", {"state": "running", "phase": "human_input_received"})
        return ok

    def cancel_pending_human_input(self, user_id: str) -> None:
        """Cancel pending ask-human state for one user."""
        uid = self._normalize_user_id(user_id)
        self.bot.cancel_pending_human(uid)

    def cleanup_request(self, request_id: str) -> None:
        rid = (request_id or "").strip()
        with self._lock:
            self._cancel_flags.pop(rid, None)
            self._request_user.pop(rid, None)

    def _workspace_prompt_path(self, name: str) -> str:
        allowed = {"SOUL.md", "IDENTITY.md", "USER.md", "AGENT.md", "MEMORY.md"}
        clean = str(name or "").strip()
        if clean not in allowed:
            raise ValueError(f"unsupported prompt file: {clean}")
        return str((Path(self.bot.workspace_layout.prompt_root) / clean).resolve())

    def _resolve_workspace_file_path(self, relative_path: str) -> Path:
        root = Path(self.agent_root).resolve()
        clean = str(relative_path or "").strip().replace("\\", "/").lstrip("/")
        if not clean:
            raise ValueError("path_required")
        target = (root / clean).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError("path_outside_workspace_root") from exc
        if not target.is_file():
            raise ValueError("file_not_found")
        if target.suffix.lower() != ".md":
            raise ValueError("markdown_only")
        return target

    def _normalize_workspace_query(self, query: str) -> str:
        return str(query or "").strip().lower()

    def _build_workspace_tree(self, path: Path, root: Path, query: str) -> Dict[str, Any] | None:
        if path.name in {".git", ".venv", ".venv copy", "__pycache__", ".pytest_cache", "node_modules"}:
            return None
        if path.is_dir():
            children = []
            try:
                entries = sorted(path.iterdir(), key=lambda item: (item.is_dir(), item.name.lower()))
            except Exception:
                return None
            for child in entries:
                node = self._build_workspace_tree(child, root, query)
                if node is not None:
                    children.append(node)
            if path != root and not children:
                return None
            relative = "" if path == root else path.relative_to(root).as_posix()
            if query:
                name_match = query in path.name.lower() or query in relative.lower()
                if not name_match and not children:
                    return None
            return {
                "type": "dir",
                "name": path.name if path != root else "workspace",
                "path": relative,
                "children": children,
            }
        relative = path.relative_to(root).as_posix()
        if query and query not in path.name.lower() and query not in relative.lower():
            return None
        return {
            "type": "file",
            "name": path.name,
            "path": relative,
            "size": path.stat().st_size,
            "ext": path.suffix.lower(),
            "openable": path.suffix.lower() == ".md",
        }

    def _validate_system_prompt_template(self, content: str) -> None:
        dummy_fields = {
            "highest_priority_runtime_constraints": "runtime constraints",
            "soul_content": "soul",
            "identity_content": "identity",
            "user_content": "user",
            "agent_content": "agent",
            "memory_content": "memory",
            "workspace_runtime": "workspace",
            "skills_runtime": "skills",
        }
        render_system_prompt(str(content or ""), dummy_fields)

    def _resolve_session_path(self, user_id: str, session_name: str, *, update_current: bool = True) -> str:
        external_uid = (user_id or "").strip() or self.web_user_id
        if session_name:
            target = self.indexer.find_session_path(external_uid, session_name)
            if not target:
                raise ValueError("session_not_found")
            if update_current:
                self.bot.session_manager.set_current_session(external_uid, target)
            return target
        return self.bot.session_manager.get_or_create_session_path(external_uid)

    def _load_session_payload(self, path: str) -> Dict[str, Any]:
        return {}

    def run_background_prompt(self, user_id: str, session_name: str, content: str, source: str = "system") -> str:
        uid = self._normalize_user_id(user_id)
        text = str(content or "").strip()
        if not text:
            return ""
        session_path = self._resolve_session_path(uid, session_name)
        try:
            self._enqueue_completed_subagent_results(session_path)
            self._deliver_pending_task_messages(session_path)
        except Exception:
            pass

        with self._run_lock:
            reply = self.bot.run_task(uid, text, cancel_checker=lambda: False)
        try:
            self._maybe_pump_task_scheduler(session_path)
        except Exception:
            pass
        return str(reply or "")

    def _build_task_runtime_controller(self):
        store = TaskRuntimeStore(self.bot.workspace_layout)
        scheduler = TaskScheduler(self.bot.workspace_layout, store)
        return store, scheduler

    def _deliver_pending_task_messages(self, session_path: str, emit: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> int:
        session_id = Path(session_path).parent.name
        store, _scheduler = self._build_task_runtime_controller()
        rows = store.read_pending_messages(session_id)
        if not rows:
            return 0
        history_store = SessionJsonlStore(session_path)
        delivered = 0
        for item in rows:
            if str(item.get("delivered_at") or "").strip():
                continue
            kind = str(item.get("kind") or "").strip()
            content = str(item.get("content") or "").strip()
            task_id = str(item.get("task_id") or "").strip()
            if kind == "task_waiting_human":
                payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
                task_title = str(payload.get("task_title") or "").strip()
                rendered_content = (
                    "[system message]\n"
                    "后台执行上下文需要信息才能继续。\n\n"
                    "任务：\n"
                    f"task_id={task_id}\n"
                    f"title={task_title}\n\n"
                    "问题：\n"
                    f"{content}\n\n"
                    "这是内部执行问题，不是用户直接提出的新需求。请先判断你能否基于当前会话上下文回答。\n"
                    "如果你能回答，请调用 task_update，把答案写回对应任务。\n"
                    "如果你不能回答，请调用 ask_human，向真实用户自然确认必要信息。\n"
                    "面向用户时不要提 task session、task id 或其他内部实现细节；把这项工作作为你自己的进行中工作来表达。"
                )
                history_store.append_event(
                    build_message_event(
                        message_id=history_store.next_message_id(),
                        role="user",
                        author="runtime",
                        content=rendered_content,
                        user_turn_meta={
                            "source": "runtime",
                            "preferred_response_language": "zh",
                            "request_kind": "system_message",
                            "message_time": datetime.now().astimezone().isoformat(timespec="seconds"),
                            "attachments": [],
                        },
                    )
                )
                if store.mark_pending_message_delivered(session_id, str(item.get("message_id") or "")):
                    delivered += 1
                continue
            if kind == "task_result":
                label = "[Task Result]"
                author = "task_session"
                origin = "task_session"
            else:
                label = "[Subagent Result]"
                author = "subagent"
                origin = "subagent"
            identifier = task_id or str((item.get("payload") or {}).get("subagent_id") or "").strip()
            rendered_content = content if not label else f"{label} {identifier}: {content}"
            history_store.append_event(
                build_message_event(
                    message_id=history_store.next_message_id(),
                    role="system",
                    author=author,
                    content=rendered_content,
                    extras={
                        "message_origin": origin,
                        "message_kind": kind,
                        "task_ref": (
                            {
                                "task_id": task_id,
                                "task_title": str((item.get("payload") or {}).get("task_title") or ""),
                                "status": str((item.get("payload") or {}).get("status") or ""),
                                "delivery_mode": "deferred_push",
                            }
                            if task_id
                            else {}
                        ),
                        "subagent_ref": dict(item.get("payload") or {}) if kind == "subagent_result" else {},
                    },
                )
            )
            if store.mark_pending_message_delivered(session_id, str(item.get("message_id") or "")):
                delivered += 1
                if emit and kind == "subagent_result":
                    payload = dict(item.get("payload") or {})
                    payload["summary"] = content
                    emit("subagent_result_received", payload)
        return delivered

    def _enqueue_completed_subagent_results(self, session_path: str) -> int:
        session_id = Path(session_path).parent.name
        subagent_tool = self._find_subagent_tool()
        if subagent_tool is None:
            return 0
        store, _scheduler = self._build_task_runtime_controller()
        appended = 0
        for record in subagent_tool.registry.list_by_parent(session_id):
            status = str(record.get("status") or "").strip()
            if status not in {"completed", "failed", "cancelled"}:
                continue
            if bool(record.get("parent_delivery_enqueued")):
                continue
            subagent_id = str(record.get("subagent_id") or "").strip()
            if not subagent_id:
                continue
            result = dict(record.get("result") or {})
            summary = str(record.get("summary") or result.get("summary") or record.get("error") or "").strip()
            if not summary:
                summary = f"Subagent {status}."
            store.append_pending_message(
                session_id,
                {
                    "message_id": f"{subagent_id}:subagent_result",
                    "origin": "subagent",
                    "task_id": "",
                    "kind": "subagent_result",
                    "content": summary,
                    "payload": {
                        "subagent_id": subagent_id,
                        "status": status,
                        "worker_kind": str(record.get("worker_kind") or ""),
                        "result": result,
                        "error": str(record.get("error") or ""),
                    },
                    "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                },
            )
            subagent_tool.registry.mark_parent_delivery_enqueued(subagent_id)
            appended += 1
        return appended

    def _maybe_pump_task_scheduler(self, session_path: str) -> int:
        session_id = Path(session_path).parent.name
        _store, scheduler = self._build_task_runtime_controller()
        return len(
            scheduler.pump_once(
                session_id,
                task_executor=lambda task_session_path, task_id: self.bot.run_task_in_task_session(
                    task_session_path,
                    task_id=task_id,
                    cancel_checker=lambda: False,
                ),
            )
        )

    def _find_current_session_path(self, user_id: str = "") -> str:
        external_uid = (user_id or "").strip() or self.web_user_id
        return self.bot.session_manager.get_current_session_path(external_uid)

    def _find_subagent_tool(self):
        for tool in list(getattr(self.bot, "tools", []) or []):
            if isinstance(tool, SubAgentTool):
                return tool
        for tool in list(getattr(self.bot, "_mcp_tools", []) or []):
            if isinstance(tool, SubAgentTool):
                return tool
        for tool in list(getattr(self.bot, "_direct_tools", []) or []):
            if isinstance(tool, SubAgentTool):
                return tool
        return None

    # ---- Internal helpers ----

    def execute_chat_request(
        self,
        *,
        request_id: str,
        req: Any,
        cancel_event: threading.Event,
        emit,
    ) -> None:
        """Execute one chat request and emit lifecycle events through the callback."""
        external_user_id = (getattr(req, "user_id", "") or "").strip() or self.web_user_id
        user_id = self._normalize_user_id(external_user_id)
        session_name = str(getattr(req, "session_name", "") or "").strip()
        content = str(getattr(req, "content", "") or "").strip()
        source = str(getattr(req, "source", "web") or "web")
        inject_uploaded_files = bool(getattr(req, "inject_uploaded_files", True))
        reply_language = self._resolve_reply_language(getattr(req, "reply_language", ""))

        if not content:
            emit("status", {"state": "failed", "reason": "empty_content"})
            emit("run_done", {"success": False, "error": "empty_content"})
            return

        try:
            session_path = self._resolve_session_path(external_user_id, session_name)
            session_name = self.bot.session_manager.get_display_name(session_path)
        except ValueError as exc:
            detail = str(exc) or "session_not_found"
            emit("status", {"state": "failed", "phase": "error", "error": detail})
            emit(
                "run_done",
                {
                    "success": False,
                    "error": detail,
                    "request_id": request_id,
                    "user_id": external_user_id,
                    "session_name": session_name,
                },
            )
            return
        except Exception:
            session_name = session_name or ""
            session_path = ""

        if session_path:
            try:
                self._enqueue_completed_subagent_results(session_path)
                self._deliver_pending_task_messages(session_path, emit=emit)
            except Exception:
                pass

        channel_prefix = self._detect_channel_prefix(external_user_id)
        realtime_stream = self._is_realtime_stream(source=source, channel_prefix=channel_prefix)

        emit(
            "run_started",
            {
                "request_id": request_id,
                "user_id": external_user_id,
                "session_id": self.bot.session_manager._session_id_from_path(session_path),
                "session_name": session_name,
                "channel_prefix": channel_prefix,
                "source": source,
            },
        )
        emit("status", {"state": "running", "phase": "boot"})

        attachments = self.files.to_attachment_descriptors(user_id) if inject_uploaded_files else []
        for item in attachments:
            raw_path = str(item.get("local_path") or "")
            if not raw_path:
                continue
            try:
                item["local_path"] = str(
                    Path(raw_path).resolve().relative_to(Path(self.agent_root).resolve()).as_posix()
                )
            except Exception:
                item["local_path"] = Path(raw_path).name

        hooks = build_react_hooks(emit)
        original_hooks = self.bot.get_react_hooks()

        def ask_handler(uid: str, question: str) -> None:
            emit(
                "ask_human",
                {
                    "user_id": uid,
                    "question": question,
                },
            )
            emit("status", {"state": "waiting", "phase": "ask_human"})

        self.bot.set_ask_handler(user_id, ask_handler)
        self.bot.set_react_hooks(hooks)

        reply_text = ""
        failed = False
        error_message = ""
        reasoning_streamed = False

        def _cancel_checker() -> bool:
            return cancel_event.is_set()

        def _on_token(delta: str) -> None:
            if not realtime_stream:
                return
            text = str(delta or "")
            if text:
                emit("assistant_delta", {"delta": text})

        def _on_reasoning(delta: str) -> None:
            nonlocal reasoning_streamed
            if not realtime_stream:
                return
            text = str(delta or "")
            if not text:
                return
            reasoning_streamed = True
            emit(
                "assistant_thinking_delta",
                {
                    "content": text,
                    "reasoning_type": "general",
                },
            )

        try:
            with self._run_lock:
                reply = self.bot.run_task(
                    user_id,
                    content,
                    cancel_checker=_cancel_checker,
                    stream=realtime_stream,
                    on_token=_on_token,
                    on_reasoning=_on_reasoning,
                    user_turn_meta={
                        "source": source or "web",
                        "preferred_response_language": reply_language,
                        "request_kind": "user_message",
                        "message_time": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "attachments": attachments,
                    },
                )
            reply_text = str(reply or "")
            if cancel_event.is_set() and not reply_text:
                emit("status", {"state": "cancelled", "phase": "stopped"})
            else:
                emit("status", {"state": "running", "phase": "streaming_reply"})
                if reasoning_streamed:
                    emit(
                        "assistant_thinking_done",
                        {"reasoning_type": "general", "keep": False},
                    )
                if not realtime_stream:
                    for chunk in self._split_chunks(reply_text, size=120):
                        emit("assistant_delta", {"delta": chunk})
                        time.sleep(0.005)
                emit("status", {"state": "completed", "phase": "done"})
        except Exception as exc:
            failed = True
            error_message = str(exc)
            emit("status", {"state": "failed", "phase": "error", "error": error_message})
        finally:
            self.bot.clear_ask_handler(user_id)
            self.bot.set_react_hooks(original_hooks)
            if session_path:
                try:
                    self._maybe_pump_task_scheduler(session_path)
                    self._enqueue_completed_subagent_results(session_path)
                    self._deliver_pending_task_messages(session_path, emit=emit)
                except Exception:
                    pass

            if failed:
                emit(
                    "run_done",
                    {
                        "success": False,
                        "error": error_message,
                        "request_id": request_id,
                    },
                )
            else:
                emit(
                    "run_done",
                    {
                        "success": True,
                        "request_id": request_id,
                        "user_id": external_user_id,
                        "session_id": self.bot.session_manager._session_id_from_path(session_path) if session_path else "",
                        "session_name": session_name,
                        "final_text": reply_text,
                    },
                )

    def _run_chat_task(self, request_id: str, req: Any, cancel_event: threading.Event) -> None:
        def _emit(event_type: str, payload: Dict[str, Any]) -> None:
            self.bus.emit(request_id, event_type, payload)
        try:
            self.execute_chat_request(
                request_id=request_id,
                req=req,
                cancel_event=cancel_event,
                emit=_emit,
            )
        finally:
            self.bus.close_stream(request_id)
            self.cleanup_request(request_id)

    def _normalize_user_id(self, user_id: str) -> str:
        uid = (user_id or "").strip()
        if not uid:
            uid = self.web_user_id
        return uid

    def _split_chunks(self, text: str, size: int = 120):
        if not text:
            return []
        chunks = []
        idx = 0
        while idx < len(text):
            chunks.append(text[idx : idx + size])
            idx += size
        return chunks

    def _is_realtime_stream(self, source: str, channel_prefix: str) -> bool:
        source_key = str(source or "").strip().lower()
        prefix_key = str(channel_prefix or "").strip().lower()
        return source_key in {"web", "cli"} or prefix_key in {"web", "cli"}

    def _detect_channel_prefix(self, user_id: str) -> str:
        text = (user_id or "").strip()
        if ":" in text:
            return text.split(":", 1)[0] or "unknown"
        if text == "debug_user":
            return "cli"
        return "unknown"

    def _make_console_text_row(
        self,
        role: str,
        content: Any,
        streaming: bool = False,
        ts: Any = "",
        attachments: Any = None,
        thinking: Any = "",
        reasoning_type: str = "general",
    ) -> Optional[Dict[str, Any]]:
        text = str(content or "")
        if not text.strip() or self._should_hide_console_message(text):
            return None
        normalized_role = str(role or "").strip().lower() or "assistant"
        if normalized_role == "tool":
            normalized_role = "system"
        return {
            "role": normalized_role,
            "kind": "text",
            "content": text,
            "streaming": bool(streaming),
            "ts": str(ts or ""),
            "attachments": list(attachments or []),
            "thinking": self._normalize_console_thinking(thinking, reasoning_type),
        }

    def _normalize_console_thinking(self, content: Any, reasoning_type: str = "general") -> Any:
        text = str(content or "").strip()
        if not text:
            return ""
        return {
            "content": text,
            "reasoning_type": str(reasoning_type or "general"),
        }

    def _make_console_tool_card_row(
        self,
        tool_name: Any = "tool",
        tool_call_id: Any = "",
        input_text: Any = "",
        output_text: Any = "",
        streaming: bool = False,
        thinking: Any = "",
        reasoning_type: str = "tool",
    ) -> Dict[str, Any]:
        return {
            "role": "system",
            "kind": "tool_card",
            "tool_name": str(tool_name or "tool"),
            "tool_call_id": str(tool_call_id or ""),
            "input_text": self._normalize_tool_payload(input_text),
            "output_text": self._normalize_tool_payload(output_text),
            "streaming": bool(streaming),
            "thinking": self._normalize_console_thinking(thinking, reasoning_type),
        }

    def _make_console_event_card_row(
        self,
        *,
        event_source: str,
        event_kind: str,
        title: str,
        content: str,
        ts: Any = "",
        task_ref: Any = None,
        subagent_ref: Any = None,
    ) -> Dict[str, Any]:
        return {
            "role": "system",
            "kind": "event_card",
            "event_source": str(event_source or ""),
            "event_kind": str(event_kind or ""),
            "title": str(title or ""),
            "content": str(content or ""),
            "ts": str(ts or ""),
            "task_ref": dict(task_ref or {}) if isinstance(task_ref, dict) else {},
            "subagent_ref": dict(subagent_ref or {}) if isinstance(subagent_ref, dict) else {},
        }

    def _strip_event_prefix(self, content: Any, *, label: str = "", identifier: str = "") -> str:
        text = str(content or "").strip()
        if not text:
            return ""
        clean_label = str(label or "").strip()
        clean_identifier = str(identifier or "").strip()
        prefixes = []
        if clean_label and clean_identifier:
            prefixes.append(f"{clean_label} {clean_identifier}:")
        if clean_label:
            prefixes.append(f"{clean_label}:")
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix) :].strip()
        return text

    def _normalize_event_card_title_and_content(
        self,
        *,
        event_source: str,
        event_kind: str,
        content: Any,
        task_ref: Any = None,
        subagent_ref: Any = None,
    ) -> Tuple[str, str]:
        task_id = str((task_ref or {}).get("task_id") or "").strip() if isinstance(task_ref, dict) else ""
        subagent_id = str((subagent_ref or {}).get("subagent_id") or "").strip() if isinstance(subagent_ref, dict) else ""
        title_map = {
            ("task_session", "task_result"): "任务结果",
            ("task_session", "task_result_received"): "任务结果",
            ("task_session", "task_waiting_human"): "任务需要你的输入",
            ("subagent", "subagent_result"): "Subagent 结果",
            ("subagent", "subagent_result_received"): "Subagent 结果",
        }
        label_map = {
            ("task_session", "task_result"): "[Task Result]",
            ("task_session", "task_result_received"): "[Task Result]",
            ("task_session", "task_waiting_human"): "[Task Waiting Human]",
            ("subagent", "subagent_result"): "[Subagent Result]",
            ("subagent", "subagent_result_received"): "[Subagent Result]",
        }
        title = title_map.get((event_source, event_kind), "运行时事件")
        normalized_content = self._strip_event_prefix(
            content,
            label=label_map.get((event_source, event_kind), ""),
            identifier=task_id or subagent_id,
        )
        return title, normalized_content

    def _canonical_console_event_kind(self, event_source: str, event_kind: str) -> str:
        source = str(event_source or "").strip()
        kind = str(event_kind or "").strip()
        canonical_map = {
            ("task_session", "task_result"): "task_result_received",
            ("subagent", "subagent_result"): "subagent_result_received",
        }
        return canonical_map.get((source, kind), kind)

    def _append_console_row(
        self,
        rows: List[Dict[str, Any]],
        row: Optional[Dict[str, Any]],
        pending_by_call_id: Dict[str, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        rows.append(row)
        if row.get("kind") == "tool_card" and row.get("tool_call_id"):
            pending_by_call_id[str(row["tool_call_id"])] = row
        return row

    def _normalize_console_render_row(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        kind = str(msg.get("kind", "") or "").strip().lower()
        if not kind:
            return None
        if kind == "text":
            return self._make_console_text_row(
                msg.get("role", "assistant"),
                msg.get("content", ""),
                bool(msg.get("streaming", False)),
                msg.get("ts", ""),
                msg.get("attachments", []),
                msg.get("thinking", ""),
                str(msg.get("reasoning_type") or "general"),
            )
        if kind == "thinking":
            return None
        if kind == "tool_card":
            return self._make_console_tool_card_row(
                tool_name=msg.get("tool_name") or msg.get("name") or "tool",
                tool_call_id=msg.get("tool_call_id") or msg.get("toolCallId") or "",
                input_text=msg.get("input_text") or msg.get("input") or "",
                output_text=msg.get("output_text") or msg.get("output") or msg.get("result") or "",
                streaming=bool(msg.get("streaming", False)),
                thinking=msg.get("thinking", ""),
                reasoning_type=str(msg.get("reasoning_type") or "tool"),
            )
        if kind == "event_card":
            return self._make_console_event_card_row(
                event_source=msg.get("event_source") or "",
                event_kind=msg.get("event_kind") or "",
                title=msg.get("title") or "",
                content=msg.get("content") or "",
                ts=msg.get("ts") or "",
                task_ref=msg.get("task_ref") or {},
                subagent_ref=msg.get("subagent_ref") or {},
            )
        return None

    def _normalize_task_or_subagent_event_row(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if str(msg.get("role", "")).strip().lower() != "system":
            return None
        event_source = str(msg.get("message_origin") or "").strip()
        raw_event_kind = str(msg.get("message_kind") or "").strip()
        event_kind = self._canonical_console_event_kind(event_source, raw_event_kind)
        if event_source not in {"task_session", "subagent"}:
            return None
        title, content = self._normalize_event_card_title_and_content(
            event_source=event_source,
            event_kind=raw_event_kind,
            content=msg.get("content") or "",
            task_ref=msg.get("task_ref") or {},
            subagent_ref=msg.get("subagent_ref") or {},
        )
        return self._make_console_event_card_row(
            event_source=event_source,
            event_kind=event_kind,
            title=title,
            content=content,
            ts=msg.get("ts") or "",
            task_ref=msg.get("task_ref") or {},
            subagent_ref=msg.get("subagent_ref") or {},
        )

    def _normalize_messages_for_console(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = messages if isinstance(messages, list) else []
        normalized: List[Dict[str, Any]] = []
        pending_by_call_id: Dict[str, Dict[str, Any]] = {}

        for msg in rows:
            if not isinstance(msg, dict):
                continue
            kind = str(msg.get("kind", "") or "").strip().lower()
            if kind == "thinking":
                continue

            render_row = self._normalize_console_render_row(msg)
            if render_row is not None:
                self._append_console_row(normalized, render_row, pending_by_call_id)
                continue

            event_row = self._normalize_task_or_subagent_event_row(msg)
            if event_row is not None:
                self._append_console_row(normalized, event_row, pending_by_call_id)
                continue

            role = str(msg.get("role", "")).strip().lower()
            if role == "assistant":
                calls = self._parse_tool_calls(msg.get("tool_calls") or msg.get("toolCalls") or msg.get("toolcalls"))
                self._append_console_row(
                    normalized,
                    self._make_console_text_row("assistant", msg.get("content", ""), False, msg.get("ts", "")),
                    pending_by_call_id,
                )

                tool_thinking = str(msg.get("reasoning_content", "") or "").strip()
                attached_tool_thinking = False
                for call in calls:
                    fn = {}
                    if isinstance(call.get("function"), dict):
                        fn = call.get("function") or {}
                    elif isinstance(call.get("func"), dict):
                        fn = call.get("func") or {}

                    card = self._make_console_tool_card_row(
                        tool_name=fn.get("name") or call.get("name") or call.get("tool_name") or "tool",
                        tool_call_id=call.get("id") or call.get("tool_call_id") or call.get("toolCallId") or "",
                        input_text=fn.get("arguments") if isinstance(fn, dict) else "",
                        output_text="",
                        streaming=False,
                        thinking=tool_thinking if not attached_tool_thinking else "",
                        reasoning_type="tool",
                    )
                    self._append_console_row(normalized, card, pending_by_call_id)
                    if tool_thinking and not attached_tool_thinking:
                        attached_tool_thinking = True
                continue

            is_tool_like = role == "tool" or bool(msg.get("tool_call_id") or msg.get("toolCallId"))
            if is_tool_like:
                call_id = str(msg.get("tool_call_id") or msg.get("toolCallId") or "")
                tool_name = str(msg.get("name") or msg.get("tool_name") or "tool")
                output = self._normalize_tool_payload(msg.get("content") or msg.get("result") or msg.get("output") or "")

                if call_id and call_id in pending_by_call_id:
                    pending = pending_by_call_id[call_id]
                    pending["output_text"] = output
                    if not pending.get("tool_name") or pending.get("tool_name") == "tool":
                        pending["tool_name"] = tool_name
                else:
                    self._append_console_row(
                        normalized,
                        self._make_console_tool_card_row(
                            tool_name=tool_name,
                            tool_call_id=call_id,
                            input_text="",
                            output_text=output,
                            streaming=False,
                        ),
                        pending_by_call_id,
                    )
                continue

            if role in {"user", "system"}:
                self._append_console_row(
                    normalized,
                    self._make_console_text_row(
                        role,
                        msg.get("content", ""),
                        False,
                        msg.get("ts", ""),
                        (msg.get("user_turn_meta") or {}).get("attachments", []) if role == "user" else [],
                    ),
                    pending_by_call_id,
                )

        return normalized

    def _should_hide_console_message(self, content: Any) -> bool:
        text = str(content or "")
        if not text.strip():
            return False
        lowered = text.lstrip().lower()
        return any(lowered.startswith(prefix) for prefix in self._CONSOLE_HIDDEN_PREFIXES)

    def _parse_tool_calls(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            return [value]
        if isinstance(value, str):
            parsed = self._safe_json_loads(value)
            if isinstance(parsed, list):
                return [row for row in parsed if isinstance(row, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        return []

    def _normalize_tool_payload(self, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""

        parsed = self._safe_json_loads(text)
        if isinstance(parsed, str):
            nested = self._safe_json_loads(parsed)
            parsed = nested if nested is not None else parsed

        if parsed is None:
            return text
        if isinstance(parsed, str):
            return parsed
        try:
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            return text

    def _safe_json_loads(self, value: str) -> Optional[Any]:
        try:
            return json.loads(value)
        except Exception:
            return None
