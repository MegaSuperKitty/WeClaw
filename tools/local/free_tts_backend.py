# -*- coding: utf-8 -*-
"""Free text-to-speech backend adapter using edge-tts."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict


DEFAULT_EDGE_TTS_VOICE = "zh-CN-XiaoxiaoNeural"


class FreeTextToSpeechBackend:
    """Generate speech files through edge-tts."""

    def __init__(self, project_root: str):
        self.project_root = str(Path(project_root).resolve())

    def synthesize(self, text: str, output_path: str, voice: str = "") -> Dict[str, str]:
        target = Path(output_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        selected_voice = str(voice or "").strip() or DEFAULT_EDGE_TTS_VOICE
        asyncio.run(self._save(text=text, output_path=str(target), voice=selected_voice))
        return {"output_path": str(target), "voice": selected_voice, "model": "edge-tts"}

    async def _save(self, text: str, output_path: str, voice: str) -> None:
        try:
            import edge_tts
        except Exception as exc:
            raise RuntimeError("edge-tts is not installed. Please install requirements and retry.") from exc

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
