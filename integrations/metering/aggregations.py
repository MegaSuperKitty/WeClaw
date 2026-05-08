# -*- coding: utf-8 -*-
"""Aggregation logic for billing overview and time series."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Iterable, List

from .types import BillingOverview, BillingSeriesPoint
from .utils import bucket_start_ts, p95, to_float, to_int


def build_overview(records: Iterable[Dict[str, Any]], from_ts: int, to_ts: int, bucket: str) -> Dict[str, Any]:
    rows = list(records)
    series_map: Dict[int, BillingSeriesPoint] = {}

    total_calls = 0
    success_calls = 0
    failed_calls = 0
    prompt_tokens_total = 0
    completion_tokens_total = 0
    tokens_total = 0
    estimated_calls_count = 0
    latency_values: List[int] = []

    for row in rows:
        total_calls += 1
        success = bool(row.get("success", False))
        if success:
            success_calls += 1
        else:
            failed_calls += 1

        usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
        prompt_tokens = to_int(usage.get("prompt_tokens"), 0)
        completion_tokens = to_int(usage.get("completion_tokens"), 0)
        total_tokens = to_int(usage.get("total_tokens"), prompt_tokens + completion_tokens)
        source = str(usage.get("source", "estimated") or "estimated").strip().lower()
        if success and source != "provider":
            estimated_calls_count += 1

        # Failed calls are excluded from token totals by product requirement.
        if not success:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

        prompt_tokens_total += prompt_tokens
        completion_tokens_total += completion_tokens
        tokens_total += total_tokens

        latency_ms = to_int(row.get("latency_ms"), 0)
        latency_values.append(latency_ms)

        ts = to_float(row.get("started_at"), 0.0)
        bts = bucket_start_ts(ts, bucket)
        point = series_map.get(bts)
        if point is None:
            point = BillingSeriesPoint(bucket_start_ts=bts)
            series_map[bts] = point

        point.call_count += 1
        point.success_count += 1 if success else 0
        point.failed_count += 0 if success else 1
        point.prompt_tokens += prompt_tokens
        point.completion_tokens += completion_tokens
        point.total_tokens += total_tokens
        point.latency_ms_sum += latency_ms

    avg_latency_ms = round(sum(latency_values) / len(latency_values), 2) if latency_values else 0.0
    failure_rate = round((failed_calls / total_calls) * 100.0, 4) if total_calls else 0.0

    overview = BillingOverview(
        from_ts=int(from_ts),
        to_ts=int(to_ts),
        bucket=bucket,
        total_calls=total_calls,
        success_calls=success_calls,
        failed_calls=failed_calls,
        failure_rate=failure_rate,
        prompt_tokens_total=prompt_tokens_total,
        completion_tokens_total=completion_tokens_total,
        tokens_total=tokens_total,
        estimated_calls_count=estimated_calls_count,
        avg_latency_ms=avg_latency_ms,
        p95_latency_ms=p95(latency_values),
        series=[series_map[key] for key in sorted(series_map.keys())],
    )
    return asdict(overview)
