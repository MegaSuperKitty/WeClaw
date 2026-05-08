# -*- coding: utf-8 -*-
"""Local offline speech-to-text using faster-whisper."""

from __future__ import annotations

import os
from pathlib import Path
import threading
from typing import Any, Dict, Optional


class LocalSpeechTranscriber:
    """Lazy-loaded local STT transcriber.

    Notes:
    - No external speech API calls.
    - Model is loaded on first request to keep startup fast.
    """

    def __init__(self, cache_dir: str):
        self.cache_dir = str(Path(cache_dir).resolve())
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        self.model_name = str(os.getenv("STT_MODEL", "small")).strip() or "small"
        self.device = str(os.getenv("STT_DEVICE", "cpu")).strip() or "cpu"
        self.compute_type = str(os.getenv("STT_COMPUTE_TYPE", "int8")).strip() or "int8"
        self.beam_size = self._parse_int(os.getenv("STT_BEAM_SIZE", "5"), 5, minimum=1, maximum=10)
        self.max_audio_mb = self._parse_int(os.getenv("STT_MAX_AUDIO_MB", "25"), 25, minimum=1, maximum=200)
        self.default_vad_filter = self._parse_bool(os.getenv("STT_VAD_FILTER", "1"), True)

        self._lock = threading.Lock()
        self._model = None

    def status(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "device": self.device,
            "compute_type": self.compute_type,
            "beam_size": self.beam_size,
            "max_audio_mb": self.max_audio_mb,
            "model_loaded": self._model is not None,
            "cache_dir": self.cache_dir,
        }

    def max_audio_bytes(self) -> int:
        return int(self.max_audio_mb) * 1024 * 1024

    def transcribe_file(self, audio_path: str, language: str = "", task: str = "transcribe") -> Dict[str, Any]:
        model = self._get_model()
        normalized_task = str(task or "transcribe").strip().lower()
        if normalized_task not in {"transcribe", "translate"}:
            normalized_task = "transcribe"

        lang = str(language or "").strip().lower()
        if not lang or lang in {"auto", "", "null", "none"}:
            lang = None

        segments, info = model.transcribe(
            audio_path,
            task=normalized_task,
            language=lang,
            beam_size=int(self.beam_size),
            vad_filter=bool(self.default_vad_filter),
        )

        parts = []
        segment_rows = []
        for seg in segments:
            text = str(getattr(seg, "text", "") or "").strip()
            if text:
                parts.append(text)
            segment_rows.append(
                {
                    "start": float(getattr(seg, "start", 0.0) or 0.0),
                    "end": float(getattr(seg, "end", 0.0) or 0.0),
                    "text": text,
                }
            )

        final_text = " ".join(parts).strip()
        return {
            "text": final_text,
            "language": str(getattr(info, "language", "") or ""),
            "language_probability": float(getattr(info, "language_probability", 0.0) or 0.0),
            "duration": float(getattr(info, "duration", 0.0) or 0.0),
            "segments": segment_rows,
            "task": normalized_task,
            "model": self.model_name,
        }

    def _get_model(self):
        with self._lock:
            if self._model is not None:
                return self._model
            try:
                from faster_whisper import WhisperModel
            except Exception as exc:
                raise RuntimeError(
                    "faster-whisper is not installed. Please install requirements and retry."
                ) from exc

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.cache_dir,
            )
            return self._model

    def _parse_bool(self, value: str, default: bool) -> bool:
        text = str(value or "").strip().lower()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
        return default

    def _parse_int(self, value: str, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(str(value or "").strip())
        except Exception:
            return default
        return max(minimum, min(maximum, parsed))
