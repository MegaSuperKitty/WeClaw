# -*- coding: utf-8 -*-
"""SQLite persistence for retrieval index."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import threading
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .types import KeywordHit, SourceChunk
from .utils import now_iso, safe_json_loads


class SQLiteRetrievalStore:
    """Thin storage layer for chunks, embeddings, metadata and FTS."""

    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).resolve())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._fts_enabled = True
        self._ensure_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _ensure_schema(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
              chunk_id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              session_name TEXT NOT NULL,
              channel_prefix TEXT NOT NULL,
              file_path TEXT NOT NULL,
              role TEXT NOT NULL,
              chunk_text TEXT NOT NULL,
              preview TEXT NOT NULL,
              start_pos INTEGER NOT NULL,
              end_pos INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              content_hash TEXT NOT NULL
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_session ON chunks(user_id, session_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(file_path)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_updated ON chunks(updated_at)")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
              chunk_id TEXT PRIMARY KEY,
              model TEXT NOT NULL,
              vector_json TEXT NOT NULL,
              FOREIGN KEY(chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS file_state (
              file_path TEXT PRIMARY KEY,
              mtime REAL NOT NULL,
              size INTEGER NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            )
            """
        )

        try:
            cur.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                  chunk_id UNINDEXED,
                  chunk_text
                )
                """
            )
        except sqlite3.OperationalError:
            self._fts_enabled = False
        self._conn.commit()

    @property
    def fts_enabled(self) -> bool:
        return self._fts_enabled

    def get_file_state(self) -> Dict[str, Tuple[float, int]]:
        with self._lock:
            cur = self._conn.execute("SELECT file_path, mtime, size FROM file_state")
            rows = cur.fetchall()
        return {str(r["file_path"]): (float(r["mtime"]), int(r["size"])) for r in rows}

    def upsert_file_chunks(
        self,
        file_path: str,
        mtime: float,
        size: int,
        chunks: Sequence[SourceChunk],
        vectors: Sequence[Sequence[float]],
        embedding_model: str,
    ) -> int:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM embeddings WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE file_path = ?)", (file_path,))
            if self._fts_enabled:
                cur.execute("DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE file_path = ?)", (file_path,))
            cur.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))

            for idx, chunk in enumerate(chunks):
                cur.execute(
                    """
                    INSERT OR REPLACE INTO chunks (
                      chunk_id, user_id, session_name, channel_prefix, file_path, role,
                      chunk_text, preview, start_pos, end_pos, updated_at, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk.chunk_id,
                        chunk.user_id,
                        chunk.session_name,
                        chunk.channel_prefix,
                        chunk.file_path,
                        chunk.role,
                        chunk.chunk_text,
                        chunk.preview,
                        int(chunk.start_pos),
                        int(chunk.end_pos),
                        int(chunk.updated_at),
                        chunk.content_hash,
                    ),
                )
                if self._fts_enabled:
                    cur.execute(
                        "INSERT INTO chunks_fts (chunk_id, chunk_text) VALUES (?, ?)",
                        (chunk.chunk_id, chunk.chunk_text),
                    )

                if idx < len(vectors):
                    vec_json = json.dumps(list(vectors[idx]), ensure_ascii=False, separators=(",", ":"))
                    cur.execute(
                        "INSERT OR REPLACE INTO embeddings (chunk_id, model, vector_json) VALUES (?, ?, ?)",
                        (chunk.chunk_id, embedding_model, vec_json),
                    )

            cur.execute(
                "INSERT OR REPLACE INTO file_state (file_path, mtime, size, updated_at) VALUES (?, ?, ?, ?)",
                (file_path, float(mtime), int(size), now_iso()),
            )
            self._conn.commit()
            return len(chunks)

    def remove_deleted_files(self, alive_files: Iterable[str]) -> int:
        alive = {str(x) for x in alive_files}
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT file_path FROM file_state")
            known = {str(r["file_path"]) for r in cur.fetchall()}
            deleted = sorted(known - alive)
            for file_path in deleted:
                cur.execute("DELETE FROM embeddings WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE file_path = ?)", (file_path,))
                if self._fts_enabled:
                    cur.execute("DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE file_path = ?)", (file_path,))
                cur.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))
                cur.execute("DELETE FROM file_state WHERE file_path = ?", (file_path,))
            self._conn.commit()
        return len(deleted)

    def keyword_search(self, query: str, limit: int = 80) -> List[KeywordHit]:
        q = str(query or "").strip()
        if not q:
            return []

        with self._lock:
            if self._fts_enabled:
                try:
                    cur = self._conn.execute(
                        """
                        SELECT f.chunk_id AS chunk_id,
                               bm25(chunks_fts) AS bm25_score,
                               c.preview AS preview
                          FROM chunks_fts f
                          JOIN chunks c ON c.chunk_id = f.chunk_id
                         WHERE chunks_fts MATCH ?
                         ORDER BY bm25_score ASC
                         LIMIT ?
                        """,
                        (q, int(limit)),
                    )
                    rows = cur.fetchall()
                    hits: List[KeywordHit] = []
                    for row in rows:
                        # bm25 smaller => better. Convert to larger-is-better score.
                        raw = float(row["bm25_score"])
                        score = 1.0 / (1.0 + max(0.0, raw))
                        hits.append(KeywordHit(chunk_id=str(row["chunk_id"]), score=score, snippet=str(row["preview"])))
                    return hits
                except sqlite3.OperationalError:
                    # fallback below
                    pass

            like = f"%{q.lower()}%"
            cur = self._conn.execute(
                """
                SELECT chunk_id, preview
                  FROM chunks
                 WHERE lower(chunk_text) LIKE ?
                 ORDER BY updated_at DESC
                 LIMIT ?
                """,
                (like, int(limit)),
            )
            rows = cur.fetchall()
        return [KeywordHit(chunk_id=str(r["chunk_id"]), score=0.5, snippet=str(r["preview"])) for r in rows]

    def fetch_chunks_by_ids(self, chunk_ids: Sequence[str]) -> Dict[str, SourceChunk]:
        ids = [str(x) for x in chunk_ids if str(x).strip()]
        if not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        with self._lock:
            cur = self._conn.execute(
                f"""
                SELECT chunk_id, user_id, session_name, channel_prefix, file_path, role,
                       chunk_text, preview, start_pos, end_pos, updated_at, content_hash
                  FROM chunks
                 WHERE chunk_id IN ({placeholders})
                """,
                ids,
            )
            rows = cur.fetchall()

        out: Dict[str, SourceChunk] = {}
        for row in rows:
            chunk = SourceChunk(
                chunk_id=str(row["chunk_id"]),
                user_id=str(row["user_id"]),
                session_name=str(row["session_name"]),
                channel_prefix=str(row["channel_prefix"]),
                file_path=str(row["file_path"]),
                role=str(row["role"]),
                chunk_text=str(row["chunk_text"]),
                preview=str(row["preview"]),
                start_pos=int(row["start_pos"]),
                end_pos=int(row["end_pos"]),
                updated_at=int(row["updated_at"]),
                content_hash=str(row["content_hash"]),
            )
            out[chunk.chunk_id] = chunk
        return out

    def iter_embeddings(self) -> Iterable[Tuple[str, List[float]]]:
        with self._lock:
            cur = self._conn.execute("SELECT chunk_id, vector_json FROM embeddings")
            rows = cur.fetchall()
        for row in rows:
            vec = safe_json_loads(str(row["vector_json"]))
            if isinstance(vec, list):
                try:
                    yield str(row["chunk_id"]), [float(x) for x in vec]
                except Exception:
                    continue

    def set_meta(self, key: str, value: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (str(key), str(value)),
            )
            self._conn.commit()

    def get_meta(self, key: str, default: str = "") -> str:
        with self._lock:
            cur = self._conn.execute("SELECT value FROM metadata WHERE key = ?", (str(key),))
            row = cur.fetchone()
        if row is None:
            return default
        return str(row["value"])

    def count_chunks(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(1) AS n FROM chunks")
            row = cur.fetchone()
        return int(row["n"] if row else 0)

    def count_files(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(1) AS n FROM file_state")
            row = cur.fetchone()
        return int(row["n"] if row else 0)
