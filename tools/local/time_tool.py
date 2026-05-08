# -*- coding: utf-8 -*-
"""Local time tool."""

from datetime import datetime

from integrations.mcp.openai_tool import Tool


class TimeTool(Tool):
    """Return the current local time."""

    def __init__(self):
        super().__init__(
            name="time",
            description="Get the current local time.",
            parameters={"type": "object", "properties": {}},
        )

    def _execute(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
