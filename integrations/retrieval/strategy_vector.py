# -*- coding: utf-8 -*-
"""Vector retrieval strategy."""

from __future__ import annotations

from typing import List

from .embeddings import EmbeddingBackend
from .sqlite_store import SQLiteRetrievalStore
from .types import VectorHit
from .utils import cosine_similarity


class VectorRetriever:
    """Cosine-similarity retrieval over stored embeddings."""

    def __init__(self, store: SQLiteRetrievalStore, embedder: EmbeddingBackend):
        self.store = store
        self.embedder = embedder
        self._disabled = False

    def search(self, query: str, limit: int = 80) -> List[VectorHit]:
        if self._disabled:
            return []
        text = str(query or "").strip()
        if not text:
            return []

        try:
            query_vector = self.embedder.embed_query(text)
        except Exception:
            self._disabled = True
            return []
        if not query_vector:
            return []

        scored: List[VectorHit] = []
        for chunk_id, vector in self.store.iter_embeddings():
            score = cosine_similarity(query_vector, vector)
            if score <= 0.0:
                continue
            scored.append(VectorHit(chunk_id=chunk_id, score=score))
        scored.sort(key=lambda row: row.score, reverse=True)
        return scored[: max(1, int(limit))]
