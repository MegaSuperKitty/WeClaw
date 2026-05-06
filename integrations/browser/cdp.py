# -*- coding: utf-8 -*-
"""Minimal Chromium CDP helpers shared by browser drivers and runtime."""

from __future__ import annotations

import base64
import json
import os
import random
import socket
import ssl
import struct
from typing import Dict, List, Tuple
from urllib import error, parse, request


DEFAULT_HTTP_TIMEOUT = 2.0
DEFAULT_WS_TIMEOUT = 5.0


class BrowserCdpError(RuntimeError):
    """Raised when a Chromium CDP endpoint cannot be used."""


def _endpoint_from_profile(cdp_url: str, cdp_host: str, cdp_port: int) -> str:
    base = str(cdp_url or "").strip()
    if base:
        return base.rstrip("/")
    host = str(cdp_host or "127.0.0.1").strip() or "127.0.0.1"
    port = int(cdp_port or 0) or 18800
    return f"http://{host}:{port}"


def build_cdp_endpoint(cdp_url: str, cdp_host: str, cdp_port: int) -> str:
    return _endpoint_from_profile(cdp_url, cdp_host, cdp_port)


def cdp_http_get(base_url: str, path: str, timeout: float = DEFAULT_HTTP_TIMEOUT):
    url = f"{base_url.rstrip('/')}{path}"
    try:
        with request.urlopen(url, timeout=timeout) as response:
            payload = response.read()
    except error.URLError as exc:
        raise BrowserCdpError(str(exc.reason or exc)) from exc
    except Exception as exc:
        raise BrowserCdpError(str(exc)) from exc
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise BrowserCdpError(f"invalid CDP response from {url}: {exc}") from exc


def get_cdp_version(base_url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> Dict[str, object]:
    data = cdp_http_get(base_url, "/json/version", timeout=timeout)
    return data if isinstance(data, dict) else {}


def list_cdp_targets(base_url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> List[Dict[str, object]]:
    data = cdp_http_get(base_url, "/json/list", timeout=timeout)
    return list(data) if isinstance(data, list) else []


def list_page_tabs(base_url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> List[Dict[str, object]]:
    tabs: List[Dict[str, object]] = []
    for item in list_cdp_targets(base_url, timeout=timeout):
        if not isinstance(item, dict):
            continue
        if str(item.get("type") or "").strip() != "page":
            continue
        tabs.append(
            {
                "target_id": str(item.get("id") or ""),
                "title": str(item.get("title") or ""),
                "url": str(item.get("url") or ""),
                "type": "page",
                "attached": bool(item.get("attached", False)),
                "websocket_url": str(item.get("webSocketDebuggerUrl") or ""),
            }
        )
    return tabs


def open_new_tab(base_url: str, url: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> Dict[str, object]:
    safe_url = str(url or "about:blank").strip() or "about:blank"
    encoded = parse.quote(safe_url, safe=":/?&=%#@+-._~")
    data = cdp_http_get(base_url, f"/json/new?{encoded}", timeout=timeout)
    if not isinstance(data, dict):
        raise BrowserCdpError("CDP new tab response was invalid")
    return {
        "target_id": str(data.get("id") or ""),
        "title": str(data.get("title") or ""),
        "url": str(data.get("url") or safe_url),
        "type": str(data.get("type") or "page"),
        "attached": bool(data.get("attached", False)),
        "websocket_url": str(data.get("webSocketDebuggerUrl") or ""),
    }


def activate_tab(base_url: str, target_id: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> None:
    safe_target = str(target_id or "").strip()
    if not safe_target:
        raise BrowserCdpError("target_id is required")
    path = f"/json/activate/{parse.quote(safe_target, safe='')}"
    cdp_http_get(base_url, path, timeout=timeout)


def close_tab(base_url: str, target_id: str, timeout: float = DEFAULT_HTTP_TIMEOUT) -> None:
    safe_target = str(target_id or "").strip()
    if not safe_target:
        raise BrowserCdpError("target_id is required")
    path = f"/json/close/{parse.quote(safe_target, safe='')}"
    cdp_http_get(base_url, path, timeout=timeout)


class _SimpleWebSocketClient:
    """Very small WebSocket client for one-at-a-time CDP JSON messages."""

    def __init__(self, ws_url: str, timeout: float = DEFAULT_WS_TIMEOUT):
        self.ws_url = ws_url
        self.timeout = timeout
        self._socket: socket.socket | ssl.SSLSocket | None = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def connect(self) -> None:
        parsed = parse.urlparse(self.ws_url)
        host = parsed.hostname or "127.0.0.1"
        scheme = parsed.scheme.lower()
        secure = scheme == "wss"
        port = parsed.port or (443 if secure else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        raw = socket.create_connection((host, port), timeout=self.timeout)
        raw.settimeout(self.timeout)
        if secure:
            context = ssl.create_default_context()
            self._socket = context.wrap_socket(raw, server_hostname=host)
        else:
            self._socket = raw

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self._socket.sendall(handshake)
        response = self._read_http_response()
        if " 101 " not in response.split("\r\n", 1)[0]:
            raise BrowserCdpError(f"websocket handshake failed: {response.splitlines()[0] if response else 'empty response'}")

    def close(self) -> None:
        sock = self._socket
        self._socket = None
        if sock is None:
            return
        try:
            sock.close()
        except Exception:
            pass

    def send_json(self, payload: Dict[str, object]) -> None:
        message = json.dumps(payload).encode("utf-8")
        self._send_frame(message, opcode=0x1)

    def recv_json(self) -> Dict[str, object]:
        payload = self._recv_frame()
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            raise BrowserCdpError(f"invalid websocket payload: {exc}") from exc
        if not isinstance(data, dict):
            raise BrowserCdpError("unexpected websocket payload type")
        return data

    def _read_http_response(self) -> str:
        if self._socket is None:
            raise BrowserCdpError("websocket not connected")
        chunks = b""
        while b"\r\n\r\n" not in chunks:
            part = self._socket.recv(4096)
            if not part:
                break
            chunks += part
        return chunks.decode("utf-8", errors="replace")

    def _send_frame(self, payload: bytes, opcode: int) -> None:
        if self._socket is None:
            raise BrowserCdpError("websocket not connected")
        first = 0x80 | (opcode & 0x0F)
        mask_bit = 0x80
        length = len(payload)
        header = bytearray([first])
        if length < 126:
            header.append(mask_bit | length)
        elif length < 65536:
            header.append(mask_bit | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(mask_bit | 127)
            header.extend(struct.pack("!Q", length))
        mask = struct.pack("!I", random.getrandbits(32))
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self._socket.sendall(bytes(header) + mask + masked)

    def _recv_exact(self, size: int) -> bytes:
        if self._socket is None:
            raise BrowserCdpError("websocket not connected")
        chunks = bytearray()
        while len(chunks) < size:
            part = self._socket.recv(size - len(chunks))
            if not part:
                raise BrowserCdpError("websocket connection closed")
            chunks.extend(part)
        return bytes(chunks)

    def _recv_frame(self) -> bytes:
        header = self._recv_exact(2)
        first, second = header[0], header[1]
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if masked else b""
        payload = self._recv_exact(length) if length else b""
        if masked:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        if opcode == 0x8:
            raise BrowserCdpError("websocket closed by peer")
        if opcode != 0x1:
            raise BrowserCdpError(f"unsupported websocket opcode: {opcode}")
        return payload


def cdp_call(ws_url: str, method: str, params: Dict[str, object] | None = None, timeout: float = DEFAULT_WS_TIMEOUT):
    request_id = 1
    with _SimpleWebSocketClient(ws_url, timeout=timeout) as client:
        client.send_json({"id": request_id, "method": method, "params": params or {}})
        while True:
            message = client.recv_json()
            if int(message.get("id") or 0) != request_id:
                continue
            if "error" in message:
                raise BrowserCdpError(str(message.get("error")))
            return message.get("result") or {}


def evaluate_tab_raw(
    ws_url: str,
    expression: str,
    *,
    return_by_value: bool = True,
    await_promise: bool = False,
    timeout: float = DEFAULT_WS_TIMEOUT,
) -> Dict[str, object]:
    script = str(expression or "").strip()
    if not script:
        raise BrowserCdpError("expression is required")
    result = cdp_call(
        ws_url,
        "Runtime.evaluate",
        params={
            "expression": script,
            "returnByValue": bool(return_by_value),
            "awaitPromise": bool(await_promise),
        },
        timeout=timeout,
    )
    return result if isinstance(result, dict) else {}


def capture_tab_screenshot(ws_url: str, *, full_page: bool = True, timeout: float = DEFAULT_WS_TIMEOUT) -> bytes:
    if full_page:
        try:
            cdp_call(ws_url, "Page.enable", timeout=timeout)
        except BrowserCdpError:
            pass
    result = cdp_call(
        ws_url,
        "Page.captureScreenshot",
        params={"format": "png", "fromSurface": True, "captureBeyondViewport": bool(full_page)},
        timeout=timeout,
    )
    data = str(result.get("data") or "")
    if not data:
        raise BrowserCdpError("CDP screenshot result was empty")
    return base64.b64decode(data)


def capture_tab_snapshot(ws_url: str, timeout: float = DEFAULT_WS_TIMEOUT) -> Dict[str, object]:
    script = """
(() => {
  const title = document.title || "";
  const url = location.href || "";
  const text = (document.body && document.body.innerText) ? document.body.innerText : "";
  const html = document.documentElement ? document.documentElement.outerHTML : "";
  return { title, url, text, html };
})()
""".strip()
    result = cdp_call(
        ws_url,
        "Runtime.evaluate",
        params={"expression": script, "returnByValue": True},
        timeout=timeout,
    )
    value = (((result or {}).get("result") or {}) if isinstance(result, dict) else {}).get("value")
    return value if isinstance(value, dict) else {}


def navigate_tab(ws_url: str, url: str, timeout: float = DEFAULT_WS_TIMEOUT) -> Dict[str, object]:
    target_url = str(url or "about:blank").strip() or "about:blank"
    result = cdp_call(ws_url, "Page.navigate", params={"url": target_url}, timeout=timeout)
    return {"url": target_url, "frame_id": str(result.get("frameId") or "")}


def evaluate_tab_expression(ws_url: str, expression: str, timeout: float = DEFAULT_WS_TIMEOUT):
    result = evaluate_tab_raw(ws_url, expression, return_by_value=True, await_promise=False, timeout=timeout)
    return (((result or {}).get("result") or {}) if isinstance(result, dict) else {}).get("value")


def upload_files_to_input(ws_url: str, selector: str, files: List[str], timeout: float = DEFAULT_WS_TIMEOUT) -> Dict[str, object]:
    safe_selector = str(selector or "").strip()
    normalized_files = [str(item or "").strip() for item in files if str(item or "").strip()]
    if not safe_selector:
        raise BrowserCdpError("selector is required for upload")
    if not normalized_files:
        raise BrowserCdpError("at least one file path is required for upload")
    missing_files = [path for path in normalized_files if not os.path.isfile(path)]
    if missing_files:
        raise BrowserCdpError(f"upload file not found: {missing_files[0]}")

    result = evaluate_tab_raw(
        ws_url,
        f"document.querySelector({json.dumps(safe_selector)})",
        return_by_value=False,
        await_promise=False,
        timeout=timeout,
    )
    remote_result = result.get("result") if isinstance(result, dict) else {}
    object_id = str((remote_result or {}).get("objectId") or "")
    if not object_id:
        raise BrowserCdpError("element_not_found")

    node = cdp_call(ws_url, "DOM.requestNode", params={"objectId": object_id}, timeout=timeout)
    node_id = int(node.get("nodeId") or 0)
    if node_id <= 0:
        raise BrowserCdpError("failed_to_resolve_input_node")
    cdp_call(ws_url, "DOM.setFileInputFiles", params={"nodeId": node_id, "files": normalized_files}, timeout=timeout)
    return {"ok": True, "files": normalized_files}


def act_in_tab(
    ws_url: str,
    kind: str,
    selector: str = "",
    value: str = "",
    expression: str = "",
    url: str = "",
    key: str = "",
    file_path: str = "",
    timeout_ms: int = 0,
    timeout: float = DEFAULT_WS_TIMEOUT,
):
    action = str(kind or "").strip().lower()
    if action == "navigate":
        return navigate_tab(ws_url, url, timeout=timeout)
    if action == "evaluate":
        return {"value": evaluate_tab_expression(ws_url, expression, timeout=timeout)}
    if action == "upload":
        return {"value": upload_files_to_input(ws_url, selector, [file_path], timeout=timeout)}
    if action == "press":
        script = f"""
(() => {{
  const el = document.querySelector({json.dumps(str(selector or "").strip())}) || document.activeElement;
  if (!el) return {{ ok: false, error: "element_not_found" }};
  const key = {json.dumps(str(key or value or "").strip())};
  if (!key) return {{ ok: false, error: "key_required" }};
  el.focus?.();
  el.dispatchEvent(new KeyboardEvent("keydown", {{ key, bubbles: true }}));
  el.dispatchEvent(new KeyboardEvent("keyup", {{ key, bubbles: true }}));
  return {{ ok: true, key }};
}})()
""".strip()
        return {"value": evaluate_tab_expression(ws_url, script, timeout=timeout)}
    if action == "wait":
        wait_selector = str(selector or "").strip()
        wait_timeout = max(0, int(timeout_ms or 0))
        if wait_selector:
            script = f"""
new Promise((resolve) => {{
  const started = Date.now();
  const timeout = {wait_timeout or 3000};
  const tick = () => {{
    const found = document.querySelector({json.dumps(wait_selector)});
    if (found) {{
      resolve({{ ok: true, selector: {json.dumps(wait_selector)} }});
      return;
    }}
    if (Date.now() - started >= timeout) {{
      resolve({{ ok: false, error: "timeout", selector: {json.dumps(wait_selector)} }});
      return;
    }}
    setTimeout(tick, 100);
  }};
  tick();
}})
""".strip()
            return {"value": evaluate_tab_raw(ws_url, script, return_by_value=True, await_promise=True, timeout=timeout).get("result", {}).get("value")}
        script = f"new Promise((resolve) => setTimeout(() => resolve({{ ok: true, waited_ms: {wait_timeout or 3000} }}), {wait_timeout or 3000}))"
        return {"value": evaluate_tab_raw(ws_url, script, return_by_value=True, await_promise=True, timeout=timeout).get("result", {}).get("value")}

    safe_selector = str(selector or "").strip()
    if not safe_selector:
        raise BrowserCdpError("selector is required for this action")

    if action == "click":
        script = f"""
(() => {{
  const el = document.querySelector({json.dumps(safe_selector)});
  if (!el) return {{ ok: false, error: "element_not_found" }};
  el.click();
  return {{ ok: true }};
}})()
""".strip()
        return {"value": evaluate_tab_expression(ws_url, script, timeout=timeout)}

    if action == "fill":
        script = f"""
(() => {{
  const el = document.querySelector({json.dumps(safe_selector)});
  if (!el) return {{ ok: false, error: "element_not_found" }};
  el.value = {json.dumps(str(value or ""))};
  el.dispatchEvent(new Event("input", {{ bubbles: true }}));
  el.dispatchEvent(new Event("change", {{ bubbles: true }}));
  return {{ ok: true, value: el.value }};
}})()
""".strip()
        return {"value": evaluate_tab_expression(ws_url, script, timeout=timeout)}

    raise BrowserCdpError(f"unsupported act kind: {action}")


def choose_tab(tabs: List[Dict[str, object]], target_id: str = "") -> Dict[str, object]:
    if target_id:
        for tab in tabs:
            if str(tab.get("target_id") or "") == str(target_id).strip():
                return tab
        raise BrowserCdpError(f"browser tab not found: {target_id}")
    if tabs:
        return tabs[0]
    raise BrowserCdpError("browser has no attachable page tabs")
