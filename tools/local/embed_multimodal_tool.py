# -*- coding: utf-8 -*-
"""Multimodal embedding MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.model_tool_utils import build_openai_client, safe_text


class EmbedMultimodalTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="embed_multimodal",
            description="Create a multimodal embedding when the provider supports it.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Optional text input."},
                },
            },
        )

    def _execute(self, **kwargs):
        text = safe_text(kwargs.get("text"))
        if not text:
            raise ValueError("text is required")
        _, profile = build_openai_client(self.project_root, "multimodal_embedding")
        raise ValueError(f"multimodal_embedding_not_implemented_for_provider:{profile.provider}")
