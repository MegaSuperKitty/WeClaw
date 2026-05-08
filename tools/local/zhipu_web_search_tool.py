# -*- coding: utf-8 -*-
"""Zhipu Web Search MCP tool (streamable HTTP)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import json
import os
import urllib.error
import urllib.request

from integrations.mcp.openai_tool import Tool


class ZhipuWebSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="web_search_zhipu",
            description="Search the web via Zhipu Web Search MCP (streamable HTTP).",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "top_k": {"type": "integer", "description": "Maximum number of results (1-50)."},
                    "recency": {"type": "string", "description": "day/week/month/year/none"},
                    "domains": {"type": "array", "items": {"type": "string"}},
                    "summary_level": {"type": "string", "description": "medium or high"},
                    "engine": {"type": "string", "description": "webSearchStd/webSearchPro/webSearchSogou/webSearchQuark"},
                },
                "required": ["query"],
            },
        )
        self._server_url = os.getenv(
            "ZHIPU_WEB_SEARCH_MCP_URL",
            "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp",
        )
        self._api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("BIGMODEL_API_KEY") or ""
        self._session_id: Optional[str] = None
        self._tools_cache: Optional[List[Dict]] = None
        self._rpc_id = 1

    def _execute(self, **kwargs):
        query = (kwargs.get("query") or "").strip()
        if not query:
            return "query must not be empty."
        if not self._api_key:
            return "ZHIPU_API_KEY (or BIGMODEL_API_KEY) is not configured."
        engine = (kwargs.get("engine") or "webSearchPro").strip()
        params = _build_params(
            query=query,
            top_k=kwargs.get("top_k"),
            recency=(kwargs.get("recency") or "none").strip().lower(),
            domains=kwargs.get("domains") or [],
            summary_level=(kwargs.get("summary_level") or "medium").strip().lower(),
            tools=self._list_tools(),
            tool_name=_pick_tool_name(engine, self._list_tools()),
        )
        result = self._call_tool(_pick_tool_name(engine, self._list_tools()), params)
        return _format_results(result)

    def _ensure_session(self) -> None:
        if self._session_id:
            return
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "weclaw", "version": "1.0.0"},
            },
            "id": self._next_id(),
        }
        _, headers = self._post(payload, session_id=None)
        self._session_id = headers.get("mcp-session-id")

    def _list_tools(self) -> List[Dict]:
        self._ensure_session()
        if self._tools_cache is not None:
            return self._tools_cache
        payload = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": self._next_id()}
        data, _ = self._post(payload, session_id=self._session_id)
        self._tools_cache = (data.get("result") or {}).get("tools") or []
        return self._tools_cache

    def _call_tool(self, name: str, params: Dict) -> Dict:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": params},
            "id": self._next_id(),
        }
        data, _ = self._post(payload, session_id=self._session_id)
        return data.get("result") or {}

    def _post(self, payload: Dict, session_id: Optional[str]) -> Tuple[Dict, Dict[str, str]]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self._server_url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("Authorization", _auth_header_value(self._api_key))
        if session_id:
            req.add_header("Mcp-Session-Id", session_id)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                raw = resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
            raise RuntimeError(f"HTTP {exc.code}: {body_text}".strip()) from None
        data = _parse_mcp_response(raw, headers)
        return data, headers

    def _next_id(self) -> int:
        current = self._rpc_id
        self._rpc_id += 1
        return current


def _pick_tool_name(engine: str, tools: List[Dict]) -> str:
    names = [tool.get("name") for tool in tools if isinstance(tool, dict) and tool.get("name")]
    return engine if engine in names else (names[0] if names else engine)


def _build_params(
    query: str,
    top_k: Optional[int],
    recency: str,
    domains: List[str],
    summary_level: str,
    tools: List[Dict],
    tool_name: str,
) -> Dict:
    params: Dict[str, object] = {"query": query}
    if top_k:
        params["count"] = int(top_k)
    if recency and recency != "none":
        params["recency"] = recency
    if domains:
        params["domains"] = domains
    if summary_level:
        params["summary_level"] = summary_level
    schema = {}
    for tool in tools or []:
        if tool.get("name") == tool_name:
            schema = (tool.get("inputSchema") or {}).get("properties") or {}
            break
    if not schema:
        return params
    mapped: Dict[str, object] = {}
    for key, value in params.items():
        if key in schema:
            mapped[key] = value
    if "q" in schema and "query" in params:
        mapped["q"] = params["query"]
    if "search_query" in schema and "query" in params:
        mapped["search_query"] = params["query"]
    if "top_k" in schema and "count" in params:
        mapped["top_k"] = params["count"]
    if "limit" in schema and "count" in params:
        mapped["limit"] = params["count"]
    if "time_filter" in schema and "recency" in params:
        mapped["time_filter"] = params["recency"]
    return mapped or params


def _format_results(result: Dict) -> str:
    if not result:
        return "no result returned."
    content = result.get("content")
    if isinstance(content, list):
        for item in content:
            if item.get("type") == "text" and item.get("text"):
                text = item["text"]
                parsed = _try_parse_json(text)
                return _format_from_json(parsed) if parsed is not None else text
    parsed = _try_parse_json(result)
    return _format_from_json(parsed) if parsed is not None else json.dumps(result, ensure_ascii=False)


def _try_parse_json(value):
    if not value:
        return None
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except Exception:
        return None
    if isinstance(parsed, str):
        try:
            return json.loads(parsed)
        except Exception:
            return parsed
    return parsed


def _format_from_json(data) -> str:
    results = []
    if isinstance(data, dict):
        for key in ("results", "data", "items", "list"):
            if isinstance(data.get(key), list):
                results = data.get(key)
                break
    elif isinstance(data, list):
        results = data
    if not results:
        return json.dumps(data, ensure_ascii=False)
    lines: list[str] = []
    for idx, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or item.get("name") or "").strip()
        url = (item.get("url") or item.get("link") or "").strip()
        desc = (item.get("summary") or item.get("snippet") or item.get("description") or "").strip()
        lines.append(f"{idx}. {title}\n{url}\n{desc}".strip())
    return "\n\n".join(lines) if lines else json.dumps(data, ensure_ascii=False)


def _parse_mcp_response(raw: str, headers: Dict[str, str]) -> Dict:
    if not raw:
        raise RuntimeError("Empty response body from MCP server.")
    content_type = (headers.get("content-type") or "").lower()
    if "text/event-stream" in content_type or raw.lstrip().startswith("data:"):
        events = _parse_sse_events(raw)
        for event in events:
            parsed = _try_parse_json(event.get("data"))
            if isinstance(parsed, dict):
                return parsed
        raise RuntimeError(f"SSE response did not contain JSON: {raw[:500]}")
    parsed = _try_parse_json(raw)
    if isinstance(parsed, dict):
        return parsed
    raise RuntimeError(f"Non-JSON response: {raw[:500]}")


def _parse_sse_events(raw: str) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            if current:
                events.append(current)
                current = {}
            continue
        if line.startswith(":"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        events.append(current)
    return events


def _auth_header_value(api_key: str) -> str:
    mode = (os.getenv("ZHIPU_MCP_AUTH_MODE") or "").strip().lower()
    if api_key.lower().startswith("bearer "):
        return api_key
    if mode == "bearer":
        return f"Bearer {api_key}"
    return api_key
