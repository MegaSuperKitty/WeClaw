# -*- coding: utf-8 -*-
"""Main-session tool for yielding the current turn until a later update."""

from __future__ import annotations

import json

from integrations.mcp.openai_tool import Tool


class WaitForUpdateTool(Tool):
    """Signal that the main session should close the current turn."""

    def __init__(self):
        super().__init__(
            name="wait_for_update",
            description=(
                "End the current main-session turn after delegated work is running in the background. "
                "Use when no further user clarification is required and there is no confirmed result yet."
            ),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )

    def _execute(self, **kwargs):
        _ = kwargs
        return json.dumps(
            {
                "ok": True,
                "message": "Wait registered. You will be notified when there is an update.",
            },
            ensure_ascii=False,
        )
