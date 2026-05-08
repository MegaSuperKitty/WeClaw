# -*- coding: utf-8 -*-
"""Load and budget MEMORY.md content for prompt injection."""

from __future__ import annotations

from pathlib import Path


DEFAULT_MEMORY_PROMPT_CHAR_BUDGET = 4000


def load_memory_for_prompt(memory_path: str, max_chars: int = DEFAULT_MEMORY_PROMPT_CHAR_BUDGET) -> str:
    """Read MEMORY.md and keep the tail when prompt budget is exceeded."""
    text = Path(memory_path).read_text(encoding="utf-8")
    budget = max(1, int(max_chars or DEFAULT_MEMORY_PROMPT_CHAR_BUDGET))
    if len(text) <= budget:
        return text
    tail = text[-budget:]
    marker = "[Earlier memory omitted; keeping the newest tail section for prompt budget.]\n\n"
    allowed_tail = max(1, budget - len(marker))
    return marker + tail[-allowed_tail:]
