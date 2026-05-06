# -*- coding: utf-8 -*-
"""Browser identity helpers for user-facing browser selection."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Dict, List


WINDOWS_USER_DATA_ROOTS = {
    "chrome": r"%LOCALAPPDATA%\Google\Chrome\User Data",
    "edge": r"%LOCALAPPDATA%\Microsoft\Edge\User Data",
    "brave": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data",
    "chromium": r"%LOCALAPPDATA%\Chromium\User Data",
}

MAC_USER_DATA_ROOTS = {
    "chrome": "~/Library/Application Support/Google/Chrome",
    "edge": "~/Library/Application Support/Microsoft Edge",
    "brave": "~/Library/Application Support/BraveSoftware/Brave-Browser",
    "chromium": "~/Library/Application Support/Chromium",
}


def normalize_local_path(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return str(Path(os.path.expandvars(os.path.expanduser(text))).resolve())


def detect_browser_family(executable_path: str) -> str:
    text = str(executable_path or "").strip().lower()
    name = Path(text).name
    if "brave" in text or "brave" in name:
        return "brave"
    if "edge" in text or "msedge" in name:
        return "edge"
    if "chromium" in text:
        return "chromium"
    if "chrome" in text:
        return "chrome"
    return ""


def browser_display_name(family: str) -> str:
    return {
        "chrome": "Google Chrome",
        "edge": "Microsoft Edge",
        "brave": "Brave",
        "chromium": "Chromium",
    }.get(str(family or "").strip(), "")


def infer_user_data_dir(family: str) -> str:
    system_name = platform.system().lower()
    roots = MAC_USER_DATA_ROOTS if system_name == "darwin" else WINDOWS_USER_DATA_ROOTS if system_name == "windows" else {}
    raw = roots.get(str(family or "").strip(), "")
    normalized = normalize_local_path(raw)
    return normalized if normalized and Path(normalized).exists() else ""


def list_profile_directories(user_data_dir: str) -> List[Dict[str, str]]:
    root = Path(str(user_data_dir or "").strip())
    if not root.exists() or not root.is_dir():
        return []

    rows: List[Dict[str, str]] = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name == "Default" or name.startswith("Profile "):
            rows.append(
                {
                    "id": name,
                    "label": "Default Profile" if name == "Default" else name,
                    "path": str(entry.resolve()),
                }
            )
    return rows


def recommend_profile_directory(profile_rows: List[Dict[str, str]]) -> str:
    if not profile_rows:
        return ""
    for item in profile_rows:
        if str(item.get("id") or "") == "Default":
            return "Default"
    return str(profile_rows[0].get("id") or "")
