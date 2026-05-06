# -*- coding: utf-8 -*-
"""Fetch a web page and extract plain text (no JS execution)."""

from __future__ import annotations

from html.parser import HTMLParser
import ipaddress
import urllib.parse
import urllib.request

from integrations.mcp.openai_tool import Tool


class WebFetchTool(Tool):
    def __init__(self):
        super().__init__(
            name="web_fetch",
            description="Fetch a web page and extract text (no JS execution).",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch (http/https)."},
                    "max_chars": {"type": "integer", "description": "Maximum chars to return."},
                },
                "required": ["url"],
            },
        )

    def _execute(self, **kwargs):
        url = (kwargs.get("url") or "").strip()
        max_chars = int(kwargs.get("max_chars") or 5000)
        if not _is_safe_url(url):
            return "url is not allowed."
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return "failed to fetch url."
        text = _html_to_text(html)[:max_chars].strip()
        return text or "no text extracted."


def _is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname or ""
    if not host or host.lower() == "localhost":
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        pass
    return True


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data):
        if data:
            self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return " ".join(parser.get_text().split())
