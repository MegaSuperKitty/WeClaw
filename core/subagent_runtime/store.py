# -*- coding: utf-8 -*-
"""Helpers for ephemeral subagent prompt and result shaping."""

from __future__ import annotations

from typing import Any, Dict, List

from .models import SubagentResult, SubagentStartRequest


def normalize_referenced_messages(messages: List[Dict[str, Any]] | None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in list(messages or []):
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "id": str(item.get("id") or "").strip(),
                "role": str(item.get("role") or "").strip(),
                "content": str(item.get("content") or ""),
                "ts": str(item.get("ts") or "").strip(),
            }
        )
    return rows


def build_subagent_prompt(request: SubagentStartRequest) -> str:
    parts = [
        f"Task: {str(request.get('task_description') or '').strip()}",
        f"Worker kind: {str(request.get('worker_kind') or 'worker').strip()}",
    ]
    instruction_text = str(request.get("instruction_text") or "").strip()
    if instruction_text:
        parts.append(f"Instruction: {instruction_text}")
    allowed_tools = [str(item).strip() for item in list(request.get("allowed_tools") or []) if str(item).strip()]
    if allowed_tools:
        parts.append("Allowed tools: " + ", ".join(allowed_tools))
    referenced = normalize_referenced_messages(request.get("referenced_messages") or [])
    if referenced:
        rendered = []
        for item in referenced:
            rendered.append(f"[{item['id']}] {item['role']}: {item['content']}")
        parts.append("Referenced messages:\n" + "\n".join(rendered))
    parts.append(
        "Role rules:\n"
        "- You are a temporary worker for the parent session, not a persistent task session.\n"
        "- Focus only on the assigned task and do not expand the scope on your own.\n"
        "- Use tools only when they materially help complete the assigned work.\n"
        "- Return a concise structured final result that the parent session can continue from."
    )
    parts.append("Return a concise structured final result when the work is done.")
    return "\n\n".join(parts)


def build_final_result(
    *,
    subagent_id: str,
    status: str,
    worker_kind: str,
    summary: str,
    final_text: str,
) -> SubagentResult:
    return SubagentResult(
        {
            "subagent_id": subagent_id,
            "status": status,
            "worker_kind": worker_kind,
            "summary": summary,
            "completed_work": [summary] if summary else [],
            "remaining_work": [] if status == "completed" else ["See summary"],
            "next_step": "" if status == "completed" else "Review partial result and continue from parent agent.",
            "final_text": final_text,
        }
    )
