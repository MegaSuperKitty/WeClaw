# -*- coding: utf-8 -*-
"""Unified console entry point for WeClaw."""

from __future__ import annotations

import argparse
import os
from typing import Sequence


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7788
DEFAULT_AGENT_ID = "main"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the WeClaw web console.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Bind host for the web console.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port for the web console.")
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID, help="Agent id for runtime state under ~/.weclaw/agents/.")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    from WeClaw_console.app import run_console

    os.environ["WE_CLAW_AGENT_ID"] = str(args.agent_id or DEFAULT_AGENT_ID).strip() or DEFAULT_AGENT_ID
    run_console(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
