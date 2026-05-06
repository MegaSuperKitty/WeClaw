# -*- coding: utf-8 -*-
"""Synchronization helpers that apply MCP runtime state to host objects."""

from __future__ import annotations

from typing import Any

from integrations.mcp.runtime import MCPRuntime


def sync_mcp_runtime(target: Any, runtime: MCPRuntime = None):
    current_runtime = runtime or getattr(target, "mcp_runtime", None)
    if current_runtime is None:
        raise ValueError("sync_mcp_runtime requires an MCPRuntime.")
    snapshot = current_runtime.sync(target=target)
    active_tools = list(snapshot.active_tools)
    setattr(target, "_mcp_tools", active_tools)
    direct_tools = list(getattr(target, "_direct_tools", []) or [])
    setattr(target, "tools", direct_tools if direct_tools else active_tools)
    if hasattr(target, "_refresh_dynamic_mcp_prompt_block"):
        target._refresh_dynamic_mcp_prompt_block(snapshot)
    else:
        setattr(target, "system_prompt", str(getattr(target, "_base_system_prompt", "") or ""))
    return snapshot
