# -*- coding: utf-8 -*-
"""Typed models for ephemeral subagent runtime."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict


SubagentRunState = Literal["created", "running", "finalizing", "completed", "failed", "cancelled"]


class SubagentStartRequest(TypedDict, total=False):
    task_description: str
    worker_kind: str
    instruction_text: str
    referenced_messages: List[Dict[str, Any]]
    allowed_tools: List[str]
    max_steps: int


class SubagentResult(TypedDict, total=False):
    subagent_id: str
    status: str
    worker_kind: str
    summary: str
    completed_work: List[str]
    remaining_work: List[str]
    next_step: str
    final_text: str


class SubagentRegistryRecord(TypedDict, total=False):
    subagent_id: str
    parent_session_id: str
    parent_run_id: str
    worker_kind: str
    status: SubagentRunState
    created_at: str
    started_at: str
    finished_at: str
    summary: str
    result: SubagentResult
    error: str
    cancel_requested: bool
    parent_delivery_enqueued: bool
