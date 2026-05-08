# -*- coding: utf-8 -*-
"""Extract quotable snippets from input text."""

from __future__ import annotations

from typing import List
import re

from integrations.mcp.openai_tool import Tool


class QuoteExtractTool(Tool):
    """Extract key quote snippets from plain text."""

    def __init__(self):
        super().__init__(
            name="quote_extract",
            description="Extract key quotes/snippets from a text for citation.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input text."},
                    "max_quotes": {"type": "integer", "description": "Maximum number of quotes."},
                    "max_chars": {"type": "integer", "description": "Maximum chars per quote."},
                },
                "required": ["text"],
            },
        )

    def _execute(self, **kwargs):
        text = (kwargs.get("text") or "").strip()
        if not text:
            return "no text to extract quotes from."
        max_quotes = int(kwargs.get("max_quotes") or 5)
        max_chars = int(kwargs.get("max_chars") or 220)
        sentences = _split_sentences(text)
        quotes: list[str] = []
        for sentence in sentences:
            snippet = sentence.strip()
            if not snippet:
                continue
            if len(snippet) > max_chars:
                snippet = snippet[: max_chars].rstrip() + "..."
            quotes.append(snippet)
            if len(quotes) >= max_quotes:
                break
        if not quotes:
            return "no quote snippets found."
        return "\n".join(f"- {quote}" for quote in quotes)


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[。！？!?])\s+", text)
    if len(parts) == 1:
        parts = text.splitlines()
    return [part.strip() for part in parts if part.strip()]
