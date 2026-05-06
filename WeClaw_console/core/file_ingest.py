# -*- coding: utf-8 -*-
"""Upload file registry for auto-injection into chat prompts."""

from __future__ import annotations

from dataclasses import dataclass
import mimetypes
from pathlib import Path
import threading
import time
from typing import Dict, List


@dataclass
class UploadedFile:
    user_id: str
    path: str
    name: str
    size: int
    ts: float
    kind: str = "file"
    mime_type: str = "application/octet-stream"
    width: int | None = None
    height: int | None = None
    preview_text: str | None = None


class FileIngestStore:
    """Thread-safe uploaded file staging store for the next user turn."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_user: Dict[str, List[UploadedFile]] = {}

    def add_file(self, user_id: str, path: str, name: str, size: int) -> UploadedFile:
        mime_type, _ = mimetypes.guess_type(name or path)
        resolved_mime = mime_type or "application/octet-stream"
        kind = "image" if resolved_mime.startswith("image/") else "file"
        item = UploadedFile(
            user_id=user_id,
            path=path,
            name=name,
            size=int(size),
            ts=time.time(),
            kind=kind,
            mime_type=resolved_mime,
        )
        with self._lock:
            self._by_user.setdefault(user_id, []).append(item)
            # Keep recent 20 pending files max per user.
            self._by_user[user_id] = self._by_user[user_id][-20:]
        return item

    def list_files(self, user_id: str) -> List[UploadedFile]:
        with self._lock:
            return list(self._by_user.get(user_id, []))

    def consume_files(self, user_id: str) -> List[UploadedFile]:
        with self._lock:
            items = list(self._by_user.get(user_id, []))
            self._by_user[user_id] = []
        return items

    def to_attachment_descriptors(self, user_id: str) -> List[Dict[str, object]]:
        attachments = []
        for item in self.consume_files(user_id):
            attachments.append(
                {
                    "kind": item.kind,
                    "name": item.name,
                    "mime_type": item.mime_type,
                    "local_path": Path(item.path).as_posix(),
                    "size_bytes": int(item.size),
                    "width": item.width,
                    "height": item.height,
                    "preview_text": item.preview_text,
                }
            )
        return attachments
