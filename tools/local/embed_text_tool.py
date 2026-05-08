# -*- coding: utf-8 -*-
"""Text embedding MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.free_embedding_backend import FreeEmbeddingBackend
from tools.local.model_tool_utils import build_openai_client, resolve_model_backend, safe_text


class EmbedTextTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="embed_text",
            description="Create a text embedding with the active text-embedding model.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to embed."},
                },
                "required": ["text"],
            },
        )

    def _execute(self, **kwargs):
        text = safe_text(kwargs.get("text"))
        if not text:
            raise ValueError("text is required")
        backend = resolve_model_backend(self.project_root, "text_embedding")
        if backend.mode == "free_fallback":
            free_backend = FreeEmbeddingBackend()
            return free_backend.embed_text(text)
        client, profile = build_openai_client(self.project_root, "text_embedding")
        response = client.embeddings.create(model=profile.model, input=text)
        data_rows = getattr(response, "data", None) or []
        if not data_rows:
            raise ValueError("embedding_empty")
        return {"embedding": list(getattr(data_rows[0], "embedding", []) or []), "model": profile.model}
