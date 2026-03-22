"""Lightweight AI router for the web dashboard (optional local LLM)."""

import os
from typing import Any

from fastmcp import FastMCP


def _tool_doc_summary(doc: str, *, max_chars: int = 240) -> str:
    """First non-empty line of a tool docstring, capped (full text still available separately)."""
    if not doc or not doc.strip():
        return ""
    for line in doc.splitlines():
        s = line.strip()
        if s:
            if len(s) <= max_chars:
                return s
            return f"{s[: max_chars - 1].rstrip()}…"
    return ""


class AIRouter:
    """Standard AI router for natural language hints against this MCP server."""

    def __init__(self, mcp_app: FastMCP):
        self.mcp = mcp_app
        self.provider = os.getenv("AI_PROVIDER", "ollama")
        self.endpoint = os.getenv("AI_ENDPOINT", "http://localhost:11434/api/generate")
        self.model = os.getenv("AI_MODEL", "llama3.1-8b")

    async def route_query(self, query: str) -> str:
        """Route natural language query to Notepad++ tools (placeholder until LLM wiring)."""
        return (
            f"AI routing (notepadpp-mcp): interpret “{query[:200]}” and use "
            f"portmanteau tools (file_ops, text_ops, tab_ops, …) via MCP."
        )

    async def get_tools_list(self) -> list[dict[str, Any]]:
        """Return MCP tools with name and description for the Tools Hub."""
        tools = await self.mcp.list_tools()
        out: list[dict[str, Any]] = []
        for t in tools:
            name = getattr(t, "name", str(t))
            desc = getattr(t, "description", "") or ""
            out.append(
                {
                    "name": name,
                    "summary": _tool_doc_summary(desc),
                    "description": desc,
                }
            )
        return out
