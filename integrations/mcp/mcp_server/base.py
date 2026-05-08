# -*- coding: utf-8 -*-
"""Base primitives for local MCP server registration."""

from __future__ import annotations

from typing import List

from integrations.mcp.schema import MCPServerManifest


class BaseLocalMCPServer:
    """Base class for local MCP server providers."""

    manifest: MCPServerManifest

    def get_manifest(self) -> MCPServerManifest:
        return self.manifest

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        raise NotImplementedError("Local MCP servers must implement build_tools().")
