# -*- coding: utf-8 -*-
"""Local MCP tool for querying workspace history."""

from __future__ import annotations

import json

from core.history.search_service import WorkspaceHistorySearchService
from integrations.mcp.openai_tool import Tool


class WorkspaceHistoryQueryTool(Tool):
    """Query session history files inside the current workspace."""

    def __init__(self, history_root: str):
        self._service = WorkspaceHistorySearchService(history_root)
        super().__init__(
            name="query_workspace_history",
            description="Search the current workspace history and return matching message excerpts.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword or phrase to search in workspace history."},
                    "limit": {"type": "integer", "description": "Maximum number of matches to return."},
                    "session_name": {"type": "string", "description": "Optional session name or id filter."},
                    "user_id": {"type": "string", "description": "Optional workspace user folder filter."},
                },
                "required": ["query"],
            },
        )

    def _execute(self, **kwargs):
        query = str(kwargs.get("query") or "").strip()
        if not query:
            return "query must not be empty."
        rows = self._service.query(
            text=query,
            limit=int(kwargs.get("limit") or 5),
            session_name=str(kwargs.get("session_name") or "").strip(),
            user_id=str(kwargs.get("user_id") or "").strip(),
        )
        return json.dumps({"success": True, "matches": rows}, ensure_ascii=False, indent=2)
