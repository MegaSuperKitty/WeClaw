# -*- coding: utf-8 -*-
"""In-memory registry for ephemeral subagent runs."""

from __future__ import annotations

from threading import Lock
from typing import Dict, List
import uuid

from core.history.session_event_types import iso_timestamp
from .models import SubagentRegistryRecord, SubagentResult


class InMemorySubagentRegistry:
    """Keep subagent lifecycle state in memory only."""

    def __init__(self):
        self._lock = Lock()
        self._records: Dict[str, SubagentRegistryRecord] = {}

    def create(self, *, parent_session_id: str, parent_run_id: str = "", worker_kind: str = "worker") -> SubagentRegistryRecord:
        subagent_id = f"subagent_{uuid.uuid4().hex[:12]}"
        record = SubagentRegistryRecord(
            {
                "subagent_id": subagent_id,
                "parent_session_id": str(parent_session_id or "").strip(),
                "parent_run_id": str(parent_run_id or "").strip(),
                "worker_kind": str(worker_kind or "worker").strip() or "worker",
                "status": "created",
                "created_at": iso_timestamp(),
                "summary": "",
                "error": "",
                "cancel_requested": False,
                "parent_delivery_enqueued": False,
            }
        )
        with self._lock:
            self._records[subagent_id] = record
        return dict(record)

    def get(self, subagent_id: str) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            return dict(record) if record else None

    def update_status(self, subagent_id: str, status: str) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            if not record:
                return None
            record["status"] = status
            if status == "running" and not str(record.get("started_at") or "").strip():
                record["started_at"] = iso_timestamp()
            if status in {"completed", "failed", "cancelled"}:
                record["finished_at"] = iso_timestamp()
            return dict(record)

    def set_result(self, subagent_id: str, result: SubagentResult) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            if not record:
                return None
            record["result"] = dict(result or {})
            record["summary"] = str((result or {}).get("summary") or "").strip()
            record["status"] = str((result or {}).get("status") or "completed")
            record["finished_at"] = iso_timestamp()
            record["parent_delivery_enqueued"] = False
            return dict(record)

    def set_error(self, subagent_id: str, error: str) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            if not record:
                return None
            record["error"] = str(error or "")
            record["status"] = "failed"
            record["finished_at"] = iso_timestamp()
            record["parent_delivery_enqueued"] = False
            return dict(record)

    def cancel(self, subagent_id: str) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            if not record:
                return None
            record["cancel_requested"] = True
            if str(record.get("status") or "") not in {"completed", "failed", "cancelled"}:
                record["status"] = "cancelled"
                record["finished_at"] = iso_timestamp()
                record["summary"] = "Subagent cancelled by parent."
            record["parent_delivery_enqueued"] = False
            return dict(record)

    def is_cancel_requested(self, subagent_id: str) -> bool:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip()) or {}
            return bool(record.get("cancel_requested"))

    def list_by_parent(self, parent_session_id: str) -> List[SubagentRegistryRecord]:
        clean_parent = str(parent_session_id or "").strip()
        with self._lock:
            rows = [
                dict(record)
                for record in self._records.values()
                if str(record.get("parent_session_id") or "").strip() == clean_parent
            ]
        rows.sort(key=lambda item: str(item.get("created_at") or ""))
        return rows

    def mark_parent_delivery_enqueued(self, subagent_id: str) -> SubagentRegistryRecord | None:
        with self._lock:
            record = self._records.get(str(subagent_id or "").strip())
            if not record:
                return None
            record["parent_delivery_enqueued"] = True
            return dict(record)
