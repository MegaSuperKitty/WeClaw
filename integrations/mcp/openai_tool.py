# -*- coding: utf-8 -*-
"""OpenAI tool compatibility primitives used by the MCP runtime."""

from __future__ import annotations

from typing import Any, Dict
import json


class Tool:
    """Minimal tool shape compatible with the existing ReAct executor."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def spec(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, arguments):
        args = self._parse_arguments(arguments)
        return self._execute(**args)

    def _execute(self, **kwargs):
        raise NotImplementedError("Tool._execute must be implemented by subclasses.")

    def _parse_arguments(self, arguments) -> Dict[str, Any]:
        if arguments is None:
            return {}
        if isinstance(arguments, dict):
            return arguments
        if isinstance(arguments, str):
            text = arguments.strip()
            if not text:
                return {}
            return json.loads(text)
        raise ValueError("Unsupported tool arguments type.")
