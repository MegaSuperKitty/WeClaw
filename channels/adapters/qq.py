# -*- coding: utf-8 -*-
"""机器人入口：WeClaw。"""
import asyncio
from collections import deque
import json
import os
from pathlib import Path
import threading
import sys
import urllib.parse
import urllib.request
from typing import Dict, Optional

import botpy
from botpy.api import Route
from botpy import logging
from botpy.message import C2CMessage

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from channels.common import (
    AGENT_ID,
    AGENT_ROOT,
    CHANNEL_CONFIG_PATH,
    HISTORY_DIR,
    RUNTIME_SECRETS_PATH,
    load_channel_settings,
    load_runtime_secrets,
)
from WeClaw_console.core.asyncio_compat import ensure_main_thread_event_loop
from WeClaw_console.core.bot_runtime import BotRuntime
from gateway import GatewayService
from integrations.llm.provider import validate_llm_config

_LOG = logging.get_logger()

_RUNTIME_SECRETS = load_runtime_secrets(RUNTIME_SECRETS_PATH)
_QQ_CHANNEL_SETTINGS = load_channel_settings("qq", CHANNEL_CONFIG_PATH)
_QQ_CHANNEL_VALUES = _QQ_CHANNEL_SETTINGS.get("settings", {}) if isinstance(_QQ_CHANNEL_SETTINGS.get("settings"), dict) else {}


def _get_secret(name: str, fallback: str = "") -> str:
    if fallback:
        return fallback
    value = os.getenv(name, "")
    if value:
        return value
    local = _RUNTIME_SECRETS.get(name, "")
    return "" if local is None else str(local)

# === Optional local config (set and keep here for convenience) ===
# Example: LLM_API_KEY = "your_llm_api_key"
LLM_API_KEY = _get_secret("LLM_API_KEY", "")
# Example: LLM_BASE_URL = "https://api.openai.com/v1"
LLM_BASE_URL = _get_secret("LLM_BASE_URL", "")
# Example: LLM_MODEL = "gpt-4o-mini"
LLM_MODEL = _get_secret("LLM_MODEL", "")
# Example: LLM_PROVIDER = "openai|anthropic|dashscope"
LLM_PROVIDER = _get_secret("LLM_PROVIDER", "")
# Example: BOTPY_APPID = "your_bot_appid"
BOTPY_APPID = _get_secret("BOTPY_APPID", str(_QQ_CHANNEL_VALUES.get("app_id", "") or ""))
# Example: BOTPY_SECRET = "your_bot_secret"
BOTPY_SECRET = _get_secret("BOTPY_SECRET", str(_QQ_CHANNEL_VALUES.get("client_secret", "") or ""))

# Push into env so model settings can pick them up.
if LLM_API_KEY and not os.getenv("LLM_API_KEY"):
    os.environ["LLM_API_KEY"] = LLM_API_KEY
if LLM_BASE_URL and not os.getenv("LLM_BASE_URL"):
    os.environ["LLM_BASE_URL"] = LLM_BASE_URL
if LLM_MODEL and not os.getenv("LLM_MODEL"):
    os.environ["LLM_MODEL"] = LLM_MODEL
if LLM_PROVIDER and not os.getenv("LLM_PROVIDER"):
    os.environ["LLM_PROVIDER"] = LLM_PROVIDER
if BOTPY_APPID and not os.getenv("BOTPY_APPID"):
    os.environ["BOTPY_APPID"] = BOTPY_APPID
if BOTPY_SECRET and not os.getenv("BOTPY_SECRET"):
    os.environ["BOTPY_SECRET"] = BOTPY_SECRET

def _escape_for_qq(text: str) -> str:
    """规避 QQ 接口的 URL 过滤策略。"""
    return text.replace(".", "·")


def _preview_text(text: str, limit: int = 10) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}…"


def _safe_filename(name: str, fallback: str = "file") -> str:
    name = (name or "").strip()
    if not name:
        return fallback
    name = os.path.basename(name)
    name = name.replace("/", "_").replace("\\", "_")
    return name or fallback


def _unique_path(dest_dir: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_dir, filename)
    index = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, f"{base}_{index}{ext}")
        index += 1
    return candidate


def _download_attachments(attachments, dest_dir: str) -> list[str]:
    saved = []
    for att in attachments or []:
        url = getattr(att, "url", None)
        if not url:
            continue
        filename = _safe_filename(getattr(att, "filename", "") or "")
        if not filename:
            parsed = urllib.parse.urlparse(url)
            filename = _safe_filename(os.path.basename(parsed.path), "file")
        path = _unique_path(dest_dir, filename)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                with open(path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            saved.append(path)
        except Exception:
            continue
    return saved


class _TaskState:
    def __init__(self):
        self.running_task: Optional[asyncio.Task] = None
        self.cancel_requested = False
        self.pending_input = False
        self.reply_msg_id: Optional[str] = None
        self.reply_seq: int = 1
        self.api = None
        self.pending_system = deque()
        self.request_id = ""
        self.waiting_for_human = False
        self._seq_lock = threading.Lock()
        self._system_lock = threading.Lock()

    def next_seq(self) -> int:
        with self._seq_lock:
            current = self.reply_seq
            self.reply_seq += 1
            return current

    def enqueue_system(self, content: str) -> None:
        if not content:
            return
        with self._system_lock:
            self.pending_system.append(content)

    def pop_system(self) -> Optional[str]:
        with self._system_lock:
            if not self.pending_system:
                return None
            return self.pending_system.popleft()

    def has_pending_system(self) -> bool:
        with self._system_lock:
            return bool(self.pending_system)


class MyClient(botpy.Client):
    """Botpy 客户端，处理私聊消息。"""

    def __init__(self, gateway: GatewayService, intents):
        super().__init__(intents=intents)
        self.gateway = gateway
        self._states: Dict[str, _TaskState] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def on_ready(self):
        """机器人启动完成时触发。"""
        self._loop = asyncio.get_running_loop()
        _LOG.info(f"robot {self.robot.name} on_ready!")

    def _get_state(self, user_id: str) -> _TaskState:
        state = self._states.get(user_id)
        if state is None:
            state = _TaskState()
            self._states[user_id] = state
        return state

    def enqueue_system_message(self, user_id: str, content: str) -> None:
        content = (content or "").strip()
        if not content:
            return
        state = self._get_state(user_id)
        state.enqueue_system(content)
        if self._loop is None:
            _LOG.warning("System message dropped: event loop not ready.")
            return
        self._loop.call_soon_threadsafe(self._ensure_system_task, user_id)

    def _ensure_system_task(self, user_id: str) -> None:
        state = self._get_state(user_id)
        running = state.running_task is not None and not state.running_task.done()
        if running:
            return
        if not state.has_pending_system():
            return
        state.running_task = asyncio.create_task(self._drain_system_queue(user_id, state))

    async def _send(self, api, user_id: str, msg_id: Optional[str], text: str, msg_seq: int = 1) -> None:
        content = _escape_for_qq(text)
        if msg_id:
            try:
                await api.post_c2c_message(
                    openid=user_id,
                    msg_type=0,
                    msg_id=msg_id,
                    msg_seq=msg_seq,
                    content=content,
                )
                return
            except Exception as exc:
                _LOG.warning("Passive reply failed for user %s, fallback to active message: %s", user_id, exc)
        await self._send_active(api, user_id, content)

    async def _send_active(self, api, user_id: str, content: str) -> None:
        payload = {"msg_type": 0, "content": content}
        route = Route("POST", "/v2/users/{openid}/messages", openid=user_id)
        try:
            await api._http.request(route, json=payload)
        except Exception as exc:
            _LOG.warning("Active message failed for user %s: %s", user_id, exc)


    async def _run_task(self, user_id: str, content: str, api, msg_id: str, state: _TaskState) -> None:
        loop = asyncio.get_running_loop()
        req = type(
            "QQGatewayRequest",
            (),
            {
                "request_id": "",
                "user_id": user_id,
                "session_name": "",
                "content": content,
                "source": "qq",
                "inject_uploaded_files": False,
            },
        )()
        request_id, queue = self.gateway.start_chat_stream(req, loop)
        state.request_id = request_id
        streamed = False
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                payload = dict(event.payload or {})
                if event.type == "assistant_delta":
                    delta = str(payload.get("delta") or "").strip()
                    if not delta:
                        continue
                    streamed = True
                    await self._send(api, user_id, msg_id, delta, msg_seq=state.next_seq())
                elif event.type == "ask_human":
                    question = str(payload.get("question") or "").strip()
                    if question:
                        state.waiting_for_human = True
                        await self._send(api, user_id, msg_id, question, msg_seq=state.next_seq())
                elif event.type == "status":
                    phase = str(payload.get("phase") or "").strip()
                    if phase == "human_input_received":
                        state.waiting_for_human = False
                elif event.type == "run_done":
                    reply_text = str(payload.get("final_text") or "").strip()
                    if reply_text and not streamed:
                        await self._send(api, user_id, msg_id, reply_text, msg_seq=state.next_seq())
        finally:
            state.running_task = None
            state.request_id = ""
            state.waiting_for_human = False
            self._ensure_system_task(user_id)

        if state.pending_input:
            await self._send(
                api,
                user_id,
                msg_id,
                "我现在任务完成了，我注意到你之前给我发了消息，但我都没有听见，你可以重新和我说一遍",
                msg_seq=state.next_seq(),
            )
            state.pending_input = False

    async def _run_system_message(self, user_id: str, content: str, state: _TaskState) -> None:
        api = state.api
        msg_id = state.reply_msg_id
        if api is None:
            _LOG.warning("System message dropped: missing api for user %s", user_id)
            return

        result = await asyncio.to_thread(
            self.gateway.dispatch_background_prompt,
            user_id=user_id,
            session_name="",
            content=content,
            source="qq_system",
            wait=True,
        )
        reply_text = str(result.get("final_text") or result.get("error") or "").strip()

        if reply_text:
            await self._send(api, user_id, msg_id, reply_text, msg_seq=state.next_seq())
            if state.pending_input:
                await self._send(
                    api,
                    user_id,
                    msg_id,
                    "我现在任务完成了，我注意到你之前给我发了消息，但我都没有听见，你可以重新和我说一遍",
                    msg_seq=state.next_seq(),
                )
                state.pending_input = False

    async def _drain_system_queue(self, user_id: str, state: _TaskState) -> None:
        try:
            while True:
                content = state.pop_system()
                if not content:
                    break
                state.cancel_requested = False
                await self._run_system_message(user_id, content, state)
        finally:
            state.running_task = None
            if state.has_pending_system():
                self._ensure_system_task(user_id)

    async def on_c2c_message_create(self, message: C2CMessage):
        """私聊消息入口。"""
        # 获取用户唯一标识与消息内容
        user_id = message.author.user_openid
        content = (message.content or "").strip()
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        state = self._get_state(user_id)
        state.api = message._api
        running = state.running_task is not None and not state.running_task.done()
        if not running:
            state.reply_seq = 1
            next_seq = state.next_seq
        else:
            seq = 1

            def next_seq() -> int:
                nonlocal seq
                current = seq
                seq += 1
                return current
        if content:
            preview = _preview_text(content, 10)
            await self._send(
                message._api,
                user_id,
                message.id,
                f"已收到【{preview}】，正在处理",
                msg_seq=next_seq(),
            )
        attachments = getattr(message, "attachments", None) or []
        if attachments:
            await self._send(
                message._api,
                user_id,
                message.id,
                "检测到发送文件，正在下载中...",
                msg_seq=next_seq(),
            )
            saved_paths = await asyncio.to_thread(_download_attachments, attachments, str(AGENT_ROOT))
            if saved_paths:
                summary = "；".join(os.path.basename(p) for p in saved_paths)
                await self._send(
                    message._api,
                    user_id,
                    message.id,
                    f"已经完成下载，保存到了工作目录：{summary}。请问需要对文件做什么操作？",
                    msg_seq=next_seq(),
                )
                if content:
                    content = f"{content}\n\n【系统提示】已保存文件：{summary}"
                else:
                    return
            else:
                await self._send(
                    message._api,
                    user_id,
                    message.id,
                    "文件下载失败（可能是权限或链接已过期）。请重试或直接发送可访问的文件链接。",
                    msg_seq=next_seq(),
                )
                if not content:
                    return
        if not content:
            return

        if running:
            if state.waiting_for_human:
                if content == "停止任务":
                    state.cancel_requested = True
                    if state.request_id:
                        self.gateway.cancel_request(state.request_id)
                    await self._send(
                        message._api,
                        user_id,
                        message.id,
                        "已停止任务。",
                        msg_seq=next_seq(),
                    )
                else:
                    self.gateway.provide_human_input(user_id, content)
                return
            if content == "停止任务":
                state.cancel_requested = True
                if state.request_id:
                    self.gateway.cancel_request(state.request_id)
                await self._send(
                    message._api,
                    user_id,
                    message.id,
                    "已停止任务。",
                    msg_seq=next_seq(),
                )
            else:
                state.pending_input = True
                await self._send(
                    message._api,
                    user_id,
                    message.id,
                    "正在完成您给的任务，在任务完成或者失败前我都会捂住我的耳朵不听任何别的话，除非你显式的输入【停止任务】这4个字",
                    msg_seq=next_seq(),
                )
            return

        state.cancel_requested = False
        state.pending_input = False
        state.reply_msg_id = message.id
        state.running_task = asyncio.create_task(
            self._run_task(user_id, content, message._api, message.id, state)
        )


def main() -> None:
    """程序入口。"""
    llm_error = validate_llm_config()
    if llm_error:
        print(f"LLM 配置不完整：{llm_error}。请至少设置 LLM_API_KEY。")
        return

    appid = os.getenv("BOTPY_APPID", "").strip()
    secret = os.getenv("BOTPY_SECRET", "").strip()
    if not appid or not secret:
        print("需要先注册 QQ 开发平台并提供 APPID 与 Secret，否则无法使用。")
        return
    runtime = BotRuntime(
        history_dir=str(HISTORY_DIR),
        agent_root=str(AGENT_ROOT),
        agent_id=AGENT_ID,
        max_rounds=20,
        max_steps=20,
        web_user_id="qq:local",
    )
    gateway = GatewayService(runtime)
    ensure_main_thread_event_loop()
    intents = botpy.Intents(public_messages=True)
    client = MyClient(gateway=gateway, intents=intents)
    runtime.bot.set_system_handler(client.enqueue_system_message)
    client.run(appid=appid, secret=secret)


if __name__ == "__main__":
    main()
