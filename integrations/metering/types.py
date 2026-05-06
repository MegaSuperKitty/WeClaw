# -*- coding: utf-8 -*-
"""Type definitions for model metering and billing statistics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CallUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    source: str = "estimated"


@dataclass
class CallRequestPayload:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    model_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallResponsePayload:
    content: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: str = ""
    response_id: str = ""


@dataclass
class LLMCallRecord:
    call_id: str
    started_at: float
    finished_at: float
    day: str
    success: bool
    latency_ms: int
    provider: str
    provider_kind: str
    model: str
    base_url: str
    profile_id: str = ""
    stream: bool = False
    key_word: str = ""
    message_count: int = 0
    tool_count: int = 0
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    usage: CallUsage = field(default_factory=CallUsage)
    request_payload: CallRequestPayload = field(default_factory=CallRequestPayload)
    response_payload: CallResponsePayload = field(default_factory=CallResponsePayload)
    input_preview: str = ""
    output_preview: str = ""
    error_type: str = ""
    error_message: str = ""
    caller_file: str = ""
    caller_func: str = ""
    caller_line: int = 0
    process_id: int = 0
    thread_id: int = 0


@dataclass
class BillingSeriesPoint:
    bucket_start_ts: int
    call_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms_sum: int = 0


@dataclass
class BillingOverview:
    from_ts: int
    to_ts: int
    bucket: str
    total_calls: int = 0
    success_calls: int = 0
    failed_calls: int = 0
    failure_rate: float = 0.0
    prompt_tokens_total: int = 0
    completion_tokens_total: int = 0
    tokens_total: int = 0
    estimated_calls_count: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: int = 0
    series: List[BillingSeriesPoint] = field(default_factory=list)


@dataclass
class BillingCallListItem:
    call_id: str
    started_at: float
    success: bool
    provider: str
    model: str
    profile_id: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    usage_source: str
    input_preview: str
    output_preview: str
    error_message: str = ""


@dataclass
class BillingCallDetail:
    call_id: str
    started_at: float
    finished_at: float
    day: str
    success: bool
    provider: str
    provider_kind: str
    model: str
    base_url: str
    profile_id: str
    latency_ms: int
    stream: bool
    key_word: str
    message_count: int
    tool_count: int
    temperature: Optional[float]
    top_p: Optional[float]
    max_tokens: Optional[int]
    usage: CallUsage
    request_payload: CallRequestPayload
    response_payload: CallResponsePayload
    input_preview: str
    output_preview: str
    error_type: str = ""
    error_message: str = ""
    caller_file: str = ""
    caller_func: str = ""
    caller_line: int = 0
    process_id: int = 0
    thread_id: int = 0


@dataclass
class BillingStatus:
    log_dir: str
    readable_days: int = 0
    total_records: int = 0
    last_write_at: float = 0.0
    writer_errors: int = 0
