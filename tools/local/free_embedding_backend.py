# -*- coding: utf-8 -*-
"""Free text embedding backend adapter backed by retrieval integration."""

from __future__ import annotations

from typing import Dict, List

from integrations.retrieval.embeddings import build_embedder


class FreeEmbeddingBackend:
    """Reuse retrieval embedding backends for MCP text embedding."""

    def __init__(self):
        self._embedder = build_embedder()

    def embed_text(self, text: str) -> Dict[str, object]:
        vector: List[float] = list(self._embedder.embed_query(text) or [])
        if not vector:
            raise ValueError("embedding_empty")
        return {"embedding": vector, "model": getattr(self._embedder, "name", "retrieval_embedder") or "retrieval_embedder"}
