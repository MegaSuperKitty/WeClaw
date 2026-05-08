# model_metering_core

Local model metering and call-audit core.

## Responsibilities

- Persist every LLM call to daily JSONL logs.
- Query logs by time range and filters.
- Aggregate token/call/failure/latency metrics.
- Provide call detail lookup by `call_id`.

## Directory layout

Logs are written under:

```text
model_call_logs/
  YYYY-MM-DD/
    calls-<pid>.jsonl
```

## Public API

- `ModelMeteringEngine.record_call(record)`
- `ModelMeteringEngine.get_overview(...)`
- `ModelMeteringEngine.list_calls(...)`
- `ModelMeteringEngine.get_call_detail(call_id)`
- `ModelMeteringEngine.status()`

Use `get_default_engine()` for shared singleton access.
