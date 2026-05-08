# -*- coding: utf-8 -*-
"""Local embedding backends for vector retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import threading
from typing import Iterable, List, Optional

from .types import EmbeddingConfig
from .utils import ensure_list_of_floats


class EmbeddingBackend:
    """Interface for embedding generation."""

    name = "base"

    def embed(self, texts: Iterable[str]) -> List[List[float]]:  # pragma: no cover - interface
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        rows = self.embed([text])
        return rows[0] if rows else []

    def recommended_max_tokens(self) -> Optional[int]:
        """Suggested max chunk tokens for this embedder."""
        return None


@dataclass
class HashEmbeddingBackend(EmbeddingBackend):
    """Deterministic local embedding fallback (no external model)."""

    dimensions: int = 256
    name: str = "hash-v1"

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for text in texts:
            out.append(self._one(text))
        return out

    def _one(self, text: str) -> List[float]:
        raw = (text or "").encode("utf-8")
        seed = hashlib.sha256(raw).digest()
        vector: List[float] = []
        idx = 0
        while len(vector) < self.dimensions:
            b = seed[idx % len(seed)]
            value = (float(b) / 255.0) * 2.0 - 1.0
            vector.append(value)
            idx += 1
            if idx % len(seed) == 0:
                seed = hashlib.sha256(seed + raw).digest()
        return vector


class SentenceTransformerBackend(EmbeddingBackend):
    """Local embedding via sentence-transformers models."""

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
    ):
        self.model_name = model_name
        self.device = (device or "cpu").strip() or "cpu"
        self.batch_size = max(1, int(batch_size or 32))
        self.normalize = bool(normalize)
        self.name = f"sentence-transformers:{model_name}"

        try:
            from sentence_transformers import SentenceTransformer
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError("sentence-transformers package not available") from exc

        self._model = SentenceTransformer(model_name, device=self.device)
        self.max_seq_length = int(getattr(self._model, "max_seq_length", 0) or 0)

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        items = [str(x or "") for x in texts]
        if not items:
            return []

        vectors = self._model.encode(
            items,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize,
        )
        # sentence-transformers may return 1-D for a single item.
        if hasattr(vectors, "ndim") and int(getattr(vectors, "ndim", 0)) == 1:
            vectors = [vectors]

        out: List[List[float]] = []
        for row in vectors:
            if hasattr(row, "tolist"):
                row = row.tolist()
            out.append(ensure_list_of_floats(row))
        return out

    def recommended_max_tokens(self) -> Optional[int]:
        if self.max_seq_length <= 0:
            return None
        # Reserve room for special tokens; keep chunks below truncation line.
        target = int(self.max_seq_length * 0.75)
        return max(48, min(384, target))


class AsyncSentenceTransformerBackend(EmbeddingBackend):
    """Non-blocking sentence-transformers backend with hash fallback."""

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
    ):
        self.model_name = model_name
        self.device = (device or "cpu").strip() or "cpu"
        self.batch_size = max(1, int(batch_size or 32))
        self.normalize = bool(normalize)

        self._fallback = HashEmbeddingBackend()
        self._active: EmbeddingBackend = self._fallback
        self._lock = threading.Lock()
        self._loading = True
        self._last_error = ""
        self.name = self._fallback.name

        self._loader = threading.Thread(target=self._load_model, name="retrieval-embed-loader", daemon=True)
        self._loader.start()

    def _load_model(self) -> None:
        try:
            backend = SentenceTransformerBackend(
                model_name=self.model_name,
                device=self.device,
                batch_size=self.batch_size,
                normalize=self.normalize,
            )
            with self._lock:
                self._active = backend
                self.name = backend.name
                self._last_error = ""
        except Exception as exc:
            with self._lock:
                self._last_error = str(exc)
        finally:
            self._loading = False

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        with self._lock:
            backend = self._active
        return backend.embed(texts)

    def recommended_max_tokens(self) -> Optional[int]:
        with self._lock:
            backend = self._active
        return backend.recommended_max_tokens()

    def loading(self) -> bool:
        return bool(self._loading)

    def last_error(self) -> str:
        return self._last_error


def build_embedding_config_from_env() -> EmbeddingConfig:
    provider = os.getenv("RETRIEVAL_EMBED_PROVIDER", "sentence_transformers").strip().lower() or "sentence_transformers"
    model = os.getenv("RETRIEVAL_EMBED_MODEL", "").strip() or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    device = os.getenv("RETRIEVAL_EMBED_DEVICE", "").strip() or "cpu"
    batch_size_raw = os.getenv("RETRIEVAL_EMBED_BATCH_SIZE", "").strip()
    normalize_raw = os.getenv("RETRIEVAL_EMBED_NORMALIZE", "").strip().lower()
    dim_raw = os.getenv("RETRIEVAL_EMBED_DIMENSIONS", "").strip()

    batch_size = int(batch_size_raw) if batch_size_raw.isdigit() else 32
    normalize = normalize_raw not in {"0", "false", "no", "off"}
    dimensions = int(dim_raw) if dim_raw.isdigit() else None
    return EmbeddingConfig(
        provider=provider,
        model=model,
        dimensions=dimensions,
        device=device,
        batch_size=batch_size,
        normalize=normalize,
    )


def build_embedder(config: Optional[EmbeddingConfig] = None) -> EmbeddingBackend:
    cfg = config or build_embedding_config_from_env()
    provider = (cfg.provider or "sentence_transformers").strip().lower()
    async_bootstrap = os.getenv("RETRIEVAL_EMBED_ASYNC_BOOTSTRAP", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }

    if provider in {"sentence_transformers", "sentence-transformers", "st", "local", "auto"}:
        if async_bootstrap:
            return AsyncSentenceTransformerBackend(
                model_name=cfg.model,
                device=cfg.device,
                batch_size=cfg.batch_size,
                normalize=cfg.normalize,
            )
        try:
            return SentenceTransformerBackend(
                model_name=cfg.model,
                device=cfg.device,
                batch_size=cfg.batch_size,
                normalize=cfg.normalize,
            )
        except Exception:
            pass
    return HashEmbeddingBackend()
