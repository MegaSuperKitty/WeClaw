# -*- coding: utf-8 -*-
"""Desktop entry point - runs console in a native window using webview."""

from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Sequence

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7788

# Icon path - user can replace this file with their own icon
ICON_PATH = Path(__file__).parent / "WeClaw_console" / "web" / "assets" / "icons" / "app-icon.png"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start WeClaw as a desktop application."
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Bind host for the internal web server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Bind port for the internal web server.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="Window width (default: 1200).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=800,
        help="Window height (default: 800).",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Open in browser instead of desktop window.",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _start_server(host: str, port: int, ready_event: threading.Event) -> None:
    """Run uvicorn server in background thread."""
    # Disable uvicorn logging to avoid clutter
    import logging

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    config = uvicorn.Config(
        "WeClaw_console.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    # Signal that server is starting
    ready_event.set()
    server.run()


def _wait_for_server(url: str, timeout: float = 30.0) -> bool:
    """Wait until the server is ready."""
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False


def _set_window_icon(icon_path: Path) -> None:
    """Set window icon using platform-specific methods.

    Note: This only works reliably when the app is packaged.
    For development, the icon is set via webview.start() on some platforms.
    """
    if sys.platform == "win32" and icon_path.exists():
        try:
            import ctypes
            from ctypes import wintypes

            # Load the icon
            icon_handle = ctypes.windll.user32.LoadImageW(
                None,
                str(icon_path),
                1,  # IMAGE_ICON
                0,
                0,
                0x00000010,  # LR_LOADFROMFILE
            )

            if icon_handle:
                # Get the console window (for packaged apps, this may need adjustment)
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, icon_handle)  # WM_SETICON, ICON_SMALL
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, icon_handle)  # WM_SETICON, ICON_BIG
        except Exception:
            pass


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    url = f"http://{args.host}:{args.port}"

    # Start server in background thread
    ready_event = threading.Event()
    server_thread = threading.Thread(
        target=_start_server,
        args=(args.host, args.port, ready_event),
        daemon=True,
    )
    server_thread.start()

    # Wait for server to start
    if not _wait_for_server(f"{url}/api/v1/health", timeout=30.0):
        print("Failed to start server")
        return

    if args.browser:
        # Browser mode for debugging
        print(f"Opening {url} in browser...")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        # Desktop mode with webview
        try:
            import webview
        except ImportError:
            print("pywebview is not installed. Installing...")
            import subprocess

            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
            import webview

        # Create window with webview
        window = webview.create_window(
            "WeClaw",
            url=url,
            width=args.width,
            height=args.height,
            min_size=(800, 600),
        )

        print(f"Starting WeClaw desktop app...")

        # Try to set icon (works on some platforms when packaged)
        icon = str(ICON_PATH) if ICON_PATH.exists() else None

        webview.start(debug=False, icon=icon)


if __name__ == "__main__":
    main()
