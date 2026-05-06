# -*- coding: utf-8 -*-
"""Gateway service that fronts BotRuntime chat execution."""

from __future__ import annotations

import asyncio
import queue
import threading
import uuid
from typing import Any

from .bus import GatewayEventBus
from .registry import GatewayRunRegistry


class GatewayService:
    """Minimal control-plane facade for chat streaming."""

    def __init__(self, runtime: Any):
        self.runtime = runtime
        self.bus = GatewayEventBus()
        self.registry = GatewayRunRegistry()
        self._lock = threading.Lock()
        self._cancel_flags: dict[str, threading.Event] = {}
        self._request_user: dict[str, str] = {}
        self._bridge_outbound: "queue.Queue[dict]" = queue.Queue()

    def start_chat_stream(self, req: Any, loop: asyncio.AbstractEventLoop):
        request_id = (getattr(req, "request_id", "") or "").strip() or str(uuid.uuid4())
        external_user_id = (getattr(req, "user_id", "") or "").strip() or self.runtime.web_user_id
        queue = self.bus.create_stream(request_id, loop)
        cancel_event = threading.Event()

        with self._lock:
            self._cancel_flags[request_id] = cancel_event
            self._request_user[request_id] = external_user_id
        self.registry.create(request_id=request_id, user_id=external_user_id)

        thread = threading.Thread(
            target=self._run_chat_task,
            args=(request_id, req, cancel_event),
            daemon=True,
            name=f"gateway-chat-{request_id[:8]}",
        )
        thread.start()
        return request_id, queue

    def cancel_request(self, request_id: str) -> bool:
        rid = str(request_id or "").strip()
        with self._lock:
            flag = self._cancel_flags.get(rid)
            user_id = self._request_user.get(rid)
        if flag is None:
            return False
        flag.set()
        if user_id:
            self.runtime.cancel_pending_human_input(user_id)
        self.registry.update(rid, status="cancel_requested", phase="stopping")
        self.bus.emit(rid, "status", {"state": "cancel_requested"})
        return True

    def provide_human_input(self, user_id: str, content: str) -> bool:
        external_user_id = str(user_id or "").strip() or self.runtime.web_user_id
        ok = self.runtime.provide_human_input(external_user_id, content)
        if ok:
            for record in self.registry.find_by_user(external_user_id):
                self.bus.emit(
                    record.request_id,
                    "status",
                    {"state": "running", "phase": "human_input_received"},
                )
                self.registry.update(
                    record.request_id,
                    status="running",
                    phase="human_input_received",
                )
        return ok

    def dispatch_background_prompt(
        self,
        *,
        user_id: str,
        session_name: str,
        content: str,
        source: str = "system",
        wait: bool = True,
        timeout: float | None = None,
    ) -> dict:
        """Run a non-interactive prompt through the same gateway control plane."""
        external_user_id = str(user_id or "").strip() or self.runtime.web_user_id
        normalized_content = str(content or "").strip()
        normalized_source = str(source or "system").strip() or "system"
        request_id = str(uuid.uuid4())
        runtime_req = type(
            "BackgroundGatewayRequest",
            (),
            {
                "request_id": request_id,
                "user_id": external_user_id,
                "session_name": str(session_name or "").strip(),
                "content": normalized_content,
                "continue_mode": "in_place",
                "source": normalized_source,
                "inject_uploaded_files": False,
            },
        )()
        cancel_event = threading.Event()
        result: dict[str, Any] = {
            "accepted": True,
            "request_id": request_id,
            "user_id": external_user_id,
            "session_name": str(session_name or "").strip(),
            "source": normalized_source,
            "success": False,
            "final_text": "",
            "error": "",
        }
        completion = threading.Event()

        with self._lock:
            self._cancel_flags[request_id] = cancel_event
            self._request_user[request_id] = external_user_id
        self.registry.create(request_id=request_id, user_id=external_user_id)

        thread = threading.Thread(
            target=self._run_background_task,
            args=(request_id, runtime_req, cancel_event, result, completion),
            daemon=True,
            name=f"gateway-background-{request_id[:8]}",
        )
        thread.start()

        if not wait:
            result["status"] = "started"
            return result

        completion.wait(timeout=timeout)
        if not completion.is_set():
            result["status"] = "running"
            return result
        result["status"] = "completed" if result.get("success") else "failed"
        return result

    def cleanup_request(self, request_id: str) -> None:
        rid = str(request_id or "").strip()
        with self._lock:
            self._cancel_flags.pop(rid, None)
            self._request_user.pop(rid, None)
        self.registry.remove(rid)

    def ingest_bridge_inbound(self, payload: dict) -> dict:
        """Accept one inbound payload from the TS channel service."""
        normalized = dict(payload or {})
        inbound_type = str(normalized.get("type") or "").strip()
        if inbound_type != "inbound_message":
            return {
                "accepted": False,
                "error": "unsupported_inbound_type",
                "kind": inbound_type or "unknown",
            }

        channel = str(normalized.get("channel") or "").strip() or "unknown"
        account_id = str(normalized.get("account_id") or "").strip() or "default"
        sender = normalized.get("sender") if isinstance(normalized.get("sender"), dict) else {}
        sender_user_id = str(sender.get("user_id") or "").strip() or "unknown"
        message = normalized.get("message") if isinstance(normalized.get("message"), dict) else {}
        message_id = str(message.get("message_id") or "").strip() or str(uuid.uuid4())
        content = str(message.get("text") or "").strip()
        request_id = str(normalized.get("request_id") or "").strip() or f"bridge_{message_id}"
        external_user_id = f"{channel}:{sender_user_id}"

        if not content:
            return {
                "accepted": False,
                "error": "empty_content",
                "kind": inbound_type,
                "request_id": request_id,
            }

        runtime_req = type(
            "BridgeGatewayRequest",
            (),
            {
                "request_id": request_id,
                "user_id": external_user_id,
                "session_name": "",
                "content": content,
                "continue_mode": "in_place",
                "source": channel,
                "inject_uploaded_files": False,
            },
        )()

        cancel_event = threading.Event()
        with self._lock:
            self._cancel_flags[request_id] = cancel_event
            self._request_user[request_id] = external_user_id
        self.registry.create(request_id=request_id, user_id=external_user_id)

        thread = threading.Thread(
            target=self._run_bridge_task,
            args=(request_id, runtime_req, cancel_event, normalized, channel, account_id, sender_user_id),
            daemon=True,
            name=f"gateway-bridge-{request_id[:8]}",
        )
        thread.start()
        return {
            "accepted": True,
            "kind": inbound_type,
            "request_id": request_id,
            "channel": channel,
            "account_id": account_id,
        }

    def pull_bridge_outbound(self, channel: str = "", account_id: str = "") -> dict:
        normalized_channel = str(channel or "").strip()
        normalized_account_id = str(account_id or "").strip()
        buffered: list[dict] = []
        matched: dict | None = None

        while True:
            try:
                item = self._bridge_outbound.get_nowait()
            except queue.Empty:
                break
            item_channel = str(item.get("channel") or "").strip()
            item_account = str(item.get("account_id") or "").strip()
            channel_ok = not normalized_channel or item_channel == normalized_channel
            account_ok = not normalized_account_id or item_account == normalized_account_id
            if matched is None and channel_ok and account_ok:
                matched = item
                continue
            buffered.append(item)

        for item in buffered:
            self._bridge_outbound.put_nowait(item)

        if matched is None:
            return {"ok": True, "message": None}
        return {"ok": True, "message": matched}

    def _run_chat_task(self, request_id: str, req: Any, cancel_event: threading.Event) -> None:
        def emit(event_type: str, payload: dict) -> None:
            if event_type == "status":
                self.registry.update(
                    request_id,
                    status=str(payload.get("state") or "").strip() or None,
                    phase=str(payload.get("phase") or "").strip() or None,
                )
            elif event_type == "run_started":
                self.registry.update(
                    request_id,
                    status="running",
                    phase="boot",
                    session_name=str(payload.get("session_name") or "").strip(),
                )
            elif event_type == "run_done":
                success = bool(payload.get("success"))
                self.registry.update(
                    request_id,
                    status="completed" if success else "failed",
                    phase="done" if success else "error",
                    session_name=str(payload.get("session_name") or "").strip() or None,
                )
            self.bus.emit(request_id, event_type, payload)

        try:
            self.runtime.execute_chat_request(
                request_id=request_id,
                req=req,
                cancel_event=cancel_event,
                emit=emit,
            )
        finally:
            self.bus.close_stream(request_id)
            self.cleanup_request(request_id)

    def _run_background_task(
        self,
        request_id: str,
        req: Any,
        cancel_event: threading.Event,
        result: dict[str, Any],
        completion: threading.Event,
    ) -> None:
        def emit(event_type: str, payload: dict) -> None:
            if event_type == "status":
                self.registry.update(
                    request_id,
                    status=str(payload.get("state") or "").strip() or None,
                    phase=str(payload.get("phase") or "").strip() or None,
                )
            elif event_type == "run_started":
                session_name = str(payload.get("session_name") or "").strip()
                self.registry.update(
                    request_id,
                    status="running",
                    phase="boot",
                    session_name=session_name,
                )
                result["session_name"] = session_name or result.get("session_name", "")
            elif event_type == "run_done":
                success = bool(payload.get("success"))
                session_name = str(payload.get("session_name") or "").strip()
                self.registry.update(
                    request_id,
                    status="completed" if success else "failed",
                    phase="done" if success else "error",
                    session_name=session_name or None,
                )
                result["success"] = success
                result["final_text"] = str(payload.get("final_text") or "")
                result["error"] = str(payload.get("error") or "")
                if session_name:
                    result["session_name"] = session_name
            self.bus.emit(request_id, event_type, payload)

        try:
            self.runtime.execute_chat_request(
                request_id=request_id,
                req=req,
                cancel_event=cancel_event,
                emit=emit,
            )
        finally:
            completion.set()
            self.bus.close_stream(request_id)
            self.cleanup_request(request_id)

    def _run_bridge_task(
        self,
        request_id: str,
        req: Any,
        cancel_event: threading.Event,
        inbound_payload: dict,
        channel: str,
        account_id: str,
        sender_user_id: str,
    ) -> None:
        final_payload: dict[str, Any] = {}

        def emit(event_type: str, payload: dict) -> None:
            if event_type == "status":
                self.registry.update(
                    request_id,
                    status=str(payload.get("state") or "").strip() or None,
                    phase=str(payload.get("phase") or "").strip() or None,
                )
            elif event_type == "run_started":
                self.registry.update(
                    request_id,
                    status="running",
                    phase="boot",
                    session_name=str(payload.get("session_name") or "").strip(),
                )
            elif event_type == "run_done":
                final_payload.clear()
                final_payload.update(payload)
                success = bool(payload.get("success"))
                self.registry.update(
                    request_id,
                    status="completed" if success else "failed",
                    phase="done" if success else "error",
                    session_name=str(payload.get("session_name") or "").strip() or None,
                )

        try:
            self.runtime.execute_chat_request(
                request_id=request_id,
                req=req,
                cancel_event=cancel_event,
                emit=emit,
            )
            success = bool(final_payload.get("success"))
            text = str(final_payload.get("final_text") or "").strip()
            if success and text:
                self._bridge_outbound.put_nowait(
                    {
                        "type": "outbound_message",
                        "session_id": str(final_payload.get("session_id") or final_payload.get("session_name") or ""),
                        "session_name": str(final_payload.get("session_name") or ""),
                        "run_id": request_id,
                        "channel": channel,
                        "account_id": account_id,
                        "delivery": {
                            "account_id": account_id,
                            "to": sender_user_id,
                            "thread_id": (
                                inbound_payload.get("thread_id")
                                if isinstance(inbound_payload.get("thread_id"), (str, type(None)))
                                else None
                            ),
                        },
                        "message": {
                            "mode": "final",
                            "text": text,
                        },
                    }
                )
        finally:
            self.cleanup_request(request_id)
