# -*- coding: utf-8 -*-
"""Run selected built-in local MCP servers over stdio transport."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional

# Ensure package imports work when this file is executed as a script path.
# The runner is executed as `<repo>/integrations/mcp/local_stdio_runner.py`,
# so `integrations.*` imports require the repository root on `sys.path`.
_PACKAGE_ROOT = str(Path(__file__).resolve().parents[2])
if _PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, _PACKAGE_ROOT)

from integrations.mcp.local_stdio_templates import supports_local_stdio
from integrations.mcp.mcp_server import get_server
from tools.local.skill_tool import SkillRuntime
from core.workspace.layout import ensure_workspace_layout, ensure_workspace_layout_for_source


@dataclass
class _RunnerTarget:
    project_root: str
    agent_root: str
    workspace_root: str
    workspace_layout: object | None = None
    skill_runtime: Optional[SkillRuntime] = None
    skill_tool: Optional[object] = None


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WeClaw built-in local MCP stdio runner")
    parser.add_argument("--server-id", required=True, help="Built-in local server id")
    parser.add_argument("--project-root", default="", help="Project root path")
    parser.add_argument("--agent-root", default="", help="Agent root path")
    return parser.parse_args(argv)


def _resolve_paths(args: argparse.Namespace) -> tuple[str, str]:
    project_root = (
        str(args.project_root or "").strip()
        or str(os.getenv("WE_CLAW_PROJECT_ROOT", "")).strip()
        or os.getcwd()
    )
    layout = ensure_workspace_layout_for_source(project_root)
    agent_root = str(args.agent_root or "").strip() or str(os.getenv("WE_CLAW_AGENT_ROOT", "")).strip() or layout.agent_root
    return os.path.abspath(project_root), os.path.abspath(agent_root)


def _build_tools(server_id: str, project_root: str, agent_root: str) -> Dict[str, object]:
    if not supports_local_stdio(server_id):
        raise RuntimeError(f"Server does not support stdio runner: {server_id}")
    server = get_server(server_id)
    if server is None:
        raise RuntimeError(f"Unknown built-in server id: {server_id}")

    layout = ensure_workspace_layout(agent_root, source_root=project_root)
    target = _RunnerTarget(
        project_root=project_root,
        agent_root=agent_root,
        workspace_root=layout.workspace_root,
        workspace_layout=layout,
    )
    if server_id == "skills":
        target.skill_runtime = SkillRuntime(project_root=project_root, workspace_root=agent_root)
        target.skill_runtime.refresh("")
        target.skill_tool = target.skill_runtime.create_tool(register=True)

    tools = server.build_tools(target, [])
    by_name: Dict[str, object] = {}
    for tool in tools:
        name = str(getattr(tool, "name", "") or "").strip()
        if name:
            by_name[name] = tool
    return by_name


def _tool_rows(tools_by_name: Mapping[str, object]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for name, tool in tools_by_name.items():
        rows.append(
            {
                "name": name,
                "description": str(getattr(tool, "description", "") or "").strip(),
                "inputSchema": dict(getattr(tool, "parameters", {}) or {}),
            }
        )
    return rows


def _read_message() -> Optional[Dict[str, object]]:
    headers: Dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        if b":" not in line:
            continue
        key, value = line.split(b":", 1)
        headers[key.decode("ascii", errors="ignore").strip().lower()] = value.decode("ascii", errors="ignore").strip()
    size = int(headers.get("content-length", "0") or "0")
    if size <= 0:
        return None
    body = sys.stdin.buffer.read(size)
    if not body:
        return None
    try:
        payload = json.loads(body.decode("utf-8", errors="ignore"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _write_message(payload: Mapping[str, object]) -> None:
    body = json.dumps(payload).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def _write_result(request_id: object, result: Mapping[str, object]) -> None:
    _write_message({"jsonrpc": "2.0", "id": request_id, "result": dict(result)})


def _write_error(request_id: object, code: int, message: str) -> None:
    _write_message(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": str(message or "error")},
        }
    )


def _format_tool_output(value: object) -> Dict[str, object]:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value or "")
    return {"content": [{"type": "text", "text": text}]}


def main(argv: List[str]) -> int:
    args = _parse_args(argv)
    server_id = str(args.server_id or "").strip()
    project_root, agent_root = _resolve_paths(args)

    try:
        tools_by_name = _build_tools(server_id, project_root, agent_root)
    except Exception as exc:
        sys.stderr.write(f"[local_stdio_runner] {exc}\n")
        sys.stderr.flush()
        return 2

    while True:
        request = _read_message()
        if request is None:
            return 0
        request_id = request.get("id")
        method = str(request.get("method") or "").strip()
        params = request.get("params") or {}

        if method == "initialize":
            _write_result(request_id, {"capabilities": {"tools": {}}, "serverInfo": {"name": server_id, "version": "1.0.0"}})
            continue
        if method == "tools/list":
            _write_result(request_id, {"tools": _tool_rows(tools_by_name)})
            continue
        if method == "tools/call":
            tool_name = str((params or {}).get("name") or "").strip()
            tool_args = (params or {}).get("arguments") or {}
            tool = tools_by_name.get(tool_name)
            if tool is None:
                _write_error(request_id, -32602, f"Unknown tool: {tool_name}")
                continue
            try:
                output = tool.run(tool_args)
                _write_result(request_id, _format_tool_output(output))
            except Exception as exc:
                _write_error(request_id, -32000, str(exc))
            continue
        _write_error(request_id, -32601, f"Unsupported method: {method}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
