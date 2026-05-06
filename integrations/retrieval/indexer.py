# -*- coding: utf-8 -*-
"""Incremental index builder."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from .chunking import TextChunker
from .embeddings import EmbeddingBackend
from .source_sessions import SessionSourceLoader
from .sqlite_store import SQLiteRetrievalStore
from .types import IndexStats, SourceChunk
from .utils import normalize_preview, now_iso, parse_int_like, sha1_text


class RetrievalIndexer:
    """Build/update index from chat session files."""

    def __init__(
        self,
        source_loader: SessionSourceLoader,
        store: SQLiteRetrievalStore,
        chunker: TextChunker,
        embedder: EmbeddingBackend,
    ):
        self.source_loader = source_loader
        self.store = store
        self.chunker = chunker
        self.embedder = embedder
        self._embedding_disabled = False

    def sync_once(self, force: bool = False) -> IndexStats:
        stats = IndexStats()
        known_state = self.store.get_file_state()
        alive_files: List[str] = []

        for path in self.source_loader.iter_session_files():
            fp = self.source_loader.build_fingerprint(path)
            if not fp:
                stats.errors += 1
                continue
            stats.scanned_files += 1
            alive_files.append(fp.file_path)

            cached = known_state.get(fp.file_path)
            unchanged = (not force) and cached and abs(cached[0] - fp.mtime) < 1e-6 and int(cached[1]) == int(fp.size)
            if unchanged:
                stats.skipped_files += 1
                continue

            try:
                chunks = self._build_chunks(path)
                vectors = []
                if chunks and not self._embedding_disabled:
                    try:
                        vectors = self.embedder.embed([c.chunk_text for c in chunks])
                    except Exception:
                        # Keep index usable even when embedding provider fails.
                        vectors = []
                        self._embedding_disabled = True
                written = self.store.upsert_file_chunks(
                    file_path=fp.file_path,
                    mtime=fp.mtime,
                    size=fp.size,
                    chunks=chunks,
                    vectors=vectors,
                    embedding_model=self.embedder.name,
                )
                stats.indexed_files += 1
                stats.chunks_written += int(written)
            except Exception as exc:
                stats.errors += 1
                stats.last_error = str(exc)

        stats.deleted_files = self.store.remove_deleted_files(alive_files)
        self.store.set_meta("last_indexed_at", now_iso())
        self.store.set_meta("last_embedder", self.embedder.name)
        self.store.set_meta("last_chunking", self.chunker.config.signature())
        self.store.set_meta("last_index_stats", self._stats_text(stats))
        if stats.last_error:
            self.store.set_meta("last_index_error", stats.last_error)
        return stats

    def _build_chunks(self, path: Path) -> List[SourceChunk]:
        doc = self.source_loader.load_document(path)
        if not doc:
            return []

        chunks: List[SourceChunk] = []
        for record in doc.messages:
            text = str(record.text or "").strip()
            if not text:
                continue
            spans = self.chunker.split(text)
            for span in spans:
                chunk_text = span.text
                chunk_id = self._chunk_id(doc.file_path, record.message_index, record.role, span.start, chunk_text)
                chunks.append(
                    SourceChunk(
                        chunk_id=chunk_id,
                        user_id=doc.user_id,
                        session_name=doc.session_name,
                        channel_prefix=doc.channel_prefix,
                        file_path=doc.file_path,
                        role=record.role,
                        chunk_text=chunk_text,
                        preview=normalize_preview(chunk_text, max_chars=260),
                        start_pos=span.start,
                        end_pos=span.end,
                        updated_at=doc.updated_at or parse_int_like(doc.updated_at_text, 0),
                        content_hash=sha1_text(chunk_text),
                    )
                )
        return chunks

    def _chunk_id(self, file_path: str, msg_index: int, role: str, start: int, text: str) -> str:
        token = f"{file_path}|{msg_index}|{role}|{start}|{sha1_text(text)}"
        return sha1_text(token)

    def _stats_text(self, stats: IndexStats) -> str:
        return (
            f"scanned={stats.scanned_files}; indexed={stats.indexed_files}; skipped={stats.skipped_files}; "
            f"deleted={stats.deleted_files}; chunks={stats.chunks_written}; errors={stats.errors}"
        )
