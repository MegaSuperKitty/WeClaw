# -*- coding: utf-8 -*-
"""Web search tool with Brave API and HTML fallback."""

from __future__ import annotations

from typing import List, Optional
import json
import os
import re
import urllib.parse
import urllib.request

from integrations.mcp.openai_tool import Tool


class WebSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description=(
                "Search the web and return a list of results. "
                "Defaults to Brave API when key is present, otherwise Brave HTML."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "top_k": {"type": "integer", "description": "Maximum number of results."},
                    "recency_days": {"type": "integer", "description": "Prefer results within N days."},
                    "domains": {"type": "array", "items": {"type": "string"}},
                    "provider": {"type": "string", "description": "brave_api or brave_html"},
                },
                "required": ["query"],
            },
        )

    def _execute(self, **kwargs):
        query = (kwargs.get("query") or "").strip()
        if not query:
            return "query must not be empty."
        top_k = int(kwargs.get("top_k") or 5)
        recency_days = kwargs.get("recency_days")
        domains = kwargs.get("domains") or []
        provider = (kwargs.get("provider") or "").strip().lower()
        if not provider:
            provider = "brave_api" if os.getenv("BRAVE_API_KEY") else "brave_html"
        if provider == "brave_api":
            return _search_brave_api(query, top_k, recency_days, domains)
        if provider == "brave_html":
            return _search_brave_html(query, top_k, domains)
        return "unknown provider."


def _search_brave_api(query: str, top_k: int, recency_days: Optional[int], domains: List[str]) -> str:
    api_key = os.getenv("BRAVE_API_KEY", "").strip()
    if not api_key:
        return "BRAVE_API_KEY is not configured."
    if domains:
        domain_query = " OR ".join(f"site:{d}" for d in domains if d)
        if domain_query:
            query = f"{query} {domain_query}"
    params = {"q": query, "count": str(max(1, min(top_k, 10)))}
    if recency_days:
        params["freshness"] = f"{recency_days}d"
    url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Subscription-Token": api_key})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception:
        return "search failed (Brave API)."
    results = data.get("web", {}).get("results", []) or []
    return _format_results(results, "title", "url", "description")


def _search_brave_html(query: str, top_k: int, domains: List[str]) -> str:
    if domains:
        domain_query = " OR ".join(f"site:{d}" for d in domains if d)
        if domain_query:
            query = f"{query} {domain_query}"
    url = "https://search.brave.com/search?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return "search failed (Brave HTML)."
    results = _parse_brave_html(html, limit=top_k)
    if not results:
        return "no parsed result from Brave HTML."
    return _format_results(results, "title", "url", "snippet")


def _parse_brave_html(html: str, limit: int = 5) -> List[dict]:
    results: List[dict] = []
    link_re = re.compile(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
    snippet_re = re.compile(r'<div[^>]+class="[^"]*snippet[^"]*"[^>]*>(.*?)</div>', re.S)
    links = link_re.findall(html)
    snippets = snippet_re.findall(html)
    for idx, (url, title_html) in enumerate(links):
        title = _strip_tags(title_html)
        snippet = _strip_tags(snippets[idx]) if idx < len(snippets) else ""
        results.append({"title": title, "url": url, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def _strip_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _format_results(results: List[dict], title_key: str, url_key: str, desc_key: str) -> str:
    if not results:
        return "no results found."
    lines = []
    for idx, item in enumerate(results, start=1):
        title = (item.get(title_key) or "").strip()
        url = (item.get(url_key) or "").strip()
        desc = (item.get(desc_key) or "").strip()
        lines.append(f"{idx}. {title}\n{url}\n{desc}".strip())
    return "\n\n".join(lines)
