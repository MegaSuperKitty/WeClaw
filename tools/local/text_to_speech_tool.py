# -*- coding: utf-8 -*-
"""Text-to-speech MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.free_tts_backend import FreeTextToSpeechBackend
from tools.local.model_tool_utils import build_openai_client, optional_output_path, resolve_model_backend, safe_text


class TextToSpeechTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="text_to_speech",
            description="Synthesize speech with the active text-to-speech model.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to synthesize."},
                    "voice": {"type": "string", "description": "Voice name."},
                    "output_path": {"type": "string", "description": "Optional output file path."},
                },
                "required": ["text"],
            },
        )

    def _execute(self, **kwargs):
        text = safe_text(kwargs.get("text"))
        if not text:
            raise ValueError("text is required")
        output_path = optional_output_path(kwargs.get("output_path") or "", "generated-speech.mp3")
        backend = resolve_model_backend(self.project_root, "text_to_speech")
        if backend.mode == "free_fallback":
            free_backend = FreeTextToSpeechBackend(self.project_root)
            return free_backend.synthesize(text=text, output_path=str(output_path), voice=safe_text(kwargs.get("voice")))
        client, profile = build_openai_client(self.project_root, "text_to_speech")
        response = client.audio.speech.create(
            model=profile.model,
            voice=safe_text(kwargs.get("voice")) or "alloy",
            input=text,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        response.stream_to_file(str(output_path))
        return {"output_path": str(output_path), "model": profile.model}
