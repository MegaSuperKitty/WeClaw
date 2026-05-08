# -*- coding: utf-8 -*-
"""Keyword retrieval strategy."""

from __future__ import annotations

from typing import List

from .sqlite_store import SQLiteRetrievalStore
from .types import KeywordHit


class KeywordRetriever:
    """BM25/FTS5 based keyword search with fallback."""

    def __init__(self, store: SQLiteRetrievalStore):
        self.store = store

    def search(self, query: str, limit: int = 80) -> List[KeywordHit]:
        return self.store.keyword_search(query, limit=limit)
