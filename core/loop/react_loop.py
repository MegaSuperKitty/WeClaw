# -*- coding: utf-8 -*-
"""ReAct agent implementation with context-direct writes and 4 hooks."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import math
import time

from core.context.lifecycle import ReActContextManager
from integrations.llm.provider import get_response

WAIT_FOR_UPDATE_TOOL_NAME = "wait_for_update"


@dataclass
class ReActHookEvent:
    """Hook event payload."""

    step: int
    phase: str
    tool_name: str = ""
    message: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    system_prompt: str = ""
    messages_count: int = 0
    timestamp: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReActHooks:
    """Only 4 hooks: LLM before/after and tool before/after."""

    before_llm: Optional[Callable[[ReActHookEvent], Optional[Tuple[List[Dict[str, Any]], str]]]] = None
    after_llm: Optional[Callable[[ReActHookEvent], Optional[Tuple[List[Dict[str, Any]], str]]]] = None
    before_tool: Optional[Callable[[ReActHookEvent], Optional[Tuple[List[Dict[str, Any]], str]]]] = None
    after_tool: Optional[Callable[[ReActHookEvent], Optional[Tuple[List[Dict[str, Any]], str]]]] = None


class ReActAgent:
    """Minimal synchronous ReAct agent."""

    def __init__(
        self,
        max_steps: int = 20,
        context_manager: Optional[ReActContextManager] = None,
        max_context_tokens: int = 60000,
        min_keep_messages: int = 6,
        system_prompt: Optional[str] = None,
        hooks: Optional[ReActHooks] = None,
        hook_error_mode: str = "isolate",
    ):
        self.max_steps = max_steps
        self.context_manager = context_manager or ReActContextManager(
            max_tokens=max_context_tokens,
            min_keep=min_keep_messages,
        )
        default_system_prompt = (
            "你是一个能调用工具的助手。"
            "如有必要请优先调用工具获取信息，然后给出简洁明确的回复。"
            "如果你要调用工具，必须在content字段写明调用工具的原因，不允许直接调用工具。"
        )
        self.system_prompt = system_prompt or default_system_prompt
        self.hooks = hooks or ReActHooks()
        self.hook_error_mode = hook_error_mode if hook_error_mode in {"isolate", "strict"} else "isolate"

    def run(
        self,
        tools=None,
        cancel_checker=None,
        stream: bool = False,
        on_token=None,
        on_reasoning=None,
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Execute ReAct loop.

        Returns:
            Tuple[str, List[Dict[str, str]]]: `(final_text, [])` for compatibility.
        """
        tool_specs, tool_map = self._normalize_tools(tools)
        runtime_system_prompt = self.system_prompt
        step_count = 0
        tool_call_count = 0
        tool_events: List[Dict[str, str]] = []

        for _ in range(self.max_steps):
            step_count += 1
            if cancel_checker and cancel_checker():
                return "", []

            # Hook 1: before_llm
            if self._has_hook("before_llm"):
                messages = self.context_manager.get_messages()
                messages, runtime_system_prompt = self._emit_hook(
                    "before_llm",
                    ReActHookEvent(
                        step=step_count,
                        phase="before_llm",
                        message=messages[-1] if messages else None,
                        messages=messages,
                        system_prompt=runtime_system_prompt,
                        messages_count=len(messages),
                        timestamp=time.time(),
                        extra={"tools_count": len(tool_specs)},
                    ),
                    messages,
                    runtime_system_prompt,
                )
                self.context_manager.set_messages(messages)

            messages = self.context_manager.get_messages()
            llm_messages = [{"role": "system", "content": runtime_system_prompt}] + messages
            message = self._assistant_message_with_tool_calls(
                get_response(
                    llm_messages,
                    tools=tool_specs,
                    stream=bool(stream),
                    on_token=on_token,
                    on_reasoning=on_reasoning,
                )
            )
            tool_calls = self._get_message_tool_calls(message)
            wait_calls = [
                call for call in tool_calls
                if self._get_tool_call_name(call) == WAIT_FOR_UPDATE_TOOL_NAME
            ]
            wait_for_update_requested = bool(wait_calls)
            if wait_calls:
                wait_call = wait_calls[0]
                message["tool_calls"] = [wait_call]
            if not tool_calls:
                message.pop("tool_calls", None)

            # Always append LLM message before after_llm hook.
            self.context_manager.append_message(message)

            # Hook 2: after_llm
            if self._has_hook("after_llm"):
                messages = self.context_manager.get_messages()
                messages, runtime_system_prompt = self._emit_hook(
                    "after_llm",
                    ReActHookEvent(
                        step=step_count,
                        phase="after_llm",
                        message=self._get_last_assistant_message(messages) or message,
                        messages=messages,
                        system_prompt=runtime_system_prompt,
                        messages_count=len(messages),
                        timestamp=time.time(),
                        extra={
                            "has_tool_calls": bool(tool_calls),
                            "tool_calls_count": len(tool_calls),
                        },
                    ),
                    messages,
                    runtime_system_prompt,
                )
                self.context_manager.set_messages(messages)

            messages = self.context_manager.get_messages()
            message = self._get_last_assistant_message(messages) or {}
            tool_calls = self._get_message_tool_calls(message)
            if not tool_calls:
                final_text = str(message.get("content") or "").strip()
                return final_text, []
            if wait_for_update_requested:
                wait_tool_calls = [
                    call for call in tool_calls
                    if self._get_tool_call_name(call) == WAIT_FOR_UPDATE_TOOL_NAME
                ]
                if wait_tool_calls:
                    tool_calls = [wait_tool_calls[0]]

            for call in tool_calls:
                if cancel_checker and cancel_checker():
                    return "", []
                # Hook 3: before_tool in order.
                if self._has_hook("before_tool"):
                    current_messages = self.context_manager.get_messages()
                    current_messages, runtime_system_prompt = self._emit_hook(
                        "before_tool",
                        ReActHookEvent(
                            step=step_count,
                            phase="before_tool",
                            tool_name=self._get_tool_call_name(call),
                            message=current_messages[-1] if current_messages else None,
                            messages=current_messages,
                            system_prompt=runtime_system_prompt,
                            messages_count=len(current_messages),
                            timestamp=time.time(),
                            extra={
                                "tool_call_id": self._get_tool_call_id(call),
                                "arguments": self._get_tool_call_arguments(call),
                            },
                        ),
                        current_messages,
                        runtime_system_prompt,
                    )
                    self.context_manager.set_messages(current_messages)

            if cancel_checker and cancel_checker():
                return "", []

            # Tool execution in parallel.
            tool_results = self._run_tool_calls_parallel(tool_calls, tool_map)

            # Process results and after_tool hooks in call order.
            for call, tool_result in zip(tool_calls, tool_results):
                if cancel_checker and cancel_checker():
                    return "", []
                tool_name = self._get_tool_call_name(call)
                tool_call_count += 1
                tool_events.append(self._summarize_tool_event(tool_name, tool_result))
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": self._get_tool_call_id(call),
                    "name": tool_name,
                    "content": tool_result,
                }
                self.context_manager.append_message(tool_msg)

                # Hook 4: after_tool.
                if self._has_hook("after_tool"):
                    current_messages = self.context_manager.get_messages()
                    current_messages, runtime_system_prompt = self._emit_hook(
                        "after_tool",
                        ReActHookEvent(
                            step=step_count,
                            phase="after_tool",
                            tool_name=tool_name,
                            message=current_messages[-1] if current_messages else tool_msg,
                            messages=current_messages,
                            system_prompt=runtime_system_prompt,
                            messages_count=len(current_messages),
                            timestamp=time.time(),
                            extra={
                                "tool_call_id": self._get_tool_call_id(call),
                                "result_preview": str(tool_result)[:200],
                                "error": str(tool_result).lower().startswith("tool error"),
                            },
                        ),
                        current_messages,
                        runtime_system_prompt,
                    )
                    self.context_manager.set_messages(current_messages)
            if wait_for_update_requested:
                wait_event = next(
                    (
                        event for event in reversed(tool_events)
                        if event.get("tool") == WAIT_FOR_UPDATE_TOOL_NAME
                    ),
                    {"tool": WAIT_FOR_UPDATE_TOOL_NAME},
                )
                wait_event = dict(wait_event)
                wait_event["wait_for_update"] = "1"
                return "", [wait_event]
            continue

        final_text = self._build_max_steps_reply(
            step_count=step_count,
            tool_call_count=tool_call_count,
            tool_events=tool_events,
        )
        self.context_manager.append_message({"role": "assistant", "content": final_text})
        return final_text, []

    def run_final_without_tools(
        self,
        cancel_checker=None,
        stream: bool = False,
        on_token=None,
        on_reasoning=None,
    ) -> Tuple[str, bool]:
        """Generate one final assistant message and report if it tried to call tools."""
        if cancel_checker and cancel_checker():
            return "", False
        messages = self.context_manager.get_messages()
        llm_messages = [{"role": "system", "content": self.system_prompt}] + messages
        message = self._assistant_message_with_tool_calls(
            get_response(
                llm_messages,
                tools=None,
                stream=bool(stream),
                on_token=on_token,
                on_reasoning=on_reasoning,
            )
        )
        if self._get_message_tool_calls(message):
            return "", True
        message.pop("tool_calls", None)
        self.context_manager.append_message(message)
        return str(message.get("content") or "").strip(), False

    def _has_hook(self, hook_name: str) -> bool:
        return getattr(self.hooks, hook_name, None) is not None

    def _emit_hook(
        self,
        hook_name: str,
        event: ReActHookEvent,
        messages: List[Dict[str, Any]],
        system_prompt: str,
    ) -> Tuple[List[Dict[str, Any]], str]:
        callback = getattr(self.hooks, hook_name, None)
        if callback is None:
            return messages, system_prompt
        try:
            updated = callback(event)
            if updated is None:
                return messages, system_prompt
            if not (isinstance(updated, tuple) and len(updated) == 2):
                raise ValueError(f"Hook '{hook_name}' must return (messages, system_prompt) or None.")
            updated_messages, updated_system_prompt = updated
            normalized_messages = self._validate_messages(updated_messages, hook_name=hook_name)
            normalized_system_prompt = str(updated_system_prompt or "")
            return normalized_messages, normalized_system_prompt
        except Exception:
            if self.hook_error_mode == "strict":
                raise
        return messages, system_prompt

    def _validate_messages(self, messages: Any, hook_name: str = "") -> List[Dict[str, Any]]:
        if not isinstance(messages, list):
            raise ValueError(f"Hook '{hook_name}' returned invalid messages type: {type(messages)}")
        normalized: List[Dict[str, Any]] = []
        valid_roles = {"system", "user", "assistant", "tool"}
        for idx, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"Hook '{hook_name}' message[{idx}] must be dict.")
            role = message.get("role")
            if not isinstance(role, str) or role not in valid_roles:
                raise ValueError(f"Hook '{hook_name}' message[{idx}] has invalid role: {role}")
            normalized_message = dict(message)
            if "content" not in normalized_message or normalized_message["content"] is None:
                normalized_message["content"] = ""
            elif not isinstance(normalized_message["content"], str):
                normalized_message["content"] = str(normalized_message["content"])
            if role == "assistant" and "tool_calls" in normalized_message:
                if not isinstance(normalized_message["tool_calls"], list):
                    raise ValueError(f"Hook '{hook_name}' assistant message[{idx}] tool_calls must be list.")
            normalized.append(normalized_message)
        return normalized

    def _normalize_tools(self, tools) -> Tuple[List[Dict], Dict[str, object]]:
        tool_specs: List[Dict] = []
        tool_map: Dict[str, object] = {}
        for tool in tools or []:
            if hasattr(tool, "spec") and hasattr(tool, "name"):
                tool_specs.append(tool.spec())
                tool_map[tool.name] = tool
            elif isinstance(tool, dict):
                tool_specs.append(tool)
        return tool_specs, tool_map

    def _assistant_message_with_tool_calls(self, message) -> Dict:
        tool_calls = []
        for call in getattr(message, "tool_calls", None) or []:
            tool_calls.append(
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
            )
        return {
            "role": "assistant",
            "content": message.content or "",
            "reasoning_content": getattr(message, "reasoning_content", "") or "",
            "tool_calls": tool_calls,
        }

    def _get_last_assistant_message(self, messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for message in reversed(messages or []):
            if isinstance(message, dict) and message.get("role") == "assistant":
                return message
        return None

    def _get_message_tool_calls(self, message: Optional[Dict[str, Any]]) -> List[Any]:
        if not isinstance(message, dict):
            return []
        tool_calls = message.get("tool_calls")
        return tool_calls if isinstance(tool_calls, list) else []

    def _get_tool_call_id(self, call: Any) -> str:
        if isinstance(call, dict):
            return str(call.get("id") or "")
        return str(getattr(call, "id", "") or "")

    def _get_tool_call_name(self, call: Any) -> str:
        if isinstance(call, dict):
            function = call.get("function") or {}
            if isinstance(function, dict):
                return str(function.get("name") or "")
            return ""
        function = getattr(call, "function", None)
        return str(getattr(function, "name", "") or "")

    def _get_tool_call_arguments(self, call: Any) -> str:
        if isinstance(call, dict):
            function = call.get("function") or {}
            if isinstance(function, dict):
                return str(function.get("arguments") or "")
            return ""
        function = getattr(call, "function", None)
        return str(getattr(function, "arguments", "") or "")

    def _run_tool_call(self, call, tool_map: Dict[str, object]) -> str:
        name = self._get_tool_call_name(call)
        arguments = self._get_tool_call_arguments(call)
        tool = tool_map.get(name)
        if not tool:
            return f"Tool not found: {name}"
        try:
            return tool.run(arguments)
        except Exception as exc:
            return f"Tool error: {exc}"

    def _run_tool_calls_parallel(self, tool_calls, tool_map: Dict[str, object]) -> List[str]:
        if not tool_calls:
            return []
        max_workers = min(8, len(tool_calls))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._run_tool_call, call, tool_map) for call in tool_calls]
            return [future.result() for future in futures]

    def _summarize_tool_event(self, tool_name: str, tool_result: str) -> Dict[str, str]:
        text = tool_result if isinstance(tool_result, str) else str(tool_result)
        snippet = text[:200].replace("\n", " ").strip()
        long_path = self._extract_long_output_path(text)
        error_flag = False
        if text:
            lowered = text.lower()
            if lowered.startswith("tool error") or "error" in lowered or "错误" in text:
                error_flag = True
        return {
            "tool": tool_name,
            "snippet": snippet,
            "long_path": long_path or "",
            "error": "1" if error_flag else "0",
        }

    def _extract_long_output_path(self, text: str) -> str:
        new_marker = "Tool output too long. Stored at: "
        if new_marker in text:
            start = text.find(new_marker) + len(new_marker)
            end = text.find(".", start)
            if end == -1:
                end = len(text)
            return text[start:end].strip()
        return ""

    def _build_max_steps_reply(self, step_count: int, tool_call_count: int, tool_events: List[Dict[str, str]]) -> str:
        summary = self._build_progress_summary(tool_events, max_tokens=200)
        lines = [
            f"已达到最大 {self.max_steps} 步执行限制（max_steps={self.max_steps}）。",
            f"本次已执行 {step_count} 步 / 工具调用 {tool_call_count} 次。",
            "",
            "过程摘要（<=200 tokens）：",
            summary,
            "",
            "未完成：",
            "- 尚未完成最终汇总与输出。",
            "",
            "需要你帮助：",
            "- 请补充关键信息或确认是否继续执行（回复‘继续’即可）。",
        ]
        return "\n".join(lines)

    def _build_progress_summary(self, tool_events: List[Dict[str, str]], max_tokens: int = 200) -> str:
        if not tool_events:
            return "已尝试分析任务，但未执行任何工具调用，当前停在规划阶段。"

        tools = []
        long_paths = []
        errors = []
        for event in tool_events:
            name = event.get("tool", "")
            if name and name not in tools:
                tools.append(name)
            path = event.get("long_path") or ""
            if path:
                long_paths.append(path)
            if event.get("error") == "1" and name:
                errors.append(name)

        actions = []
        tool_set = set(t.lower() for t in tools)
        if any("search" in t for t in tool_set):
            actions.append("检索资料")
        if any("fetch" in t for t in tool_set):
            actions.append("抓取网页")
        if any(t == "read" or "read" in t for t in tool_set):
            actions.append("读取文件")
        if any("write" in t or "edit" in t for t in tool_set):
            actions.append("写入/编辑内容")
        if any("skill" == t or "skill" in t for t in tool_set):
            actions.append("加载技能提示")

        tools_str = "、".join(tools[:4]) + (" 等" if len(tools) > 4 else "")
        action_str = "、".join(actions) if actions else "处理中间步骤"
        parts = [
            f"已完成{action_str}（涉及 {tools_str}），并对结果做了初步处理。",
        ]

        if long_paths:
            path = long_paths[0]
            if len(long_paths) == 1:
                parts.append(f"其中有 1 次输出过长已落盘到 {path}。")
            else:
                parts.append(f"其中有 {len(long_paths)} 次输出过长，已落盘到 {path} 等。")
        if errors:
            err_tools = "、".join(sorted(set(errors))[:3]) + (" 等" if len(set(errors)) > 3 else "")
            parts.append(f"过程中出现工具报错：{err_tools}。")
        summary = " ".join(parts)
        return self._limit_text_tokens(summary, max_tokens=max_tokens)

    def _limit_text_tokens(self, text: str, max_tokens: int = 200) -> str:
        if self._estimate_text_tokens(text) <= max_tokens:
            return text
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._estimate_text_tokens(text[:mid]) <= max_tokens:
                lo = mid + 1
            else:
                hi = mid
        cut = max(0, lo - 1)
        trimmed = text[:cut].rstrip()
        if trimmed and trimmed[-1] not in "。?!?":
            trimmed += "..."
        return trimmed

    def _estimate_text_tokens(self, text: str) -> int:
        ascii_count = sum(1 for ch in text if ord(ch) < 128)
        non_ascii = len(text) - ascii_count
        return non_ascii + math.ceil(ascii_count / 4)
