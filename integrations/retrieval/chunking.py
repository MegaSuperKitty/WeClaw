# -*- coding: utf-8 -*-
"""Chunking primitives used by indexer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .types import ChunkSpan


@dataclass
class ChunkingConfig:
    """Approximate token chunking config."""

    target_tokens: int = 400
    overlap_tokens: int = 80
    chars_per_token: float = 1.8

    @property
    def target_chars(self) -> int:
        return max(120, int(self.target_tokens * self.chars_per_token))

    @property
    def overlap_chars(self) -> int:
        return max(0, int(self.overlap_tokens * self.chars_per_token))

    def signature(self) -> str:
        return f"target={self.target_tokens};overlap={self.overlap_tokens};cpt={self.chars_per_token:.3f}"


class TextChunker:
    """Split long text into overlapping spans."""

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    def split(self, text: str) -> List[ChunkSpan]:
        raw = str(text or "")
        if not raw.strip():
            return []

        target = self.config.target_chars
        overlap = min(self.config.overlap_chars, max(0, target - 1))
        step = max(1, target - overlap)

        spans: List[ChunkSpan] = []
        start = 0
        n = len(raw)
        while start < n:
            end = min(n, start + target)
            if end < n:
                # Prefer a nearby natural boundary to keep snippets readable.
                boundary = self._find_boundary(raw, start, end)
                if boundary > start + int(target * 0.55):
                    end = boundary
            chunk = raw[start:end].strip()
            if chunk:
                spans.append(ChunkSpan(start=start, end=end, text=chunk))
            if end >= n:
                break
            start = end - overlap
        return spans

    def _find_boundary(self, text: str, start: int, end: int) -> int:
        window = text[start:end]
        candidates = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", "，", ","]
        best = -1
        for mark in candidates:
            idx = window.rfind(mark)
            if idx > best:
                best = idx
        if best < 0:
            return end
        return start + best + 1
