# -*- coding: utf-8 -*-
"""In-memory registry for active gateway runs."""

from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
from typing import Dict, List, Optional


@dataclass
class GatewayRunRecord:
    """Track one active gateway request/run."""

    request_id: str
    user_id: str
    session_name: str = ""
    status: str = "created"
    phase: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class GatewayRunRegistry:
    """Thread-safe registry keyed by request id."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: Dict[str, GatewayRunRecord] = {}

    def create(self, request_id: str, user_id: str, session_name: str = "") -> GatewayRunRecord:
        record = GatewayRunRecord(
            request_id=request_id,
            user_id=user_id,
            session_name=session_name,
        )
        with self._lock:
            self._records[request_id] = record
        return record

    def get(self, request_id: str) -> Optional[GatewayRunRecord]:
        with self._lock:
            return self._records.get(request_id)

    def update(
        self,
        request_id: str,
        *,
        status: Optional[str] = None,
        phase: Optional[str] = None,
        session_name: Optional[str] = None,
    ) -> Optional[GatewayRunRecord]:
        with self._lock:
            record = self._records.get(request_id)
            if record is None:
                return None
            if status is not None:
                record.status = status
            if phase is not None:
                record.phase = phase
            if session_name is not None:
                record.session_name = session_name
            record.updated_at = time.time()
            return record

    def remove(self, request_id: str) -> None:
        with self._lock:
            self._records.pop(request_id, None)

    def find_by_user(self, user_id: str) -> List[GatewayRunRecord]:
        normalized = str(user_id or "").strip()
        with self._lock:
            return [record for record in self._records.values() if record.user_id == normalized]
