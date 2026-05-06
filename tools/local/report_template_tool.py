# -*- coding: utf-8 -*-
"""Generate a simple structured report template."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool


class ReportTemplateTool(Tool):
    """Generate a report outline with citation placeholders."""

    def __init__(self):
        super().__init__(
            name="report_template",
            description="Generate a structured report template with citation placeholders.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Report topic."},
                    "requirements": {"type": "string", "description": "Optional requirements."},
                },
                "required": ["topic"],
            },
        )

    def _execute(self, **kwargs):
        topic = (kwargs.get("topic") or "").strip()
        requirements = (kwargs.get("requirements") or "").strip()
        if not topic:
            return "topic must not be empty."
        req_block = f"Requirements: {requirements}\n\n" if requirements else ""
        return (
            f"Title: {topic}\n\n"
            f"{req_block}"
            "1. Background and Scope\n"
            "- Context and motivation (source: [#])\n\n"
            "2. Method and Data Sources\n"
            "- Search strategy and source types\n"
            "- Inclusion/exclusion criteria\n\n"
            "3. Key Findings\n"
            "- Finding 1 (source: [#])\n"
            "- Finding 2 (source: [#])\n\n"
            "4. Consensus and Disagreements\n"
            "- Consensus points (sources: [#][#])\n"
            "- Disagreements (sources: [#][#])\n\n"
            "5. Conclusion and Recommendations\n"
            "- Conclusion\n"
            "- Recommendations\n\n"
            "6. References\n"
            "- [#] Title - URL\n"
        )
