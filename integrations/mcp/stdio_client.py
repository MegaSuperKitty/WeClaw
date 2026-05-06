# -*- coding: utf-8 -*-
"""Generic local stdio MCP client support."""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Mapping, Optional, Tuple

from integrations.mcp.openai_tool import Tool
from integrations.mcp.schema import MCPClientConfig


class StdioMCPClient:
    """Minimal JSON-RPC MCP client over stdio transport."""

    def __init__(self, config: MCPClientConfig, env: Mapping[str, str]):
        self._command = str(config.command or "").strip()
        self._args = [str(item) for item in (config.args or []) if str(item).strip()]
        self._cwd = str(config.cwd or "").strip() or None
        self._env = dict(env or {})
        self._proc: Optional[subprocess.Popen[bytes]] = None
        self._rpc_id = 1
        self._initialized = False
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    def list_tools(self) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        if self._tools_cache is not None:
            return list(self._tools_cache)
        result = self._send_request("tools/list", {})
        tools = (result or {}).get("tools") or []
        self._tools_cache = [tool for tool in tools if isinstance(tool, dict)]
        return list(self._tools_cache)

    def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        self._ensure_initialized()
        result = self._send_request("tools/call", {"name": str(name or "").strip(), "arguments": dict(arguments or {})})
        return result or {}

    def close(self) -> None:
        process = self._proc
        self._proc = None
        if process is None:
            return
        try:
            process.terminate()
            process.wait(timeout=1)
        except Exception:
            try:
                process.kill()
                process.wait(timeout=1)
            except Exception:
                pass
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is None:
                continue
            try:
                stream.close()
            except Exception:
                pass

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        self._start_process()
        self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "weclaw", "version": "1.0.0"},
            },
        )
        self._initialized = True

    def _start_process(self) -> None:
        if self._proc is not None:
            return
        if not self._command:
            raise RuntimeError("stdio MCP client requires command.")
        command = [self._command, *self._args]
        try:
            self._proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._cwd,
                env=self._env,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to start stdio MCP process: {exc}") from exc

    def _send_request(self, method: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        request_id = self._next_id()
        self._write_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": str(method or "").strip(),
                "params": dict(params or {}),
            }
        )
        while True:
            message = self._read_message()
            if not isinstance(message, dict):
                continue
            if message.get("id") != request_id:
                continue
            error = message.get("error")
            if isinstance(error, dict):
                raise RuntimeError(str(error.get("message") or "Unknown MCP error"))
            result = message.get("result")
            return result if isinstance(result, dict) else {}

    def _write_message(self, payload: Mapping[str, Any]) -> None:
        process = self._proc
        if process is None or process.stdin is None:
            raise RuntimeError("stdio MCP process stdin is unavailable.")
        body = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        try:
            process.stdin.write(header)
            process.stdin.write(body)
            process.stdin.flush()
        except Exception as exc:
            raise RuntimeError(f"Failed to write MCP stdio request: {exc}") from exc

    def _read_message(self) -> Dict[str, Any]:
        process = self._proc
        if process is None or process.stdout is None:
            raise RuntimeError("stdio MCP process stdout is unavailable.")
        headers: Dict[str, str] = {}
        while True:
            line = process.stdout.readline()
            if line == b"":
                stderr_text = self._read_stderr_tail(process)
                raise RuntimeError(f"MCP stdio process exited unexpectedly. {stderr_text}".strip())
            stripped = line.strip()
            if not stripped:
                break
            if b":" not in line:
                continue
            key, value = line.split(b":", 1)
            headers[key.decode("ascii", errors="ignore").strip().lower()] = value.decode("ascii", errors="ignore").strip()
        content_length = int(headers.get("content-length", "0") or "0")
        if content_length <= 0:
            raise RuntimeError("Invalid stdio MCP content-length header.")
        body = process.stdout.read(content_length)
        if not body:
            raise RuntimeError("Empty stdio MCP response body.")
        try:
            payload = json.loads(body.decode("utf-8", errors="ignore"))
        except Exception as exc:
            raise RuntimeError(f"Invalid JSON from stdio MCP server: {exc}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("Non-object JSON response from stdio MCP server.")
        return payload

    def _next_id(self) -> int:
        current = self._rpc_id
        self._rpc_id += 1
        return current

    def _read_stderr_tail(self, process: subprocess.Popen[bytes]) -> str:
        try:
            if process.stderr is None:
                return ""
            data = process.stderr.read() or b""
            text = data.decode("utf-8", errors="ignore").strip()
            return text[-400:]
        except Exception:
            return ""


class LocalStdioMCPTool(Tool):
    """Dynamic tool wrapper over one stdio MCP tool definition."""

    def __init__(self, session: StdioMCPClient, tool_def: Mapping[str, Any]):
        remote_name = str(tool_def.get("name") or "").strip()
        description = str(tool_def.get("description") or "").strip()
        schema = tool_def.get("inputSchema")
        parameters = schema if isinstance(schema, dict) else {"type": "object", "properties": {}}
        super().__init__(
            name=remote_name or "local_stdio_tool",
            description=description or f"Local stdio MCP tool: {remote_name or 'local_stdio_tool'}",
            parameters=parameters,
        )
        self._session = session
        self._remote_name = remote_name or self.name

    def _execute(self, **kwargs):
        result = self._session.call_tool(self._remote_name, kwargs)
        return _format_tool_result(result)


def build_local_stdio_tools(config: MCPClientConfig, env: Mapping[str, str]) -> Tuple[List[object], List[Dict[str, Any]]]:
    session = StdioMCPClient(config, env)
    tools = session.list_tools()
    wrappers = [LocalStdioMCPTool(session, tool_def) for tool_def in tools]
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
                return "\n\n".join(text_blocks)
        return json.dumps(result, ensure_ascii=False)
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False)
