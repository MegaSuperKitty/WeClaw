# -*- coding: utf-8 -*-
"""Package entry point for `python -m WeClaw_console`."""

from __future__ import annotations

from typing import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    from entry_weclaw_console import main as run_main

    run_main(argv)


if __name__ == "__main__":
    main()
