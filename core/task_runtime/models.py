# -*- coding: utf-8 -*-
"""Typed models for task-session runtime storage."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class ReferencedMainMessage(TypedDict, total=False):
    id: str
    role: str
    content: str
    ts: str


class TaskQueueItem(TypedDict, total=False):
    message_kind: str
    instruction_text: str
    referenced_messages: List[ReferencedMainMessage]
    enqueued_at: str


class TaskPendingMessage(TypedDict, total=False):
    message_id: str
    origin: str
    task_id: str
    kind: str
    content: str
    payload: Dict[str, Any]
    created_at: str
    deliver_after_run_id: str
    delivered_at: str
    responded_at: str
    dropped_at: str


class TaskState(TypedDict, total=False):
    task_id: str
    parent_session_id: str
    title: str
    status: str
    run_phase: str
    instruction_text: str
    acceptance_criteria: List[str]
    priority: str
    latest_plan: List[str]
    latest_progress_summary: str
    pending_questions: List[Dict[str, Any]]
    result_summary: str
    queued_messages: List[TaskQueueItem]
    referenced_main_message_ids: List[str]
    created_at: str
    updated_at: str
    last_run_started_at: str
    last_run_finished_at: str
    active_run_id: str
    wake_reason: str
    closed_by: str
    closed_at: str


class TaskQuerySnapshot(TypedDict, total=False):
    task_id: str
    title: str
    status: str
    run_phase: str
    instruction_text: str
    latest_progress_summary: str
    messages: List[Dict[str, Any]]
