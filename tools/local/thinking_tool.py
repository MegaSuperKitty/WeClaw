# -*- coding: utf-8 -*-
"""Deep reflection tool that asks the LLM for structured reconsideration."""

from __future__ import annotations

from typing import Callable, List, Optional

from integrations.llm.provider import get_response
from integrations.mcp.openai_tool import Tool


class ThinkingTool(Tool):
    """Generate long-form reflection when normal execution gets stuck.
    
    Attributes:
        _context_provider (Optional[Callable[[], List[dict]]]): Instance field for context provider.
    """

    def __init__(self):
        """Initialize tool schema and optional context provider.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        self._context_provider: Optional[Callable[[], List[dict]]] = None
        super().__init__(
            name="thinking_tool",
            description=(
                "Generate a deep reflection response when the agent is stuck or needs to reassess. "
                "Use this to analyze failures, refine the plan, and decide next actions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why deep reflection is needed (e.g., repeated tool failures).",
                    }
                },
                "required": ["reason"],
            },
        )

    def set_context(self, context_provider: Optional[Callable[[], List[dict]]] = None):
        """Inject a callable that returns the latest runtime message list.
        
        Args:
            context_provider (Optional[Callable[[], List[dict]]]): Input value for context provider.
        
        Returns:
            None: This method does not return a value.
        """
        if context_provider is not None:
            self._context_provider = context_provider

    def _execute(self, **kwargs):
        """Run reflection using current context and a caller-provided reason.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        reason = (kwargs.get("reason") or "").strip()
        if not reason:
            return "thinking_tool requires a non-empty reason."

        context_text = _format_context(self._context_provider() if self._context_provider else [])
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a dedicated reflection tool. "
                    "Write at least 300 words that explain failure causes, summarize known facts, "
                    "propose alternatives, and provide concrete next actions."
                ),
            },
            {
                "role": "user",
                "content": f"[Full Context]\n{context_text}\n\n[Reason for Reflection]\n{reason}",
            },
        ]

        response = get_response(messages, tools=None, stream=False)
        return (response.content or "").strip()


def _format_context(messages: List[dict]) -> str:
    """Serialize runtime messages into readable plain text context.
    
    Args:
        messages (List[dict]): Conversation/message payload used for processing.
    
    Returns:
        str: Result produced by this function.
    
    Note:
        This is a private helper used internally by the module/class.
    """
    if not messages:
        return "(no context)"

    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = (msg.get("content") or "").strip()
        if not content:
            content = "(empty)"
        lines.append(f"{role}: {content}")
    return "\n".join(lines)
