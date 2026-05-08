# -*- coding: utf-8 -*-
"""Image generation MCP tool."""

from __future__ import annotations

from base64 import b64decode

from integrations.mcp.openai_tool import Tool
from tools.local.model_tool_utils import build_openai_client, optional_output_path, safe_text


class ImageGenerationTool(Tool):
    def __init__(self, project_root: str):
        self.project_root = project_root
        super().__init__(
            name="generate_image",
            description="Generate an image with the active image-generation model.",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Image generation prompt."},
                    "size": {"type": "string", "description": "Requested image size, e.g. 1024x1024."},
                    "output_path": {"type": "string", "description": "Optional output file path."},
                },
                "required": ["prompt"],
            },
        )

    def _execute(self, **kwargs):
        prompt = safe_text(kwargs.get("prompt"))
        if not prompt:
            raise ValueError("prompt is required")
        client, profile = build_openai_client(self.project_root, "image_generation")
        response = client.images.generate(
            model=profile.model,
            prompt=prompt,
            size=safe_text(kwargs.get("size")) or "1024x1024",
        )
        data_rows = getattr(response, "data", None) or []
        if not data_rows:
            raise ValueError("image_generation_empty")
        image_b64 = getattr(data_rows[0], "b64_json", "") or ""
        if not image_b64:
            raise ValueError("image_generation_missing_b64")
        output_path = optional_output_path(kwargs.get("output_path") or "", "generated-image.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b64decode(image_b64))
        return {"output_path": str(output_path), "model": profile.model}
