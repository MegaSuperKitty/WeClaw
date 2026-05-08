# -*- coding: utf-8 -*-
"""Speech-to-text MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.free_speech_backend import FreeSpeechBackend
from tools.local.model_tool_utils import build_openai_client, ensure_file_path, resolve_model_backend


class SpeechToTextTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="speech_to_text",
            description="Transcribe audio with the active speech-to-text model.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Local audio file path."},
                },
                "required": ["file_path"],
            },
        )

    def _execute(self, **kwargs):
        audio_path = ensure_file_path(kwargs.get("file_path") or "")
        backend = resolve_model_backend(self.project_root, "speech_to_text")
        if backend.mode == "free_fallback":
            free_backend = FreeSpeechBackend(self.project_root)
            result = free_backend.transcribe(str(audio_path))
            return result.get("text", "") or "speech_to_text_ok"
        client, profile = build_openai_client(self.project_root, "speech_to_text")
        with audio_path.open("rb") as handle:
            response = client.audio.transcriptions.create(model=profile.model, file=handle)
        return getattr(response, "text", "") or "speech_to_text_ok"
