# -*- coding: utf-8 -*-
"""Utility helpers for model metering."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List


def now_ts() -> float:
    return datetime.now().timestamp()


def day_from_ts(ts: float) -> str:
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d")


def day_to_date(day_text: str) -> datetime:
    return datetime.strptime(day_text, "%Y-%m-%d")


def iter_days_inclusive(from_ts: float, to_ts: float) -> List[str]:
    start_day = day_to_date(day_from_ts(from_ts))
    end_day = day_to_date(day_from_ts(to_ts))
    if start_day > end_day:
        start_day, end_day = end_day, start_day
    rows: List[str] = []
    current = start_day
    while current <= end_day:
        rows.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return rows


def bucket_start_ts(ts: float, bucket: str) -> int:
    dt = datetime.fromtimestamp(float(ts))
    if bucket == "day":
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif bucket == "hour":
        dt = dt.replace(minute=0, second=0, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    return int(dt.timestamp())


def auto_bucket(from_ts: int, to_ts: int) -> str:
    span = max(0, int(to_ts) - int(from_ts))
    if span <= 24 * 3600:
        return "minute"
    if span <= 7 * 24 * 3600:
        return "hour"
    return "day"


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return max(minimum, min(maximum, parsed))


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def clip_text(value: Any, limit: int = 400) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def normalize_text(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n")


def to_jsonable(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        return str(value)


def ensure_dir(path: str) -> Path:
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def p95(values: Iterable[int]) -> int:
    rows = sorted(int(v) for v in values if isinstance(v, (int, float)))
    if not rows:
        return 0
    idx = max(0, min(len(rows) - 1, math.ceil(len(rows) * 0.95) - 1))
    return int(rows[idx])


def safe_lower(value: Any) -> str:
    return str(value or "").strip().lower()


def parse_call_id_day(call_id: str) -> str:
    text = str(call_id or "").strip()
    if len(text) >= 8 and text[:8].isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return ""


def compact_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        return str(value)
