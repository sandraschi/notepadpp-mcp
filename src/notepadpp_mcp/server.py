"""
Notepad++ MCP Server — FastMCP 3.1

- Portmanteau tools (file_ops, text_ops, …), sampling (Ollama-compatible HTTP or client LLM),
  prompts, skill:// resources, and agentic_notepad_workflow (SEP-1577 sample_step).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastmcp import Context, FastMCP

from .sampling import NotepadSamplingHandler
from .tools.agentic_notepad_workflow import register_agentic_notepad_workflow
from .tools.display_operations import DisplayOperationsTool

# Tool imports from modular subpackage
from .tools.file_operations import FileOperationsTool
from .tools.linting_operations import LintingOperationsTool
from .tools.plugin_operations import PluginOperationsTool
from .tools.session_operations import SessionOperationsTool
from .tools.status_operations import StatusOperationsTool
from .tools.tab_operations import TabOperationsTool
from .tools.text_operations import TextOperationsTool

# Windows-specific imports for controller
try:
    import win32api  # noqa: F401
    import win32con  # noqa: F401
    import win32gui  # noqa: F401

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Import the Notepad++ controller
from .tools.controller import NotepadPPController
from .web import setup_webapp

logger = logging.getLogger(__name__)

# Global controller instance
controller = NotepadPPController() if WINDOWS_AVAILABLE else None

_USE_CLIENT_SAMPLING = os.getenv("NOTEPADPP_SAMPLING_USE_CLIENT_LLM", "").lower() in (
    "1",
    "true",
    "yes",
)

sampling_handler = NotepadSamplingHandler()


@asynccontextmanager
async def server_lifespan(_mcp_instance: FastMCP):
    """FastMCP 3.1 lifespan (extend for background services if needed)."""
    yield


mcp = FastMCP(
    "Notepad++ MCP Server",
    version="0.2.0",
    instructions="""Notepad++ MCP (Windows): FastMCP 3.1 portmanteau tools (AGENT_PROTOCOLS / TOOL_DESIGN_STANDARDS).

Primary tools: file_ops, text_ops, tab_ops, session_ops, linting_ops, display_ops, plugin_ops, status_ops.
Meta: agentic_notepad_workflow (sampling + tools), suggest_notepad_plan (sampling).

Sampling: set NOTEPADPP_SAMPLING_BASE_URL (default http://127.0.0.1:11434/v1) and NOTEPADPP_SAMPLING_MODEL for server-side Ollama,
or NOTEPADPP_SAMPLING_USE_CLIENT_LLM=1 with sampling_handler_behavior fallback so the MCP host runs the LLM.

Skills: skill://notepadpp-mcp/SKILL.md. Prompts: prompt://notepadpp-mcp/*.
""",
    lifespan=server_lifespan,
    sampling_handler=sampling_handler,
    sampling_handler_behavior="fallback" if _USE_CLIENT_SAMPLING else "always",
    on_duplicate="replace",
    strict_input_validation=True,
)

# MCP Bridge — Proxy external MCP servers via MCP_BRIDGE_URLS
_bridge_proxies: list[str] = []
bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if bridge_urls:
    try:
        from fastmcp.server import create_proxy
        for url in bridge_urls.split(","):
            url = url.strip()
            if url:
                try:
                    mcp.add_provider(create_proxy(url))
                    _bridge_proxies.append(url)
                except Exception:
                    pass
    except ImportError:
        pass

# Initialize tool managers
file_tool = FileOperationsTool(mcp, controller)
text_tool = TextOperationsTool(mcp, controller)
status_tool = StatusOperationsTool(mcp, controller, logger=logger)
tab_tool = TabOperationsTool(mcp, controller)
session_tool = SessionOperationsTool(mcp, controller)
linting_tool = LintingOperationsTool(mcp, controller)
display_tool = DisplayOperationsTool(mcp, controller)
plugin_tool = PluginOperationsTool(mcp, controller)

# Register all tools
file_tool.register_tools()
text_tool.register_tools()
status_tool.register_tools()
tab_tool.register_tools()
session_tool.register_tools()
linting_tool.register_tools()
display_tool.register_tools()
plugin_tool.register_tools()


# —— Resources (FastMCP 3.1) ——


@mcp.resource("resource://notepadpp-mcp/capabilities")
def resource_capabilities() -> str:
    """Server capabilities: tools, sampling, prompts, skills."""
    return (
        "Notepad++ MCP 0.2.0 (FastMCP 3.1)\n"
        "- Tools: file_ops, text_ops, tab_ops, session_ops, linting_ops, display_ops, plugin_ops, status_ops\n"
        "- Meta: agentic_notepad_workflow, suggest_notepad_plan\n"
        "- Sampling: NOTEPADPP_SAMPLING_BASE_URL, NOTEPADPP_SAMPLING_MODEL; optional NOTEPADPP_SAMPLING_USE_CLIENT_LLM=1\n"
        "- Resources: resource://notepadpp-mcp/capabilities; skills under skill://notepadpp-mcp/SKILL.md\n"
        "- Prompts: prompt://notepadpp-mcp/workflow-guide, session-focus, plugin-discovery\n"
    )


# —— Prompts ——


@mcp.prompt("prompt://notepadpp-mcp/workflow-guide")
def prompt_workflow_guide() -> str:
    """How to combine tools for common Notepad++ tasks."""
    return """Plan a Notepad++ automation using MCP tools:
1. status_ops(health_check) if unsure the editor is reachable.
2. file_ops(info) for active document hints from the window title; file_ops(open, file_path=...) to load a path.
3. text_ops(insert|find) for buffer edits; tab_ops(list|switch|close) for tabs.
4. linting_ops(python|javascript|json|markdown, file_path=...) on saved files.
5. plugin_ops(discover|install|list|execute) for the plugin ecosystem (install uses UI automation).
Use agentic_notepad_workflow when the user wants multi-step orchestration and sampling is available."""


@mcp.prompt("prompt://notepadpp-mcp/session-focus")
def prompt_session_focus(task: str) -> str:
    """User message template focused on one editing task."""
    return (
        f"Focus on this Notepad++ task only: {task}\n"
        "Prefer file_ops and text_ops first; then linting_ops if a file path is known."
    )


@mcp.prompt("prompt://notepadpp-mcp/plugin-discovery")
def prompt_plugin_discovery(topic: str) -> str:
    """Guide discovery from the official plugin list."""
    return (
        f"Search the official Notepad++ plugin list for: {topic}\n"
        "Call plugin_ops(operation='discover', search_term=..., limit=20). "
        "For install, use plugin_ops(operation='install', plugin_name=...) and expect Plugin Admin UI involvement."
    )


# —— Skills directory (skill://notepadpp-mcp/SKILL.md) ——

try:
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    _skills_root = Path(__file__).resolve().parent / "skills"
    if _skills_root.is_dir():
        mcp.add_provider(SkillsDirectoryProvider(roots=[_skills_root]))
except ImportError:
    logger.warning("SkillsDirectoryProvider not available; skills not mounted.")
except OSError as e:
    logger.warning("Skills provider skipped: %s", e)


# —— Sampling helpers ——


@mcp.tool()
async def suggest_notepad_plan(goal: str, ctx: Context) -> dict[str, Any]:
    """SUGGEST_NOTEPAD_PLAN — Short plan via MCP sampling (requires reachable LLM).

    Args:
        goal: What to achieve in Notepad++.

    Returns:
        dict with success, plan text, and goal echo.
    """
    result = await ctx.sample(
        messages=(
            f"Goal for Notepad++ on Windows (MCP tools: file_ops, text_ops, tab_ops, session_ops, "
            f"linting_ops, display_ops, plugin_ops, status_ops):\n{goal[:3000]}\n\n"
            "Reply with a numbered plan (3–7 steps). Name tools explicitly. No JSON."
        ),
        system_prompt="Be concise. Plain text only.",
        max_tokens=500,
    )
    text = getattr(result, "text", None) or str(result)
    return {"success": True, "plan": text.strip(), "goal": goal}


# —— Agentic workflow (register after portmanteau tools) ——
register_agentic_notepad_workflow(mcp)


# ASGI app: FastAPI bridge + MCP streamable HTTP at /mcp
_mcp_http = mcp.http_app(path="/")
app = FastAPI(title="Notepad++ MCP", lifespan=_mcp_http.lifespan)
setup_webapp(app, mcp, controller)
app.mount("/mcp", _mcp_http)


def run() -> None:
    """Entry point: stdio MCP or FastAPI + uvicorn on the bridge port."""
    parser = argparse.ArgumentParser(description="Notepad++ MCP Server")
    parser.add_argument(
        "--http", action="store_true", help="Run FastAPI bridge + MCP HTTP on MCP_PORT"
    )
    parser.add_argument("--port", type=int, default=10815, help="Port for the bridge (HTTP mode)")
    args, _unknown = parser.parse_known_args()

    if not WINDOWS_AVAILABLE:
        logger.error("This MCP server requires Windows and pywin32")
        sys.exit(1)

    if args.http:
        import uvicorn

        logger.info("Starting Notepad++ MCP bridge on http://127.0.0.1:%s (MCP at /mcp)", args.port)
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")
    else:
        asyncio.run(mcp.run_stdio_async())


def main() -> None:
    """Console script entry (alias for run)."""
    run()


if __name__ == "__main__":
    run()
