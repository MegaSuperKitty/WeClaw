# -*- coding: utf-8 -*-
"""Public retrieval engine API for WeClaw_console and future core integration."""

from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
import threading
from typing import Any, Dict, Optional

from .chunking import ChunkingConfig, TextChunker
from .embeddings import build_embedder
from .indexer import RetrievalIndexer
from .source_sessions import SessionSourceLoader
from .sqlite_store import SQLiteRetrievalStore
from .strategy_hybrid import HybridRetriever
from .strategy_keyword import KeywordRetriever
from .strategy_vector import VectorRetriever
from .types import EngineStatus, SearchResponse
from .watcher import DebouncedWatcher


class RetrievalEngine:
    """Facade exposing index lifecycle and search APIs."""

    def __init__(
        self,
        history_dir: str,
        data_dir: str,
        db_name: str = "session_memory.sqlite",
    ):
        self.history_dir = str(Path(history_dir).resolve())
        self.data_dir = str(Path(data_dir).resolve())
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        self.db_path = str(Path(self.data_dir) / db_name)

        self._lock = threading.Lock()
        self._indexing = False
        self._ready = False
        self._last_error = ""
        self._embedder_watch_stop = threading.Event()
        self._embedder_watch_thread: Optional[threading.Thread] = None

        self.source = SessionSourceLoader(self.history_dir)
        self.store = SQLiteRetrievalStore(self.db_path)
        self.embedder = build_embedder()
        self.chunking_config = self._resolve_chunking_config(self.embedder)
        self.chunker = TextChunker(self.chunking_config)
        self.indexer = RetrievalIndexer(
            source_loader=self.source,
            store=self.store,
            chunker=self.chunker,
            embedder=self.embedder,
        )
        self.keyword = KeywordRetriever(self.store)
        self.vector = VectorRetriever(self.store, self.embedder)
        self.hybrid = HybridRetriever(self.store, self.keyword, self.vector)

        self.watcher = DebouncedWatcher(
            list_files=lambda: self.source.iter_session_files(),
            on_debounced_change=self._watcher_reindex,
            poll_interval_seconds=1.0,
            debounce_seconds=1.5,
        )

    def start(self) -> Dict[str, Any]:
        """Start watcher and perform initial indexing."""
        last_embedder = self.store.get_meta("last_embedder", "")
        last_chunking = self.store.get_meta("last_chunking", "")
        chunking_changed = bool(last_chunking and last_chunking != self.chunking_config.signature())
        force = bool((last_embedder and last_embedder != self.embedder.name) or chunking_changed)
        self.reindex_now(force=force)
        self.watcher.start()
        self._start_embedder_watch()
        self._ready = True
        return self.status_dict()

    def stop(self) -> None:
        self._embedder_watch_stop.set()
        if self._embedder_watch_thread and self._embedder_watch_thread.is_alive():
            self._embedder_watch_thread.join(timeout=1.0)
        self.watcher.stop()
        self.store.close()

    def reindex_now(self, force: bool = False) -> Dict[str, Any]:
        with self._lock:
            self._indexing = True
            try:
                stats = self.indexer.sync_once(force=force)
                self._last_error = stats.last_error or ""
                return asdict(stats)
            except Exception as exc:
                self._last_error = str(exc)
                raise
            finally:
                self._indexing = False

    def search_sessions(
        self,
        query: str,
        limit: int = 20,
        channel_prefix: str = "",
        user_id: str = "",
    ) -> SearchResponse:
        return self.hybrid.search_sessions(
            query=query,
            limit=limit,
            channel_prefix=channel_prefix,
            user_id=user_id,
        )

    def status(self) -> EngineStatus:
        return EngineStatus(
            ready=self._ready,
            indexing=self._indexing,
            last_indexed_at=self.store.get_meta("last_indexed_at", ""),
            embedder=self.embedder.name,
            db_path=self.db_path,
            chunks=self.store.count_chunks(),
            files=self.store.count_files(),
            watcher_running=self.watcher.running,
            last_error=self._last_error or self.store.get_meta("last_index_error", ""),
            extra={
                "history_dir": self.history_dir,
                "fts_enabled": str(self.store.fts_enabled).lower(),
                "vector_enabled": str(not getattr(self.vector, "_disabled", False)).lower(),
                "chunk_target_tokens": str(self.chunking_config.target_tokens),
                "chunk_overlap_tokens": str(self.chunking_config.overlap_tokens),
                "chunk_chars_per_token": f"{self.chunking_config.chars_per_token:.2f}",
            },
        )

    def status_dict(self) -> Dict[str, Any]:
        return asdict(self.status())

    def _watcher_reindex(self) -> None:
        try:
            self.reindex_now(force=False)
        except Exception as exc:
            self._last_error = str(exc)

    def _start_embedder_watch(self) -> None:
        if self._embedder_watch_thread and self._embedder_watch_thread.is_alive():
            return
        self._embedder_watch_stop.clear()
        self._embedder_watch_thread = threading.Thread(
            target=self._embedder_watch_loop,
            name="retrieval-embedder-watch",
            daemon=True,
        )
        self._embedder_watch_thread.start()

    def _embedder_watch_loop(self) -> None:
        while not self._embedder_watch_stop.wait(2.0):
            try:
                if self._indexing:
                    continue
                current = str(getattr(self.embedder, "name", "") or "")
                last = self.store.get_meta("last_embedder", "")
                # Embedder upgraded (e.g. hash -> sentence-transformers):
                # force a full reindex so stored vectors match query vectors.
                if current and last and current != last:
                    self.reindex_now(force=True)
            except Exception as exc:
                self._last_error = str(exc)

    def _resolve_chunking_config(self, embedder) -> ChunkingConfig:
        env_target = self._parse_int_env("RETRIEVAL_CHUNK_TARGET_TOKENS")
        env_overlap = self._parse_int_env("RETRIEVAL_CHUNK_OVERLAP_TOKENS")
        env_cpt = self._parse_float_env("RETRIEVAL_CHARS_PER_TOKEN")

        recommended = None
        if hasattr(embedder, "recommended_max_tokens"):
            try:
                recommended = embedder.recommended_max_tokens()
            except Exception:
                recommended = None

        target_tokens = env_target or recommended or 400
        target_tokens = max(32, int(target_tokens))

        default_overlap = max(8, int(target_tokens * 0.2))
        overlap_tokens = env_overlap if env_overlap is not None else default_overlap
        overlap_tokens = max(0, min(int(overlap_tokens), max(0, target_tokens - 1)))

        chars_per_token = env_cpt if env_cpt is not None else 1.8
        if chars_per_token <= 0:
            chars_per_token = 1.8

        return ChunkingConfig(
            target_tokens=target_tokens,
            overlap_tokens=overlap_tokens,
            chars_per_token=chars_per_token,
        )

    def _parse_int_env(self, key: str):
        raw = os.getenv(key, "").strip()
        if not raw:
            return None
        try:
            return int(raw)
        except Exception:
            return None

    def _parse_float_env(self, key: str):
        raw = os.getenv(key, "").strip()
        if not raw:
            return None
        try:
            return float(raw)
        except Exception:
            return None
