# -*- coding: utf-8 -*-
"""Facade for model call recording and billing queries."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
import os
import random
import threading
from typing import Any, Dict, Optional

from .aggregations import build_overview
from .reader import CallLogReader
from .utils import auto_bucket, clamp_int, day_from_ts, ensure_dir, now_ts, to_float, to_int
from .writer import JsonlDailyWriter


class ModelMeteringEngine:
    def __init__(self, log_dir: str):
        self.log_dir = str(ensure_dir(log_dir))
        self.writer = JsonlDailyWriter(self.log_dir)
        self.reader = CallLogReader(self.log_dir)
        self._lock = threading.Lock()

    def build_call_id(self, started_at: float) -> str:
        dt = datetime.fromtimestamp(float(started_at))
        stamp = dt.strftime("%Y%m%d%H%M%S")
        ms = int((float(started_at) % 1) * 1000)
        return f"{stamp}{ms:03d}_{os.getpid()}_{random.randint(100000, 999999)}"

    def record_call(self, record: Any) -> None:
        if record is None:
            return
        if is_dataclass(record):
            payload = asdict(record)
        elif isinstance(record, dict):
            payload = dict(record)
        else:
            return

        started_at = to_float(payload.get("started_at"), now_ts())
        payload.setdefault("started_at", started_at)
        payload.setdefault("finished_at", started_at)
        payload.setdefault("day", day_from_ts(started_at))
        payload.setdefault("call_id", self.build_call_id(started_at))
        payload.setdefault("success", False)
        payload.setdefault("latency_ms", max(0, int((to_float(payload.get("finished_at"), started_at) - started_at) * 1000)))

        usage = payload.get("usage")
        if not isinstance(usage, dict):
            usage = {}
        usage.setdefault("prompt_tokens", 0)
        usage.setdefault("completion_tokens", 0)
        usage.setdefault("total_tokens", to_int(usage.get("prompt_tokens"), 0) + to_int(usage.get("completion_tokens"), 0))
        usage.setdefault("source", "estimated")
        payload["usage"] = usage

        self.writer.append(payload)

    def status(self) -> Dict[str, Any]:
        read_status = self.reader.status()
        write_status = self.writer.status()
        return {
            "log_dir": self.log_dir,
            "readable_days": int(read_status.get("readable_days", 0)),
            "total_records": int(read_status.get("total_records", 0)),
            "last_write_at": float(max(read_status.get("last_write_at", 0.0), write_status.get("last_write_at", 0.0))),
            "writer_errors": int(write_status.get("writer_errors", 0)),
        }

    def get_overview(
        self,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        bucket: str = "",
        provider: str = "",
        model: str = "",
        profile_id: str = "",
        status: str = "all",
    ) -> Dict[str, Any]:
        from_ts_i, to_ts_i = self._normalize_window(from_ts, to_ts)
        bucket_name = self._normalize_bucket(bucket, from_ts_i, to_ts_i)

        rows = self.reader.query_records(
            from_ts=from_ts_i,
            to_ts=to_ts_i,
            provider=provider,
            model=model,
            profile_id=profile_id,
            status=status,
            q="",
        )
        overview = build_overview(rows, from_ts=from_ts_i, to_ts=to_ts_i, bucket=bucket_name)
        return {
            "filters": {
                "from_ts": from_ts_i,
                "to_ts": to_ts_i,
                "bucket": bucket_name,
                "provider": provider,
                "model": model,
                "profile_id": profile_id,
                "status": status,
            },
            "overview": overview,
        }

    def list_calls(
        self,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        provider: str = "",
        model: str = "",
        profile_id: str = "",
        status: str = "all",
        page: int = 1,
        page_size: int = 20,
        q: str = "",
    ) -> Dict[str, Any]:
        from_ts_i, to_ts_i = self._normalize_window(from_ts, to_ts)
        page_i = clamp_int(page, 1, 1, 100000)
        # Product rule: billing call list is fixed at 20 rows per page.
        _ = page_size
        size_i = 20

        rows = self.reader.query_records(
            from_ts=from_ts_i,
            to_ts=to_ts_i,
            provider=provider,
            model=model,
            profile_id=profile_id,
            status=status,
            q=q,
        )

        total = len(rows)
        start = (page_i - 1) * size_i
        end = start + size_i
        page_rows = rows[start:end]

        items = []
        for row in page_rows:
            usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
            success = bool(row.get("success", False))
            prompt_tokens = to_int(usage.get("prompt_tokens"), 0) if success else 0
            completion_tokens = to_int(usage.get("completion_tokens"), 0) if success else 0
            total_tokens = to_int(usage.get("total_tokens"), prompt_tokens + completion_tokens) if success else 0
            items.append(
                {
                    "call_id": row.get("call_id", ""),
                    "started_at": row.get("started_at", 0),
                    "success": success,
                    "provider": row.get("provider", ""),
                    "model": row.get("model", ""),
                    "profile_id": row.get("profile_id", ""),
                    "latency_ms": to_int(row.get("latency_ms"), 0),
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "usage_source": str(usage.get("source", "estimated") or "estimated"),
                    "input_preview": row.get("input_preview", ""),
                    "output_preview": row.get("output_preview", ""),
                    "error_message": row.get("error_message", ""),
                }
            )

        return {
            "filters": {
                "from_ts": from_ts_i,
                "to_ts": to_ts_i,
                "provider": provider,
                "model": model,
                "profile_id": profile_id,
                "status": status,
                "q": q,
            },
            "page": page_i,
            "page_size": size_i,
            "total": total,
            "items": items,
        }

    def get_call_detail(self, call_id: str) -> Dict[str, Any]:
        row = self.reader.find_by_call_id(call_id)
        if not row:
            raise ValueError("call not found")
        return row

    def _normalize_window(self, from_ts: Optional[int], to_ts: Optional[int]) -> tuple[int, int]:
        now_int = int(now_ts())
        from_i = int(from_ts) if from_ts is not None else now_int - 12 * 3600
        to_i = int(to_ts) if to_ts is not None else now_int
        if from_i > to_i:
            from_i, to_i = to_i, from_i
        return from_i, to_i

    def _normalize_bucket(self, bucket: str, from_ts: int, to_ts: int) -> str:
        name = str(bucket or "").strip().lower()
        if name in {"minute", "hour", "day"}:
            return name
        return auto_bucket(from_ts, to_ts)
