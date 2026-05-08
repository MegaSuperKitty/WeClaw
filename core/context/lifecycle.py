# -*- coding: utf-8 -*-
"""Unified JSONL-backed context lifecycle and ReAct-specific behavior."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import math
import os

from integrations.llm.provider import get_response
from core.history.context_builder import build_model_messages_from_session
from core.history.session_event_types import (
    build_message_event,
    build_summary_checkpoint_event,
    iso_timestamp,
)
from core.history.session_jsonl_store import SessionJsonlStore
from core.workspace.layout import ensure_workspace_layout_for_source


def _timestamp() -> str:
    return iso_timestamp()


class ContextManager:
    """Base context manager backed by session JSONL events."""

    VALID_ROLES = {"system", "user", "assistant", "tool"}

    def __init__(
        self,
        context_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        write_through: bool = True,
    ):
        if context_path:
            path = os.path.abspath(context_path)
        else:
            default_base = ensure_workspace_layout_for_source(os.getcwd()).history_root
            base = os.path.abspath(base_dir or default_base)
            os.makedirs(base, exist_ok=True)
            stem = _timestamp().replace("-", "").replace(":", "").replace("T", "_")[:15]
            path = os.path.join(base, f"{stem}.jsonl")

        self._context_path = path
        self._write_through = bool(write_through)
        os.makedirs(os.path.dirname(self._context_path), exist_ok=True)

        self._store = SessionJsonlStore(self._context_path)
        self._store.ensure_created(
            session_id=os.path.splitext(os.path.basename(self._context_path))[0],
            session_name=os.path.splitext(os.path.basename(self._context_path))[0],
        )
        self._messages: List[Dict[str, Any]] = []
        self.reload()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return a safe copy of current model-facing messages."""
        return [dict(message) for message in self._messages]

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Replace runtime-only message cache without rewriting persisted events."""
        self._messages = [self._normalize_message(message) for message in (messages or [])]

    def append_message(self, message: Dict[str, Any]) -> None:
        """Append one validated message and persist it as a JSONL event."""
        normalized = self._normalize_message(message)
        if self._write_through:
            self._append_persisted_message(normalized)
            self.reload()
        else:
            self._messages.append(normalized)

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        for message in messages or []:
            self.append_message(message)

    def reload(self) -> None:
        """Reload model-facing messages from persisted events."""
        if self._write_through:
            self._messages = build_model_messages_from_session(session_path=self._context_path)

    def save(self) -> None:
        """JSONL store is append-only; save is a compatibility no-op."""
        return None

    def get_context_path(self) -> str:
        return self._context_path

    def _append_persisted_message(self, message: Dict[str, Any]) -> str:
        role = str(message.get("role") or "")
        extras: Dict[str, Any] = {}
        for key in ("reasoning_content", "name"):
            value = message.get(key)
            if value:
                extras[key] = value
        event = build_message_event(
            message_id=self._store.next_message_id(),
            role=role,
            author=self._infer_author(message),
            content=str(message.get("content") or ""),
            user_turn_meta=message.get("user_turn_meta") if role == "user" else None,
            tool_call_id=str(message.get("tool_call_id") or ""),
            tool_calls=message.get("tool_calls") if isinstance(message.get("tool_calls"), list) else [],
            extras=extras,
            ts=str(message.get("ts") or _timestamp()),
        )
        if role == "user" and "user_turn_meta" not in event["payload"]:
            event["payload"]["user_turn_meta"] = {
                "source": "web",
                "preferred_response_language": "zh",
                "request_kind": "user_message",
                "message_time": event["ts"],
                "attachments": [],
            }
        self._store.append_event(event)
        return str(event["payload"]["id"])

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(message, dict):
            raise ValueError("message must be dict")
        role = message.get("role")
        if role not in self.VALID_ROLES:
            raise ValueError(f"invalid role: {role}")

        normalized = dict(message)
        if "content" not in normalized or normalized.get("content") is None:
            normalized["content"] = ""
        elif not isinstance(normalized.get("content"), str):
            normalized["content"] = str(normalized.get("content"))
        return normalized

    def _infer_author(self, message: Dict[str, Any]) -> str:
        role = str(message.get("role") or "")
        if role == "tool":
            return "tool"
        if role == "assistant":
            return "assistant"
        if role == "system":
            return "runtime"
        return "user"


class ReActContextManager(ContextManager):
    """ReAct context manager with summary checkpoints and tool-output normalization."""

    def __init__(
        self,
        context_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        write_through: bool = True,
        max_tokens: int = 60000,
        min_keep: int = 6,
        agent_root: Optional[str] = None,
        tool_output_dir: Optional[str] = None,
        workspace_root: Optional[str] = None,
        summarizer=None,
    ):
        self.max_tokens = max_tokens
        self.min_keep = max(1, int(min_keep))
        self.agent_root = os.path.abspath(agent_root) if agent_root else None
        self.workspace_root = os.path.abspath(workspace_root) if workspace_root else self.agent_root
        self.summarizer = summarizer
        if tool_output_dir:
            self.tool_output_dir = tool_output_dir
        elif self.agent_root:
            self.tool_output_dir = os.path.join(self.agent_root, "tool_outputs")
        else:
            self.tool_output_dir = None
        self._tool_output_index = 0
        super().__init__(context_path=context_path, base_dir=base_dir, write_through=write_through)

    def set_messages(self, messages: List[Dict[str, Any]]) -> None:
        normalized = [self._normalize_for_react(message) for message in (messages or [])]
        self._messages = normalized

    def append_message(self, message: Dict[str, Any]) -> None:
        normalized = self._normalize_for_react(message)
        if self._write_through:
            self._append_persisted_message(normalized)
            self._maybe_append_summary_checkpoint()
            self.reload()
        else:
            self._messages.append(normalized)

    def append_messages(self, messages: List[Dict[str, Any]]) -> None:
        for message in messages or []:
            self.append_message(message)

    def _append_persisted_message(self, message: Dict[str, Any]) -> str:
        role = str(message.get("role") or "")
        normalized = dict(message)
        ts = str(normalized.get("ts") or _timestamp())
        if role == "user":
            meta = dict(normalized.get("user_turn_meta") or {})
            meta.setdefault("source", "web")
            meta.setdefault("preferred_response_language", "zh")
            meta.setdefault("request_kind", "user_message")
            meta.setdefault("message_time", ts)
            meta.setdefault("attachments", [])
            normalized["user_turn_meta"] = meta
            normalized["ts"] = ts
        return super()._append_persisted_message(normalized)

    def _normalize_for_react(self, message: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self._normalize_message(message)
        if normalized.get("role") == "tool":
            tool_name = normalized.get("name") or normalized.get("tool_name")
            if tool_name != "skill":
                normalized["content"] = self.normalize_tool_output(normalized.get("content", ""))
        return normalized

    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        total_chars = 0
        for msg in messages:
            total_chars += len(str(msg.get("role", ""))) + 1
            content = msg.get("content", "")
            if content:
                total_chars += len(str(content))
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                total_chars += len(json.dumps(tool_calls, ensure_ascii=False))
        return math.ceil(total_chars / 4)

    def window_messages(self, messages: List[Dict[str, Any]], preserve_system: bool = True) -> List[Dict[str, Any]]:
        if not messages:
            return []
        if self.estimate_tokens(messages) <= self.max_tokens:
            return list(messages)
        start_idx = 0
        system_msg: List[Dict[str, Any]] = []
        if preserve_system and messages[0].get("role") == "system":
            start_idx = 1
            system_msg = [messages[0]]

        body = messages[start_idx:]
        keep = body[-self.min_keep :]
        window = system_msg + keep
        while self.estimate_tokens(window) > self.max_tokens and len(keep) > 1:
            keep = keep[1:]
            window = system_msg + keep
        return window

    def normalize_tool_output(self, content: Any) -> str:
        if content is None:
            return ""
        text = content if isinstance(content, str) else str(content)
        if len(text) <= 10000:
            return text
        if text.startswith("Tool output too long. Stored at:"):
            return text

        output_path = self._write_tool_output(text)
        if output_path:
            rel_base = self.workspace_root or self.agent_root
            rel_path = os.path.relpath(output_path, rel_base) if rel_base else output_path
            prefix = (
                "Tool output too long. Stored at: "
                f"{rel_path}. Use read tool for the full content. Preview(1000 chars):\n"
            )
        else:
            prefix = "Tool output too long. Storage path unavailable. Preview(1000 chars):\n"
        return prefix + text[:1000]

    def _write_tool_output(self, content: str) -> Optional[str]:
        if not self.tool_output_dir:
            return None
        os.makedirs(self.tool_output_dir, exist_ok=True)
        self._tool_output_index += 1
        filename = f"tool_output_{_timestamp().replace(':', '').replace('-', '')}_{self._tool_output_index}.txt"
        path = os.path.join(self.tool_output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            return path
        except Exception:
            return None

    def _maybe_append_summary_checkpoint(self) -> None:
        messages = build_model_messages_from_session(session_path=self._context_path)
        if not messages:
            return
        if messages[-1].get("role") == "assistant":
            return
        if self.estimate_tokens(messages) < self.max_tokens:
            return
        if len(messages) <= 3:
            return
        removed = messages[:-3]
        kept = messages[-3:]
        summary = self._summarize_messages(removed)
        tail_ids = []
        count = 0
        for event in self._store.iter_events():
            if str(event.get("type") or "") != "message":
                continue
            count += 1
            tail_ids.append(str((event.get("payload") or {}).get("id") or ""))
        cover_index = max(0, count - len(kept) - 1)
        events = [e for e in self._store.iter_events() if str(e.get("type") or "") == "message"]
        if not events or cover_index < 0:
            return
        cover_id = str((events[cover_index].get("payload") or {}).get("id") or "")
        if not cover_id:
            return
        latest_summary = self._store.read_last_event("summary_checkpoint")
        if latest_summary:
            latest_cover = str(((latest_summary.get("payload") or {}).get("covers_until_message_id") or ""))
            if latest_cover == cover_id:
                return
        self._store.append_event(
            build_summary_checkpoint_event(
                summary_id=self._store.next_summary_id(),
                summary_text=summary,
                covers_until_message_id=cover_id,
                covered_message_count=max(0, count - len(kept)),
            )
        )

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        if self.summarizer:
            try:
                summary = self.summarizer.summarize(messages)
                if summary:
                    return summary.strip()
            except Exception:
                pass
        return self._fallback_structured_summary(messages)

    def _fallback_structured_summary(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return self._format_structured_summary(
                facts=["none"],
                done=["unknown"],
                todo=["unknown"],
                constraints=["unknown"],
                next_steps=["none"],
            )

        facts: List[str] = []
        done: List[str] = []
        todo: List[str] = []
        constraints: List[str] = []

        for msg in messages:
            role = str(msg.get("role", "user"))
            content = str(msg.get("content", "")).strip().replace("\n", " ")
            if not content:
                continue
            content = content[:120] + ("..." if len(content) > 120 else "")

            if role == "user" and len(facts) < 3:
                facts.append(content)
            if role == "assistant" and len(done) < 3 and any(
                key in content.lower() for key in ["done", "completed", "fixed", "implemented", "updated"]
            ):
                done.append(content)
            if len(todo) < 3 and any(key in content.lower() for key in ["need", "todo", "next", "please"]):
                todo.append(content)
            if len(constraints) < 3 and any(
                key in content.lower() for key in ["must", "cannot", "limit", "requirement", "note"]
            ):
                constraints.append(content)

        if not facts:
            facts = ["unknown"]
        if not done:
            done = ["unknown"]
        if not todo:
            todo = ["unknown"]
        if not constraints:
            constraints = ["unknown"]

        next_steps = todo[:2] if todo else ["unknown"]
        return self._format_structured_summary(facts, done, todo, constraints, next_steps)

    def _format_structured_summary(
        self,
        facts: List[str],
        done: List[str],
        todo: List[str],
        constraints: List[str],
        next_steps: List[str],
    ) -> str:
        return (
            "Facts: " + " ; ".join(facts) + "\n"
            "Done: " + " ; ".join(done) + "\n"
            "Todo: " + " ; ".join(todo) + "\n"
            "Constraints: " + " ; ".join(constraints) + "\n"
            "Next: " + " ; ".join(next_steps)
        )


class LlmSummarizer:
    """LLM-based conversation summarizer."""

    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_chars: int = 500,
    ):
        self.model = model or os.getenv("LLM_SUMMARIZER_MODEL", "")
        self.provider = provider or os.getenv("LLM_PROVIDER", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.max_output_chars = max_output_chars

    def summarize(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return (
                "Facts: none\n"
                "Done: unknown\n"
                "Todo: unknown\n"
                "Constraints: unknown\n"
                "Next: none"
            )

        content = self._format_messages(messages, max_chars=4000)
        prompt = (
            "Summarize the conversation into concise structured Chinese lines.\n"
            "Use exactly these fields and no extra text:\n"
            "Facts: ...\n"
            "Done: ...\n"
            "Todo: ...\n"
            "Constraints: ...\n"
            "Next: ...\n"
            "Do not fabricate facts.\n"
            "Conversation:\n"
            f"{content}"
        )

        response = get_response(
            prompts=[
                {"role": "system", "content": "You are a strict conversation summarizer."},
                {"role": "user", "content": prompt},
            ],
            tools=None,
            stream=False,
            temperature=0.0,
            top_p=0.1,
            provider=self.provider or None,
            base_url=self.base_url or None,
            api_key=self.api_key or None,
            model=self.model or None,
            max_tokens=1024,
        )
        text = (response.content or "").strip()
        if self.max_output_chars and len(text) > self.max_output_chars:
            text = text[: self.max_output_chars].rstrip() + "..."
        return text

    def _format_messages(self, messages: List[Dict[str, Any]], max_chars: int = 4000) -> str:
        parts: List[str] = []
        total = 0
        for msg in messages:
            role = str(msg.get("role", "user"))
            content = str(msg.get("content", "")).strip().replace("\n", " ")
            line = f"{role}: {content}"
            parts.append(line)
            total += len(line) + 1
            if total >= max_chars:
                break
        text = "\n".join(parts)
        if total >= max_chars:
            text += "\n..."
        return text
