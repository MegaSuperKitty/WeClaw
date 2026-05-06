# -*- coding: utf-8 -*-
"""Small shared helpers for retrieval integration."""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
from typing import Iterable, List, Optional, Sequence


def sha1_text(text: str) -> str:
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()


def compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def normalize_preview(text: str, max_chars: int = 200) -> str:
    normalized = compact_whitespace(text)
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1] + "…"


def safe_json_dumps(value) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return str(value)


def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def decode_storage_user_id(storage_user_id: str) -> Optional[str]:
    """Decode `u_<base64url>` user id, if applicable."""
    raw = (storage_user_id or "").strip()
    if not raw.startswith("u_"):
        return None
    token = raw[2:]
    if not token:
        return None
    token += "=" * ((4 - len(token) % 4) % 4)
    try:
        return base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def to_external_user_id(storage_user_id: str) -> str:
    decoded = decode_storage_user_id(storage_user_id)
    if decoded:
        return decoded
    return (storage_user_id or "").strip()


def detect_channel_prefix(user_id: str) -> str:
    text = (user_id or "").strip()
    if ":" in text:
        return text.split(":", 1)[0] or "unknown"
    if text == "debug_user":
        return "cli"
    return "unknown"


def ensure_list_of_floats(values: Sequence[float]) -> List[float]:
    out: List[float] = []
    for value in values:
        try:
            out.append(float(value))
        except Exception:
            out.append(0.0)
    return out


def dot_product(a: Sequence[float], b: Sequence[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b)))


def norm(values: Iterable[float]) -> float:
    return math.sqrt(sum(v * v for v in values))


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    n1 = norm(a)
    n2 = norm(b)
    if n1 <= 0.0 or n2 <= 0.0:
        return 0.0
    return dot_product(a, b) / (n1 * n2)


def now_ts_ms() -> int:
    import time

    return int(time.time() * 1000)


def now_iso() -> str:
    import datetime as _dt

    return _dt.datetime.now().isoformat(timespec="seconds")


def parse_int_like(text: str, default: int = 0) -> int:
    raw = (text or "").strip()
    if not raw:
        return default
    m = re.search(r"(\d{8}_\d{6}|\d{8,14})", raw)
    token = m.group(1) if m else raw
    token = token.replace("_", "")
    try:
        return int(token)
    except Exception:
        return default
