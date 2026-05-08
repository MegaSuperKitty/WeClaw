# -*- coding: utf-8 -*-
"""Compatibility wrapper for the Discord channel entrypoint."""

from __future__ import annotations


def main() -> None:
    from channels.adapters.discord import main as run_main

    run_main()


if __name__ == "__main__":
    main()
