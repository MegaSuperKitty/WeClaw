# -*- coding: utf-8 -*-
"""Gateway event payloads shared by streaming subscribers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GatewayEvent:
    """Single event payload delivered to gateway stream subscribers."""

    type: str
    ts: float
    request_id: str
    payload: Dict[str, Any]
