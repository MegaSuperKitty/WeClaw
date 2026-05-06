# -*- coding: utf-8 -*-
"""Render the workspace prompt template using controlled placeholder fields."""

from __future__ import annotations


REQUIRED_FIELDS = (
    "highest_priority_runtime_constraints",
    "soul_content",
    "identity_content",
    "user_content",
    "agent_content",
    "memory_content",
    "workspace_runtime",
    "skills_runtime",
)


def render_system_prompt(template_text: str, fields: dict[str, str]) -> str:
    """Render one system prompt template with the required placeholder fields."""
    text = str(template_text or "")
    for field_name in REQUIRED_FIELDS:
        placeholder = "{" + field_name + "}"
        if placeholder not in text:
            raise ValueError(f"missing required placeholder: {placeholder}")
    rendered = text.format(**{key: str(value or "") for key, value in fields.items()})
    return rendered.strip()
