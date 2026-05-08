# -*- coding: utf-8 -*-
"""Command safety checks shared by execution tools."""

from __future__ import annotations

import re


_RISKY_KEYWORDS = [
    "rm ",
    "rm -",
    "del ",
    "erase ",
    "rmdir ",
    "remove-item",
    "remove-item ",
    "move ",
    "mv ",
    "rename ",
    "ren ",
    "set-content",
    "add-content",
    "out-file",
    ">>",
    "> ",
    "icacls ",
    "attrib ",
    "chmod ",
    "chown ",
]

_ABS_PATH_PATTERNS = [
    re.compile(r"[a-zA-Z]:\\"),
    re.compile(r"[a-zA-Z]:/"),
    re.compile(r"\\\\"),
]


def is_risky_command(command: str) -> bool:
    """Is risky command.
    
    Args:
        command (str): Input value for command.
    
    Returns:
        bool: True when the condition is satisfied; otherwise False.
    """
    text = (command or "").lower()
    return any(keyword in text for keyword in _RISKY_KEYWORDS)


def contains_path_escape(command: str) -> bool:
    """Contains path escape.
    
    Args:
        command (str): Input value for command.
    
    Returns:
        bool: Result produced by this function.
    """
    text = command or ""
    if "..\\" in text or "../" in text:
        return True
    return any(pattern.search(text) for pattern in _ABS_PATH_PATTERNS)
