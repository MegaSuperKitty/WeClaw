# -*- coding: utf-8 -*-
"""Read call logs from daily JSONL partitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

from .utils import iter_days_inclusive, parse_call_id_day, safe_lower, to_float


class CallLogReader:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()

    def iter_records(
        self,
        from_ts: float,
        to_ts: float,
        day_hint: str = "",
    ) -> Iterator[Dict[str, Any]]:
        if day_hint:
            days = [day_hint]
        else:
            days = iter_days_inclusive(from_ts, to_ts)

        for day in days:
            day_dir = self.base_dir / day
            if not day_dir.is_dir():
                continue
            files = sorted(day_dir.glob("calls-*.jsonl"))
            for file_path in files:
                yield from self._iter_file(file_path, from_ts, to_ts)

    def query_records(
        self,
        from_ts: float,
        to_ts: float,
        provider: str = "",
        model: str = "",
        profile_id: str = "",
        status: str = "all",
        q: str = "",
    ) -> List[Dict[str, Any]]:
        p_provider = safe_lower(provider)
        p_model = safe_lower(model)
        p_profile = str(profile_id or "").strip()
        p_status = safe_lower(status or "all")
        p_q = safe_lower(q)

        rows: List[Dict[str, Any]] = []
        for record in self.iter_records(from_ts, to_ts):
            if p_provider and safe_lower(record.get("provider")) != p_provider:
                continue
            if p_model and safe_lower(record.get("model")) != p_model:
                continue
            if p_profile and str(record.get("profile_id", "")).strip() != p_profile:
                continue

            success = bool(record.get("success", False))
            if p_status == "success" and not success:
                continue
            if p_status == "failed" and success:
                continue

            if p_q and not self._contains_q(record, p_q):
                continue

            rows.append(record)

        rows.sort(key=lambda item: float(item.get("started_at") or 0.0), reverse=True)
        return rows

    def find_by_call_id(self, call_id: str) -> Optional[Dict[str, Any]]:
        cid = str(call_id or "").strip()
        if not cid:
            return None

        day_hint = parse_call_id_day(cid)
        if day_hint:
            for row in self.iter_records(0, 4102444800, day_hint=day_hint):
                if str(row.get("call_id", "")).strip() == cid:
                    return row
            return None

        for row in self.iter_records(0, 4102444800):
            if str(row.get("call_id", "")).strip() == cid:
                return row
        return None

    def status(self) -> Dict[str, Any]:
        readable_days = 0
        total_records = 0
        last_write_at = 0.0

        if not self.base_dir.exists():
            return {
                "readable_days": 0,
                "total_records": 0,
                "last_write_at": 0.0,
            }

        for day_dir in sorted(self.base_dir.iterdir()):
            if not day_dir.is_dir():
                continue
            readable_days += 1
            for file_path in sorted(day_dir.glob("calls-*.jsonl")):
                for row in self._iter_file(file_path, 0, 4102444800):
                    total_records += 1
                    ts = to_float(row.get("started_at"), 0.0)
                    if ts > last_write_at:
                        last_write_at = ts

        return {
            "readable_days": readable_days,
            "total_records": total_records,
            "last_write_at": last_write_at,
        }

    def _iter_file(self, file_path: Path, from_ts: float, to_ts: float) -> Iterator[Dict[str, Any]]:
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    text = line.strip()
                    if not text:
                        continue
                    try:
                        row = json.loads(text)
                    except Exception:
                        continue
                    if not isinstance(row, dict):
                        continue
                    ts = to_float(row.get("started_at"), 0.0)
                    if ts < from_ts or ts > to_ts:
                        continue
                    yield row
        except Exception:
            return

    def _contains_q(self, record: Dict[str, Any], query: str) -> bool:
        haystacks = [
            safe_lower(record.get("provider")),
            safe_lower(record.get("model")),
            safe_lower(record.get("profile_id")),
            safe_lower(record.get("input_preview")),
            safe_lower(record.get("output_preview")),
            safe_lower(record.get("error_message")),
        ]

        req = record.get("request_payload")
        rsp = record.get("response_payload")
        if isinstance(req, dict):
            haystacks.append(safe_lower(json.dumps(req, ensure_ascii=False, default=str)))
        if isinstance(rsp, dict):
            haystacks.append(safe_lower(json.dumps(rsp, ensure_ascii=False, default=str)))

        return any(query in text for text in haystacks if text)
