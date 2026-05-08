# -*- coding: utf-8 -*-
"""Discord entry for WeClaw."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Dict, Optional

import aiohttp

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

from WeClaw_console.core.bot_runtime import BotRuntime
from gateway import GatewayService
from integrations.llm.provider import validate_llm_config

try:
    import discord  # type: ignore
except Exception:  # pragma: no cover
    discord = None

_DiscordClientBase = discord.Client if discord is not None else object
_DiscordDMChannel = discord.DMChannel if discord is not None else ()


_RUNTIME_SECRETS = load_runtime_secrets(RUNTIME_SECRETS_PATH)
_DISCORD_CHANNEL = load_channel_settings("discord", CHANNEL_CONFIG_PATH)
_DISCORD_VALUES = _DISCORD_CHANNEL.get("settings", {}) if isinstance(_DISCORD_CHANNEL.get("settings"), dict) else {}


def _value_from_sources(channel_value: str, env_name: str) -> str:
    channel_text = str(channel_value or "").strip()
    if channel_text:
        return channel_text
    env_text = os.getenv(env_name, "").strip()
    if env_text:
        return env_text
    secret_text = str(_RUNTIME_SECRETS.get(env_name, "") or "").strip()
    return secret_text


LLM_API_KEY = _value_from_sources("", "LLM_API_KEY")
LLM_BASE_URL = _value_from_sources("", "LLM_BASE_URL")
LLM_MODEL = _value_from_sources("", "LLM_MODEL")
LLM_PROVIDER = _value_from_sources("", "LLM_PROVIDER")

DISCORD_BOT_TOKEN = _value_from_sources(str(_DISCORD_VALUES.get("bot_token", "") or ""), "DISCORD_BOT_TOKEN")
DISCORD_HTTP_PROXY = _value_from_sources(str(_DISCORD_VALUES.get("http_proxy", "") or ""), "DISCORD_HTTP_PROXY")
DISCORD_HTTP_PROXY_AUTH = _value_from_sources(
    str(_DISCORD_VALUES.get("http_proxy_auth", "") or ""),
    "DISCORD_HTTP_PROXY_AUTH",
)
DISCORD_GUILD_ID = _value_from_sources(str(_DISCORD_VALUES.get("guild_id", "") or ""), "DISCORD_GUILD_ID")
DISCORD_BOT_PREFIX = (
    str(_DISCORD_CHANNEL.get("bot_prefix", "") or "").strip()
    or os.getenv("DISCORD_BOT_PREFIX", "").strip()
    or "[BOT] "
)


for key, value in [
    ("LLM_API_KEY", LLM_API_KEY),
    ("LLM_BASE_URL", LLM_BASE_URL),
    ("LLM_MODEL", LLM_MODEL),
    ("LLM_PROVIDER", LLM_PROVIDER),
    ("DISCORD_BOT_TOKEN", DISCORD_BOT_TOKEN),
    ("DISCORD_HTTP_PROXY", DISCORD_HTTP_PROXY),
    ("DISCORD_HTTP_PROXY_AUTH", DISCORD_HTTP_PROXY_AUTH),
    ("DISCORD_GUILD_ID", DISCORD_GUILD_ID),
]:
    if value and not os.getenv(key):
        os.environ[key] = value


class _TaskState:
    def __init__(self):
        self.running_task: Optional[asyncio.Task] = None
        self.cancel_requested = False
        self.pending_input = False
        self.request_id = ""
        self.waiting_for_human = False


class DiscordAngelClient(_DiscordClientBase):  # type: ignore[misc]
    def __init__(
        self,
        gateway: GatewayService,
        bot_prefix: str,
        allowed_guild_id: Optional[int],
        proxy: str,
        proxy_auth_text: str,
        **kwargs,
    ):
        self.gateway = gateway
        self.bot_prefix = (bot_prefix or "").strip()
        self.allowed_guild_id = allowed_guild_id
        self._states: Dict[str, _TaskState] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        proxy_auth = None
        auth_text = (proxy_auth_text or "").strip()
        if auth_text and ":" in auth_text:
            user, password = auth_text.split(":", 1)
            if user and password:
                proxy_auth = aiohttp.BasicAuth(user, password)

        super().__init__(
            proxy=(proxy or "").strip() or None,
            proxy_auth=proxy_auth,
            **kwargs,
        )

    async def on_ready(self) -> None:
        self._loop = asyncio.get_running_loop()
        print(f"Discord bot ready: {self.user}")

    def _get_state(self, user_key: str) -> _TaskState:
        state = self._states.get(user_key)
        if state is None:
            state = _TaskState()
            self._states[user_key] = state
        return state

    def _make_user_key(self, discord_user_id: int) -> str:
        return f"discord:{discord_user_id}"

    def _extract_discord_user_id(self, user_key: str) -> Optional[int]:
        text = (user_key or "").strip()
        if not text.startswith("discord:"):
            return None
        token = text.split(":", 1)[1].strip()
        if not token.isdigit():
            return None
        return int(token)

    async def _send_text(self, target, text: str) -> None:
        body = str(text or "").strip()
        if not body:
            return
        chunk_size = 1800
        for i in range(0, len(body), chunk_size):
            await target.send(body[i : i + chunk_size])

    def enqueue_system_message(self, user_id: str, content: str) -> None:
        if not content or self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self._dispatch_system_message(user_id, content), self._loop)

    async def _dispatch_system_message(self, user_id: str, content: str) -> None:
        result = await asyncio.to_thread(
            self.gateway.dispatch_background_prompt,
            user_id=user_id,
            session_name="",
            content=content,
            source="discord_system",
            wait=True,
        )
        text = str(result.get("final_text") or result.get("error") or "").strip()
        if not text:
            return
        uid = self._extract_discord_user_id(user_id)
        if uid is None:
            return
        user = self.get_user(uid)
        if user is None:
            try:
                user = await self.fetch_user(uid)
            except Exception:
                return
        await self._send_text(user, text)

    def _extract_prompt(self, message) -> str:
        content = (message.content or "").strip()
        if not content:
            return ""
        if _DiscordDMChannel and isinstance(message.channel, _DiscordDMChannel):
            return content
        if self.user is not None:
            mention_forms = [f"<@{self.user.id}>", f"<@!{self.user.id}>"]
            for tag in mention_forms:
                if content.startswith(tag):
                    return content[len(tag) :].strip()
        if self.bot_prefix and content.startswith(self.bot_prefix):
            return content[len(self.bot_prefix) :].strip()
        return ""

    def _guild_allowed(self, message) -> bool:
        if self.allowed_guild_id is None:
            return True
        if message.guild is None:
            return True
        return int(message.guild.id) == int(self.allowed_guild_id)

    async def _run_task(self, user_key: str, content: str, channel, state: _TaskState) -> None:
        loop = asyncio.get_running_loop()
        req = SimpleNamespace(
            request_id="",
            user_id=user_key,
            session_name="",
            content=content,
            source="discord",
            inject_uploaded_files=False,
        )
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
                    delta = str(payload.get("delta") or "")
                    if delta:
                        streamed = True
                        await self._send_text(channel, delta)
                elif event.type == "ask_human":
                    question = str(payload.get("question") or "").strip()
                    if question:
                        state.waiting_for_human = True
                        await self._send_text(channel, question)
                elif event.type == "status":
                    phase = str(payload.get("phase") or "").strip()
                    if phase == "human_input_received":
                        state.waiting_for_human = False
                elif event.type == "run_done":
                    reply_text = str(payload.get("final_text") or "").strip()
                    if reply_text and not streamed:
                        await self._send_text(channel, reply_text)
        finally:
            state.running_task = None
            state.request_id = ""
            state.waiting_for_human = False

        if state.pending_input:
            await self._send_text(
                channel,
                "Task finished. I saw another message during execution, please send it again.",
            )
            state.pending_input = False

    async def on_message(self, message) -> None:
        if message.author.bot:
            return
        if not self._guild_allowed(message):
            return

        prompt = self._extract_prompt(message)
        if not prompt:
            return

        user_key = self._make_user_key(message.author.id)
        state = self._get_state(user_key)
        running = state.running_task is not None and not state.running_task.done()

        if running:
            if state.waiting_for_human:
                if prompt in {"停止任务", "stop task"}:
                    state.cancel_requested = True
                    if state.request_id:
                        self.gateway.cancel_request(state.request_id)
                    await self._send_text(message.channel, "已停止任务。")
                else:
                    self.gateway.provide_human_input(user_key, prompt)
                    await self._send_text(message.channel, "已收到你的补充输入。")
                return
            if prompt in {"停止任务", "stop task"}:
                state.cancel_requested = True
                if state.request_id:
                    self.gateway.cancel_request(state.request_id)
                await self._send_text(message.channel, "已停止任务。")
            else:
                state.pending_input = True
                await self._send_text(message.channel, "正在处理当前任务。若需中断，请发送“停止任务”。")
            return

        state.cancel_requested = False
        state.pending_input = False
        state.running_task = asyncio.create_task(self._run_task(user_key, prompt, message.channel, state))


def _parse_optional_int(value: str) -> Optional[int]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    return None


def main() -> None:
    if discord is None:
        print("Missing dependency: discord.py. Install it first: pip install discord.py")
        return

    llm_error = validate_llm_config()
    if llm_error:
        print(f"LLM config is incomplete: {llm_error}")
        return

    token = os.getenv("DISCORD_BOT_TOKEN", "").strip() or DISCORD_BOT_TOKEN
    if not token:
        print(
            "Missing DISCORD_BOT_TOKEN. Configure it in the Channels page "
            "or ~/.weclaw/agents/<agent_id>/runtime/secrets.yaml."
        )
        return

    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.dm_messages = True
    intents.message_content = True

    runtime = BotRuntime(
        history_dir=str(HISTORY_DIR),
        agent_root=str(AGENT_ROOT),
        agent_id=AGENT_ID,
        max_rounds=20,
        max_steps=20,
        web_user_id="discord:local",
    )
    gateway = GatewayService(runtime)

    client = DiscordAngelClient(
        gateway=gateway,
        bot_prefix=DISCORD_BOT_PREFIX,
        allowed_guild_id=_parse_optional_int(os.getenv("DISCORD_GUILD_ID", "").strip() or DISCORD_GUILD_ID),
        proxy=os.getenv("DISCORD_HTTP_PROXY", "").strip() or DISCORD_HTTP_PROXY,
        proxy_auth_text=os.getenv("DISCORD_HTTP_PROXY_AUTH", "").strip() or DISCORD_HTTP_PROXY_AUTH,
        intents=intents,
    )
    runtime.bot.set_system_handler(client.enqueue_system_message)
    client.run(token)


if __name__ == "__main__":
    main()
