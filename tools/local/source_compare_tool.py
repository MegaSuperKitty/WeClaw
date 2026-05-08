# -*- coding: utf-8 -*-
"""Cross-source comparison template tool."""

from __future__ import annotations

from integrations.mcp.openai_tool import Tool


class SourceCompareTool(Tool):
    """Output a structured comparison scaffold for multiple source summaries.
    
    Note:
        This class currently exposes no documented instance attributes.
    """

    def __init__(self):
        """Initialize tool metadata and schema.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        super().__init__(
            name="source_compare",
            description="Compare multiple source summaries and output consensus and differences.",
            parameters={
                "type": "object",
                "properties": {
                    "summaries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of source summaries.",
                    },
                },
                "required": ["summaries"],
            },
        )

    def _execute(self, **kwargs):
        """Return a fill-in template for source consensus and divergence.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        summaries = kwargs.get("summaries") or []
        if not summaries:
            return "No source summaries were provided for comparison."

        cleaned = [s.strip() for s in summaries if str(s).strip()]
        if not cleaned:
            return "No source summaries were provided for comparison."

        lines = [
            "[Consensus]",
            "- (Fill in shared claims supported by multiple sources)",
            "",
            "[Differences]",
            "- (List conflicting or inconsistent claims across sources)",
            "",
            "[Uncertain / Needs Verification]",
            "- (Mark items that are under-supported or need validation)",
        ]
        return "\n".join(lines)
