# -*- coding: utf-8 -*-
"""Compatibility wrapper for the CLI channel entrypoint."""

from __future__ import annotations


def main() -> None:
    from channels.cli import main as run_main

    run_main()


if __name__ == "__main__":
    main()
