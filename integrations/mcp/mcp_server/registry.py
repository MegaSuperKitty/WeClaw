# -*- coding: utf-8 -*-
"""Registry of built-in local MCP servers."""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BaseLocalMCPServer
from .builtin_servers import (
    AgentMCPServer,
    BrowserMCPServer,
    BraveSearchMCPServer,
    EmbeddingModelsMCPServer,
    FilesystemMCPServer,
    GenerationModelsMCPServer,
    ResearchMCPServer,
    SkillsMCPServer,
    SpeechModelsMCPServer,
    SystemMCPServer,
    VisionModelsMCPServer,
)


_SERVER_TYPES: List[Type[BaseLocalMCPServer]] = [
    FilesystemMCPServer,
    SystemMCPServer,
    BrowserMCPServer,
    VisionModelsMCPServer,
    GenerationModelsMCPServer,
    SpeechModelsMCPServer,
    EmbeddingModelsMCPServer,
    ResearchMCPServer,
    SkillsMCPServer,
    AgentMCPServer,
    BraveSearchMCPServer,
]


def list_server_instances() -> List[BaseLocalMCPServer]:
    return [server_type() for server_type in _SERVER_TYPES]


def list_server_manifests():
    return [server.get_manifest() for server in list_server_instances()]


def get_server(server_id: str) -> Optional[BaseLocalMCPServer]:
    normalized = str(server_id or "").strip()
    if not normalized:
        return None
    by_id: Dict[str, BaseLocalMCPServer] = {server.get_manifest().server_id: server for server in list_server_instances()}
    return by_id.get(normalized)
