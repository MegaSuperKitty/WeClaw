# -*- coding: utf-8 -*-
"""Schema models for MCP discovery, configuration, and runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MCPServerManifest:
    server_id: str
    name: str
    description: str = ""
    mode: str = "local"
    transport: str = "stdio"
    requires_secrets: bool = False
    required_secrets: List[str] = field(default_factory=list)
    required_model_types: List[str] = field(default_factory=list)
    default_enabled: bool = True
    tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "server_id": self.server_id,
            "name": self.name,
            "description": self.description,
            "mode": self.mode,
            "transport": self.transport,
            "requires_secrets": self.requires_secrets,
            "required_secrets": list(self.required_secrets),
            "required_model_types": list(self.required_model_types),
            "default_enabled": bool(self.default_enabled),
            "tools": list(self.tools),
        }


@dataclass
class MCPClientConfig:
    client_id: str
    name: str
    description: str = ""
    enabled: bool = True
    mode: str = "local"
    transport: str = "stdio"
    server_id: str = ""
    endpoint: str = ""
    command: str = ""
    args: List[str] = field(default_factory=list)
    cwd: str = ""
    enabled_tools: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    secret_refs: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> "MCPClientConfig":
        mode = (self.mode or "local").strip().lower() or "local"
        transport = (self.transport or ("stdio" if mode == "local" else "streamable_http")).strip().lower()
        return MCPClientConfig(
            client_id=(self.client_id or "").strip(),
            name=(self.name or self.client_id or "").strip(),
            description=(self.description or "").strip(),
            enabled=bool(self.enabled),
            mode=mode,
            transport=transport,
            server_id=(self.server_id or "").strip(),
            endpoint=(self.endpoint or "").strip(),
            command=(self.command or "").strip(),
            args=[str(item) for item in (self.args or []) if str(item).strip()],
            cwd=(self.cwd or "").strip(),
            enabled_tools=_normalize_tool_names(self.enabled_tools),
            env={str(k): str(v) for k, v in (self.env or {}).items()},
            headers={str(k): str(v) for k, v in (self.headers or {}).items()},
            secret_refs={str(k): str(v) for k, v in (self.secret_refs or {}).items()},
            metadata=dict(self.metadata or {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "name": self.name,
            "description": self.description,
            "enabled": bool(self.enabled),
            "mode": self.mode,
            "transport": self.transport,
            "server_id": self.server_id,
            "endpoint": self.endpoint,
            "command": self.command,
            "args": list(self.args),
            "cwd": self.cwd,
            "enabled_tools": list(self.enabled_tools),
            "env": dict(self.env),
            "headers": dict(self.headers),
            "secret_refs": dict(self.secret_refs),
            "metadata": dict(self.metadata),
        }

    def to_api_dict(
        self,
        *,
        available_tools: Optional[List[Dict[str, Any]]] = None,
        active_tool_names: Optional[List[str]] = None,
        secret_slots: Optional[List[Dict[str, Any]]] = None,
        runtime_error: str = "",
    ) -> Dict[str, Any]:
        row = self.to_dict()
        row["available_tools"] = list(available_tools or [])
        row["active_tool_names"] = list(active_tool_names or [])
        row["secret_slots"] = list(secret_slots or [])
        row["runtime_error"] = str(runtime_error or "").strip()
        return row


@dataclass
class MCPToolBinding:
    client_id: str
    server_id: str
    mode: str
    tool_name: str
    description: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "server_id": self.server_id,
            "mode": self.mode,
            "tool_name": self.tool_name,
            "description": self.description,
        }


@dataclass
class MCPRuntimeSnapshot:
    discovered: List[MCPServerManifest] = field(default_factory=list)
    configured: List[object] = field(default_factory=list)
    active_clients: List[MCPClientConfig] = field(default_factory=list)
    active_tools: List[object] = field(default_factory=list)
    tool_bindings: List[MCPToolBinding] = field(default_factory=list)

    def discovered_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for item in self.discovered:
            if isinstance(item, dict):
                rows.append(dict(item))
            else:
                rows.append(item.to_dict())
        return rows

    def configured_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for item in self.configured:
            if isinstance(item, dict):
                rows.append(dict(item))
            else:
                rows.append(item.to_dict())
        return rows

    def tool_rows(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.tool_bindings]


def _normalize_tool_names(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    seen = set()
    rows: List[str] = []
    for item in value:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        rows.append(text)
        seen.add(text)
    return rows
