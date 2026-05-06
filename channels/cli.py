# -*- coding: utf-8 -*-
"""CLI entry point for WeClaw local debugging."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from channels.common import AGENT_ID, AGENT_ROOT, HISTORY_DIR, RUNTIME_SECRETS_PATH, load_runtime_secrets

from WeClaw_console.core.bot_runtime import BotRuntime
from gateway import GatewayService
from integrations.llm.provider import validate_llm_config


STOP_TASK_COMMANDS = {"stop_task", "停止任务"}
_RUNTIME_SECRETS = load_runtime_secrets(RUNTIME_SECRETS_PATH)


def _get_secret(name: str, fallback: str = "") -> str:
    """Return secret value from fallback, env, or runtime YAML.
    
    Args:
        name (str): Input value for name.
        fallback (str): Input value for fallback.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if fallback:
        return fallback
    value = os.getenv(name, "")
    if value:
        return value
    secret = _RUNTIME_SECRETS.get(name, "")
    return "" if secret is None else str(secret)


# Optional local config values for convenience.
LLM_API_KEY = _get_secret("LLM_API_KEY", "")
LLM_BASE_URL = _get_secret("LLM_BASE_URL", "")
LLM_MODEL = _get_secret("LLM_MODEL", "")
LLM_PROVIDER = _get_secret("LLM_PROVIDER", "")
BOTPY_APPID = _get_secret("BOTPY_APPID", "")
BOTPY_SECRET = _get_secret("BOTPY_SECRET", "")


# Export local config to environment if missing there.
for env_name, env_value in [
    ("LLM_API_KEY", LLM_API_KEY),
    ("LLM_BASE_URL", LLM_BASE_URL),
    ("LLM_MODEL", LLM_MODEL),
    ("LLM_PROVIDER", LLM_PROVIDER),
    ("BOTPY_APPID", BOTPY_APPID),
    ("BOTPY_SECRET", BOTPY_SECRET),
]:
    if env_value and not os.getenv(env_name):
        os.environ[env_name] = env_value


class _DebugState:
    """Track in-flight task status for the interactive CLI loop.
    
    Attributes:
        running_task (asyncio.Task | None): Instance field for running task.
        cancel_requested (bool): Instance field for cancel requested.
        pending_input (bool): Instance field for pending input.
        reply_seq (int): Instance field for reply seq.
        request_id (str): Active gateway request id.
        waiting_for_human (bool): Whether ask-human is currently waiting.
    """

    def __init__(self):
        """Initialize task state fields.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        self.running_task: asyncio.Task | None = None
        self.cancel_requested = False
        self.pending_input = False
        self.reply_seq = 1
        self.request_id = ""
        self.waiting_for_human = False

    def next_seq(self) -> int:
        """Return next reply sequence id.
        
        Args:
            None.
        
        Returns:
            int: Result produced by this function.
        """
        current = self.reply_seq
        self.reply_seq += 1
        return current


async def _run_task(gateway: GatewayService, user_id: str, content: str, state: _DebugState) -> None:
    """Execute one gateway task and print streamed output to CLI.

    Args:
        gateway (GatewayService): Input value for gateway.
        user_id (str): Identifier for the user.
        content (str): Text content to process.
        state (_DebugState): Input value for state.
    
    Returns:
        None: This method does not return a value.
    
    Note:
        This is a private helper used internally by the module/class.
    """

    streamed = {"assistant_started": False}
    loop = asyncio.get_running_loop()
    req = SimpleNamespace(
        request_id="",
        user_id=user_id,
        session_name="",
        content=content,
        source="cli",
        inject_uploaded_files=False,
    )
    request_id, queue = gateway.start_chat_stream(req, loop)
    state.request_id = request_id
    final_text = ""
    try:
        while True:
            event = await queue.get()
            if event is None:
                break
            payload = dict(event.payload or {})
            if event.type == "assistant_delta":
                delta = str(payload.get("delta") or "")
                if not delta:
                    continue
                if not streamed["assistant_started"]:
                    print("Bot> ", end="", flush=True)
                    streamed["assistant_started"] = True
                print(delta, end="", flush=True)
            elif event.type == "ask_human":
                question = str(payload.get("question") or "").strip()
                if question:
                    if streamed["assistant_started"]:
                        print("")
                        streamed["assistant_started"] = False
                    print(f"Bot> {question}")
                    state.waiting_for_human = True
            elif event.type == "status":
                phase = str(payload.get("phase") or "").strip()
                if phase == "human_input_received":
                    state.waiting_for_human = False
            elif event.type == "run_done":
                final_text = str(payload.get("final_text") or "")
    finally:
        state.running_task = None
        state.request_id = ""
        state.waiting_for_human = False

    if final_text:
        if streamed["assistant_started"]:
            print("")
        else:
            print(f"Bot> {final_text}")
        if state.pending_input:
            print("Bot> Task finished. I saw your earlier message; please send it again.")
            state.pending_input = False


async def main_async() -> None:
    """Run the interactive CLI chat loop.
    
    Args:
        None.
    
    Returns:
        None: This method does not return a value.
    """
    runtime = BotRuntime(
        history_dir=str(HISTORY_DIR),
        agent_root=str(AGENT_ROOT),
        agent_id=AGENT_ID,
        max_rounds=20,
        max_steps=20,
        web_user_id="debug_user",
    )
    gateway = GatewayService(runtime)
    runtime.bot.set_system_handler(
        lambda gateway_user_id, system_content: gateway.dispatch_background_prompt(
            user_id=gateway_user_id,
            session_name="",
            content=system_content,
            source="cli_system",
            wait=False,
        )
    )
    user_id = "debug_user"
    state = _DebugState()

    print("WeClaw CLI (type /quit to exit)")
    print(f"Agent: {AGENT_ID}")
    print(f"Agent root: {AGENT_ROOT}")

    while True:
        try:
            content = (await asyncio.to_thread(input, "You> ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not content:
            continue
        if content.lower() in {"/quit", "/exit"}:
            print("Bye.")
            break

        llm_error = validate_llm_config()
        if llm_error:
            print(f"LLM config is incomplete: {llm_error}")
            print("Please set LLM_API_KEY (required).")
            continue

        normalized = content.strip().lower()

        if state.running_task is not None and not state.running_task.done():
            if state.waiting_for_human:
                if normalized in STOP_TASK_COMMANDS:
                    state.cancel_requested = True
                    if state.request_id:
                        gateway.cancel_request(state.request_id)
                    print("Bot> Task stopped.")
                else:
                    gateway.provide_human_input(user_id, content)
                continue

            if normalized in STOP_TASK_COMMANDS:
                state.cancel_requested = True
                if state.request_id:
                    gateway.cancel_request(state.request_id)
                print("Bot> Task stopped.")
            else:
                state.pending_input = True
                print("Bot> A task is running. Send 'stop_task' to interrupt.")
            continue

        state.cancel_requested = False
        state.pending_input = False
        state.reply_seq = 1
        state.waiting_for_human = False
        state.running_task = asyncio.create_task(_run_task(gateway, user_id, content, state))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
