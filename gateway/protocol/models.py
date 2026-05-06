# -*- coding: utf-8 -*-
"""Gateway protocol models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import uuid


@dataclass(frozen=True)
class GatewayChatRequest:
    """Normalized chat request entering the gateway."""

    request_id: str
    user_id: str
    session_name: str
    content: str
    continue_mode: str
    source: str
    inject_uploaded_files: bool

    @classmethod
    def from_payload(cls, payload: Any) -> "GatewayChatRequest":
        return cls(
            request_id=(getattr(payload, "request_id", "") or "").strip() or str(uuid.uuid4()),
            user_id=(getattr(payload, "user_id", "") or "").strip() or "web:local",
            session_name=(getattr(payload, "session_name", "") or "").strip(),
            content=(getattr(payload, "content", "") or "").strip(),
            continue_mode=(getattr(payload, "continue_mode", "in_place") or "in_place").strip() or "in_place",
            source=(getattr(payload, "source", "web") or "web").strip() or "web",
            inject_uploaded_files=bool(getattr(payload, "inject_uploaded_files", True)),
        )
