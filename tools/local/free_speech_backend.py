# -*- coding: utf-8 -*-
"""Free local speech-to-text backend adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from WeClaw_console.core.speech_transcriber import LocalSpeechTranscriber


class FreeSpeechBackend:
    """Adapt the existing local speech transcriber for MCP tools."""

    def __init__(self, project_root: str):
        root = Path(project_root).resolve()
        self.project_root = str(root)
        self.cache_dir = str((root / ".weclaw_cache" / "speech_models").resolve())
        self._transcriber = LocalSpeechTranscriber(self.cache_dir)

    def transcribe(self, file_path: str, language: str = "", task: str = "transcribe") -> Dict[str, Any]:
        return self._transcriber.transcribe_file(file_path, language=language, task=task)
