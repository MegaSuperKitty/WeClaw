# -*- coding: utf-8 -*-
"""Generic remote MCP client support for streamable HTTP servers."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Mapping, Optional, Tuple

from integrations.mcp.openai_tool import Tool
from integrations.mcp.schema import MCPClientConfig


class StreamableHttpMCPClient:
    """Minimal JSON-RPC MCP client over streamable HTTP."""

    def __init__(self, config: MCPClientConfig, secrets: Mapping[str, str]):
        self._endpoint = str(config.endpoint or "").strip()
        self._headers: Dict[str, str] = {
            str(key): str(value)
            for key, value in (config.headers or {}).items()
            if str(key).strip() and str(value).strip()
        }
        self._secrets = {str(key): str(value) for key, value in (secrets or {}).items() if str(value).strip()}
        self._session_id: Optional[str] = None
        self._rpc_id = 1
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    def list_tools(self) -> List[Dict[str, Any]]:
        self._ensure_session()
        if self._tools_cache is not None:
            return list(self._tools_cache)
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self._next_id(),
        }
        data, _ = self._post(payload, session_id=self._session_id)
        tools = (data.get("result") or {}).get("tools") or []
        self._tools_cache = [tool for tool in tools if isinstance(tool, dict)]
        return list(self._tools_cache)

    def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        self._ensure_session()
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": str(name or "").strip(), "arguments": dict(arguments or {})},
            "id": self._next_id(),
        }
        data, _ = self._post(payload, session_id=self._session_id)
        return data.get("result") or {}

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

    def _post(self, payload: Dict[str, Any], session_id: Optional[str]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self._endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        for key, value in self._request_headers().items():
            req.add_header(key, value)
        if session_id:
            req.add_header("Mcp-Session-Id", session_id)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                headers = {str(k).lower(): str(v) for k, v in resp.headers.items()}
                raw = resp.read().decode("utf-8", errors="ignore")
            return _parse_mcp_response(raw, headers), headers
        except urllib.error.HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body_text = ""
            raise RuntimeError(f"HTTP {exc.code}: {body_text}".strip()) from None

    def _request_headers(self) -> Dict[str, str]:
        headers = dict(self._headers)
        api_key = str(self._secrets.get("api_key", "") or "").strip()
        if api_key and not any(str(key).lower() == "authorization" for key in headers):
            headers["Authorization"] = _auth_header_value(api_key)
        return headers

    def _next_id(self) -> int:
        current = self._rpc_id
        self._rpc_id += 1
        return current


class RemoteMCPTool(Tool):
    """Dynamic wrapper over one remote MCP tool definition."""

    def __init__(self, session: StreamableHttpMCPClient, tool_def: Mapping[str, Any]):
        remote_name = str(tool_def.get("name") or "").strip()
        description = str(tool_def.get("description") or "").strip()
        schema = tool_def.get("inputSchema")
        parameters = schema if isinstance(schema, dict) else {"type": "object", "properties": {}}
        super().__init__(
            name=remote_name or "remote_tool",
            description=description or f"Remote MCP tool: {remote_name or 'remote_tool'}",
            parameters=parameters,
        )
        self._session = session
        self._remote_name = remote_name or self.name

    def _execute(self, **kwargs):
        result = self._session.call_tool(self._remote_name, kwargs)
        return _format_tool_result(result)


def build_remote_tools(config: MCPClientConfig, secrets: Mapping[str, str]) -> Tuple[List[object], List[Dict[str, Any]]]:
    session = StreamableHttpMCPClient(config, secrets)
    tools = session.list_tools()
    wrappers = [RemoteMCPTool(session, tool_def) for tool_def in tools]
    catalog = [_tool_descriptor(tool_def) for tool_def in tools]
    return wrappers, catalog


def _tool_descriptor(tool_def: Mapping[str, Any]) -> Dict[str, Any]:
    schema = tool_def.get("inputSchema")
    return {
        "name": str(tool_def.get("name") or "").strip(),
        "description": str(tool_def.get("description") or "").strip(),
        "input_schema": schema if isinstance(schema, dict) else {"type": "object", "properties": {}},
    }


def _format_tool_result(result: Any) -> str:
    if not result:
        return ""
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list):
            text_blocks = [
                str(item.get("text") or "").strip()
                for item in content
                if isinstance(item, dict) and str(item.get("type") or "").strip() == "text" and str(item.get("text") or "").strip()
            ]
            if text_blocks:
                merged = "\n\n".join(text_blocks)
                parsed = _try_parse_json(merged)
                if parsed is not None:
                    return _format_json_like(parsed)
                return merged
        parsed = _try_parse_json(result)
        if parsed is not None:
            return _format_json_like(parsed)
    if isinstance(result, str):
        parsed = _try_parse_json(result)
        if parsed is not None:
            return _format_json_like(parsed)
        return result
    return json.dumps(result, ensure_ascii=False)


def _try_parse_json(value: Any):
    if value is None:
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
            nested = json.loads(parsed)
            return nested
        except Exception:
            return parsed
    return parsed


def _format_json_like(data: Any) -> str:
    results: List[Any] = []
    if isinstance(data, dict):
        for key in ("results", "data", "items", "list"):
            if isinstance(data.get(key), list):
                results = data.get(key)
                break
    elif isinstance(data, list):
        results = data

    if not results:
        return json.dumps(data, ensure_ascii=False)

    lines: List[str] = []
    for index, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("name") or "").strip()
        url = str(item.get("url") or item.get("link") or "").strip()
        desc = str(item.get("summary") or item.get("snippet") or item.get("description") or "").strip()
        line = f"{index}. {title}\n{url}\n{desc}".strip()
        if line:
            lines.append(line)
    return "\n\n".join(lines) if lines else json.dumps(data, ensure_ascii=False)


def _parse_mcp_response(raw: str, headers: Mapping[str, str]) -> Dict[str, Any]:
    if not raw:
        raise RuntimeError("Empty response body from MCP server.")
    content_type = str(headers.get("content-type") or "").lower()
    if "text/event-stream" in content_type or raw.lstrip().startswith("data:"):
        for event in _parse_sse_events(raw):
            data = event.get("data")
            if not data:
                continue
            parsed = _try_parse_json(data)
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
            current[str(key).strip()] = str(value).strip()
    if current:
        events.append(current)
    return events


def _auth_header_value(api_key: str) -> str:
    text = str(api_key or "").strip()
    if not text:
        return ""
    if text.lower().startswith("bearer "):
        return text
    return text
