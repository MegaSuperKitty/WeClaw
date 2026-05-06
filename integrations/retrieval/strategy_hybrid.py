# -*- coding: utf-8 -*-
"""Hybrid retrieval (keyword + vector)."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from .sqlite_store import SQLiteRetrievalStore
from .strategy_keyword import KeywordRetriever
from .strategy_vector import VectorRetriever
from .types import SearchHit, SearchResponse, SearchSessionHit
from .utils import normalize_preview


class HybridRetriever:
    """Merge keyword and vector retrieval then group by session."""

    def __init__(
        self,
        store: SQLiteRetrievalStore,
        keyword: KeywordRetriever,
        vector: VectorRetriever,
        keyword_weight: float = 0.58,
        vector_weight: float = 0.42,
    ):
        self.store = store
        self.keyword = keyword
        self.vector = vector
        self.keyword_weight = float(keyword_weight)
        self.vector_weight = float(vector_weight)

    def search_sessions(
        self,
        query: str,
        limit: int = 20,
        channel_prefix: str = "",
        user_id: str = "",
    ) -> SearchResponse:
        import time

        start = time.perf_counter()

        q = str(query or "").strip()
        top = max(1, int(limit))
        if not q:
            return SearchResponse(query="", limit=top, total_sessions=0, session_hits=[], elapsed_ms=0)

        keyword_hits = self.keyword.search(q, limit=max(60, top * 8))
        vector_hits = self.vector.search(q, limit=max(60, top * 8))

        by_chunk: Dict[str, SearchHit] = {}
        for hit in keyword_hits:
            row = by_chunk.setdefault(
                hit.chunk_id,
                SearchHit(
                    chunk_id=hit.chunk_id,
                    user_id="",
                    session_name="",
                    channel_prefix="unknown",
                    file_path="",
                    preview=hit.snippet,
                    role="",
                ),
            )
            row.keyword_score = max(row.keyword_score, float(hit.score))
            if "keyword" not in row.matched_by:
                row.matched_by.append("keyword")

        for hit in vector_hits:
            row = by_chunk.setdefault(
                hit.chunk_id,
                SearchHit(
                    chunk_id=hit.chunk_id,
                    user_id="",
                    session_name="",
                    channel_prefix="unknown",
                    file_path="",
                    preview="",
                    role="",
                ),
            )
            row.vector_score = max(row.vector_score, float(hit.score))
            if "vector" not in row.matched_by:
                row.matched_by.append("vector")

        chunks = self.store.fetch_chunks_by_ids(list(by_chunk.keys()))
        merged: List[SearchHit] = []
        filter_channel = (channel_prefix or "").strip().lower()
        filter_user = (user_id or "").strip()
        for chunk_id, row in by_chunk.items():
            chunk = chunks.get(chunk_id)
            if not chunk:
                continue
            if filter_channel and chunk.channel_prefix.lower() != filter_channel:
                continue
            if filter_user and chunk.user_id != filter_user:
                continue

            row.user_id = chunk.user_id
            row.session_name = chunk.session_name
            row.channel_prefix = chunk.channel_prefix
            row.file_path = chunk.file_path
            row.role = chunk.role
            if not row.preview:
                row.preview = chunk.preview
            row.final_score = row.keyword_score * self.keyword_weight + row.vector_score * self.vector_weight
            if row.final_score <= 0.0:
                continue
            merged.append(row)

        merged.sort(key=lambda item: item.final_score, reverse=True)

        grouped = self._group_by_session(merged)
        session_hits = grouped[:top]

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return SearchResponse(
            query=q,
            limit=top,
            total_sessions=len(grouped),
            session_hits=session_hits,
            elapsed_ms=elapsed_ms,
        )

    def _group_by_session(self, rows: Sequence[SearchHit]) -> List[SearchSessionHit]:
        best_by_session: Dict[Tuple[str, str], SearchHit] = {}
        for row in rows:
            key = (row.user_id, row.session_name)
            prev = best_by_session.get(key)
            if prev is None or row.final_score > prev.final_score:
                best_by_session[key] = row

        out: List[SearchSessionHit] = []
        for key, row in best_by_session.items():
            out.append(
                SearchSessionHit(
                    user_id=key[0],
                    session_name=key[1],
                    channel_prefix=row.channel_prefix,
                    file_path=row.file_path,
                    score=row.final_score,
                    preview=normalize_preview(row.preview, max_chars=260),
                    role=row.role,
                    matched_by=list(row.matched_by),
                    source_chunk_id=row.chunk_id,
                    metadata={
                        "keyword_score": f"{row.keyword_score:.4f}",
                        "vector_score": f"{row.vector_score:.4f}",
                        "final_score": f"{row.final_score:.4f}",
                    },
                )
            )
        out.sort(key=lambda row: row.score, reverse=True)
        return out
