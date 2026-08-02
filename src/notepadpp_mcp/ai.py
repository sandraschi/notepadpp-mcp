"""Lightweight AI router for the web dashboard (optional local LLM)."""

import logging
import os
from typing import Any

import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


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
    """AI router: natural-language chat against a local LLM (Ollama-compatible HTTP)."""

    def __init__(self, mcp_app: FastMCP):
        self.mcp = mcp_app
        self.provider = os.getenv("AI_PROVIDER", "ollama")
        self.endpoint = os.getenv("AI_ENDPOINT", "http://127.0.0.1:11434/api/generate")
        self.model = os.getenv("AI_MODEL", "llama3.1-8b")

    async def route_query(self, query: str, context: str | None = None) -> str:
        """Send the query to the configured local LLM; fall back to a routing hint on failure."""
        tool_hint = (
            "Available tools: file_ops, text_ops, tab_ops, session_ops, linting_ops, "
            "display_ops, plugin_ops, status_ops."
        )
        prefix = f"{context.strip()}\n\n" if context and context.strip() else ""
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                r = await client.post(
                    self.endpoint,
                    json={
                        "model": self.model,
                        "prompt": (
                            f"{prefix}You are the Notepad++ MCP assistant. {tool_hint}\n"
                            "Answer concisely. If the user asks to perform an action, "
                            "describe the exact MCP tool call to use.\n\n"
                            f"User: {query[:4000]}"
                        ),
                        "stream": False,
                    },
                )
                r.raise_for_status()
                data = r.json()
                text = data.get("response") or data.get("content") or ""
                if text:
                    return text.strip()
                logger.warning("LLM returned empty response from %s", self.endpoint)
        except Exception as e:
            logger.warning("LLM unavailable (%s): %s", type(e).__name__, e)
        return (
            f"Local LLM is not reachable at {self.endpoint} (model {self.model}). "
            f"Start Ollama (or set AI_ENDPOINT/AI_MODEL in .env) to enable chat. "
            f"{tool_hint}"
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
