# -*- coding: utf-8 -*-
"""Vision understanding MCP tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool
from tools.local.model_tool_utils import build_openai_client, image_input_from_path_or_url, safe_text


class VisionUnderstandTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="vision_understand",
            description="Understand an input image with the active vision model.",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Instruction for the vision model."},
                    "image_path": {"type": "string", "description": "Local image file path."},
                    "image_url": {"type": "string", "description": "Remote image URL."},
                },
                "required": ["prompt"],
            },
        )

    def _execute(self, **kwargs):
        prompt = safe_text(kwargs.get("prompt"))
        if not prompt:
            raise ValueError("prompt is required")
        client, profile = build_openai_client(self.project_root, "vision")
        image_part = image_input_from_path_or_url(kwargs.get("image_path") or "", kwargs.get("image_url") or "")
        response = client.responses.create(
            model=profile.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        image_part,
                    ],
                }
            ],
        )
        return getattr(response, "output_text", "") or "vision_understand_ok"
