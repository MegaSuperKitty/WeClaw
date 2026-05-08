# -*- coding: utf-8 -*-
"""Video generation MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.model_tool_utils import build_openai_client, safe_text


class VideoGenerationTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="generate_video",
            description="Generate a video with the active video-generation model when the provider supports it.",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Video generation prompt."},
                },
                "required": ["prompt"],
            },
        )

    def _execute(self, **kwargs):
        prompt = safe_text(kwargs.get("prompt"))
        if not prompt:
            raise ValueError("prompt is required")
        _, profile = build_openai_client(self.project_root, "video_generation")
        raise ValueError(f"video_generation_not_implemented_for_provider:{profile.provider}")
