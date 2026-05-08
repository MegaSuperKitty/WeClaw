# -*- coding: utf-8 -*-
"""Session file discovery and extraction from workspace-private history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.history.context_builder import build_model_messages_from_session
from core.history.render_reader import replay_session_summary

from .types import FileFingerprint, SessionDocument, SessionMessageRecord
from .utils import compact_whitespace, detect_channel_prefix, safe_json_loads, to_external_user_id


class SessionSourceLoader:
    """Load and normalize workspace history session files."""

    def __init__(self, history_dir: str):
        self.history_dir = Path(history_dir).resolve()

    def iter_session_files(self) -> Iterable[Path]:
        if not self.history_dir.exists():
            return []
        paths = []
        for path in self.history_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.name == "state.json":
                continue
            if path.suffix == ".json" or path.name == "history.jsonl":
                paths.append(path)
        return paths

    def build_fingerprint(self, path: Path) -> Optional[FileFingerprint]:
        try:
            stat = path.stat()
            return FileFingerprint(file_path=str(path), mtime=float(stat.st_mtime), size=int(stat.st_size))
        except Exception:
            return None

    def load_document(self, path: Path) -> Optional[SessionDocument]:
        payload = self._load_json(path)
        if not payload and path.name != "history.jsonl":
            return None

        storage_user_id = self._user_id_from_path(path)
        external_user_id = to_external_user_id(storage_user_id)
        channel = detect_channel_prefix(external_user_id)
        session_name = self._session_name(path, payload)
        updated_text = str(payload.get("updated_at") or payload.get("created_at") or "")

        records: List[SessionMessageRecord] = []
        rows = self._extract_messages(path, payload)
        for idx, row in enumerate(rows):
            records.extend(self._extract_records(idx, row))

        return SessionDocument(
            file_path=str(path),
            user_id=external_user_id,
            session_name=session_name,
            channel_prefix=channel,
            updated_at=self._parse_updated_int(updated_text),
            updated_at_text=updated_text,
            messages=records,
        )

    def _extract_records(self, message_index: int, row: Any) -> List[SessionMessageRecord]:
        if not isinstance(row, dict):
            return []
        role = str(row.get("role") or "").strip().lower()
        if not role:
            role = "unknown"

        out: List[SessionMessageRecord] = []

        # Main content.
        content = str(row.get("content") or "").strip()
        if content:
            out.append(SessionMessageRecord(role=role, text=content, message_index=message_index))

        # Assistant tool calls are indexed as synthetic text for retrievability.
        if role == "assistant":
            calls = self._parse_tool_calls(row.get("tool_calls") or row.get("toolCalls") or row.get("toolcalls"))
            for call in calls:
                text = self._format_tool_call_text(call)
                if text:
                    out.append(
                        SessionMessageRecord(
                            role="assistant_tool_call",
                            text=text,
                            message_index=message_index,
                        )
                    )
        return out

    def _format_tool_call_text(self, call: Dict[str, Any]) -> str:
        fn = call.get("function") if isinstance(call.get("function"), dict) else {}
        if not fn and isinstance(call.get("func"), dict):
            fn = call.get("func")
        name = str(fn.get("name") or call.get("name") or call.get("tool_name") or "").strip()
        if not name:
            return ""
        args = fn.get("arguments")
        if isinstance(args, (dict, list)):
            args_text = json.dumps(args, ensure_ascii=False)
        else:
            args_text = str(args or "").strip()
        if args_text:
            return f"[tool_call] {name}\n{args_text}"
        return f"[tool_call] {name}"

    def _parse_tool_calls(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            return [value]
        if isinstance(value, str):
            parsed = safe_json_loads(value)
            if isinstance(parsed, list):
                return [row for row in parsed if isinstance(row, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        return []

    def _session_name(self, path: Path, payload: Dict[str, Any]) -> str:
        name = str(payload.get("name") or "").strip()
        if name:
            return name
        if path.name == "history.jsonl":
            return path.parent.name
        return path.stem

    def _user_id_from_path(self, path: Path) -> str:
        if path.name == "history.jsonl":
            summary = replay_session_summary(str(path))
            return str(summary.get("user_id") or "")
        try:
            relative_parent = path.parent.relative_to(self.history_dir)
            return str(relative_parent)
        except Exception:
            return path.parent.name

    def _extract_messages(self, path: Path, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        if path.name == "history.jsonl":
            model_messages = build_model_messages_from_session(session_path=str(path))
            rows: List[Dict[str, Any]] = []
            for item in model_messages:
                role = str(item.get("role") or "").strip()
                content = str(item.get("content") or "").strip()
                if role == "user":
                    parsed = safe_json_loads(content)
                    if isinstance(parsed, dict):
                        content = str(parsed.get("content") or "").strip()
                rows.append({"role": role, "content": content, "tool_calls": item.get("tool_calls")})
            return rows
        rows = payload.get("messages")
        return rows if isinstance(rows, list) else []

    def _parse_updated_int(self, updated_text: str) -> int:
        cleaned = "".join(ch for ch in str(updated_text or "") if ch.isdigit())
        if not cleaned:
            return 0
        try:
            return int(cleaned)
        except Exception:
            return 0

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.name == "history.jsonl":
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                return {}
            return data
        except UnicodeDecodeError:
            try:
                # Fallback for legacy files with non-utf8 encodings.
                with path.open("r", encoding="gbk", errors="replace") as handle:
                    data = json.load(handle)
                if not isinstance(data, dict):
                    return {}
                return data
            except Exception:
                return {}
        except Exception:
            return {}


def build_keyword_blob(text: str) -> str:
    """Normalize text for keyword fallback."""
    return compact_whitespace(text).lower()
