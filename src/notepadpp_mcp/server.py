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
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI
from fastmcp import Context, FastMCP
from prefab_ui.components import Card, CardContent, CardHeader, Column, DataTable, DataTableColumn, Text
from pydantic import Field

from .fleet import probe_fleet
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
    sampling_handler=sampling_handler,
    sampling_handler_behavior="fallback" if _USE_CLIENT_SAMPLING else "always",
    on_duplicate="replace",
    strict_input_validation=True,
)


@mcp.lifespan()
async def server_lifespan(server: FastMCP):
    """FastMCP native lifespan for server-level lifecycle tasks."""
    logger.info("Notepad++ MCP native lifespan starting")
    yield
    logger.info("Notepad++ MCP native lifespan stopping")


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
                except Exception as e:
                    logger.warning("Failed to add bridge proxy for %s: %s", url, e)
    except ImportError:
        logger.warning("fastmcp.server.create_proxy not available, skipping bridge configuration")

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
async def suggest_notepad_plan(
    goal: Annotated[str, Field(description="What to achieve in Notepad++ (natural language goal).")],
    ctx: Context,
) -> dict[str, Any]:
    """SUGGEST_NOTEPAD_PLAN — Short plan via MCP sampling (requires reachable LLM).

    ## Return Format
    {"success": bool, "plan": str, "goal": str}

    ## Examples
    suggest_notepad_plan(goal="Set up a Python linting workflow for my scripts")

    Notes:
     - Requires MCP sampling (client LLM or server-side Ollama via NOTEPADPP_SAMPLING_*); returns error dict when sampling is unavailable.
    """
    result = await ctx.sample(
        messages=(
            f"Goal for Notepad++ on Windows (MCP tools: file_ops, text_ops, tab_ops, session_ops, "
            f"linting_ops, display_ops, plugin_ops, status_ops):\n{goal[:3000]}\n\n"
            "Reply with a numbered plan (3-7 steps). Name tools explicitly. No JSON."
        ),
        system_prompt="Be concise. Plain text only.",
        max_tokens=500,
    )
    text = getattr(result, "text", None) or str(result)
    return {"success": True, "plan": text.strip(), "goal": goal}


@mcp.tool(app=True)
async def notepad_dashboard() -> Column:
    """NOTEPAD_DASHBOARD — Show the MCP server status, open tab info, and fleet status in a rich UI dashboard.

    PORTMANTEAU PATTERN RATIONALE: Integrates editor metrics, tab details, and fleet health into a unified interface (TOOL_DESIGN_STANDARDS.md §1).

    ## Return Format
    Prefab Column: Cards for bridge status, active editor tab, and fleet table (plain-text fallback lists the same data).

    ## Examples
    notepad_dashboard()
    """
    # 1. Notepad++ running status
    status_details = []
    if controller:
        try:
            is_running = await controller.ensure_notepadpp_running()
            if is_running:
                status_details = [
                    "Status: Notepad++ is running",
                    f"Main Window Handle: {controller.hwnd}",
                    f"Scintilla Window Handle: {controller.scintilla_hwnd}",
                    f"Executable Path: {controller.notepadpp_exe or 'Unknown'}",
                ]
            else:
                status_details = ["Status: Notepad++ is not running"]
        except Exception as e:
            status_details = [f"Status: Verification failed ({e})"]
    else:
        status_details = ["Status: Windows API unavailable"]

    # 2. Get active tab information
    tab_details = []
    if controller and getattr(controller, "hwnd", None):
        try:
            window_text = await controller.get_window_text(controller.hwnd)
            filename = "Untitled"
            if " - Notepad++" in window_text:
                filename = window_text.split(" - Notepad++")[0]
            is_modified = "*" in window_text
            tab_details = [
                f"Active File: {filename}",
                f"Unsaved Changes: {'Yes' if is_modified else 'No'}",
                f"Full Window Title: {window_text}",
            ]
        except Exception:
            tab_details = ["Active File: None or inaccessible"]
    else:
        tab_details = ["Active File: None or inaccessible"]

    # 3. Probe fleet ports
    fleet_rows = []
    try:
        entries, _meta = await probe_fleet()
        for entry in entries:
            fleet_rows.append(
                {
                    "port": entry.get("port"),
                    "url": entry.get("url"),
                    "status": "Online" if entry.get("reachable") else "Offline",
                }
            )
    except Exception as e:
        fleet_rows = [{"port": 0, "url": f"Probe error: {e}", "status": "Error"}]

    # Combine into prefab-ui components
    return Column(
        children=[
            Card(
                children=[
                    CardHeader(children=[Text("Notepad++ MCP Bridge Status")]),
                    CardContent(children=[Text("\n".join(status_details))]),
                ]
            ),
            Card(
                children=[
                    CardHeader(children=[Text("Active Editor Tab")]),
                    CardContent(children=[Text("\n".join(tab_details))]),
                ]
            ),
            Card(
                children=[
                    CardHeader(children=[Text("Fleet Status")]),
                    CardContent(
                        children=[
                            DataTable(
                                columns=[
                                    DataTableColumn(key="port", header="Port", sortable=True),
                                    DataTableColumn(key="url", header="URL"),
                                    DataTableColumn(key="status", header="Status"),
                                ],
                                rows=fleet_rows,
                                search=True,
                            )
                        ]
                    ),
                ]
            ),
        ]
    )


# —— Agentic workflow (register after portmanteau tools) ——
register_agentic_notepad_workflow(mcp)


@mcp.tool(annotations={"destructive": True})
async def notepadpp_shutdown(confirm: bool = False) -> dict[str, Any]:
    """NOTEPADPP_SHUTDOWN — Stop the Notepad++ MCP bridge process (agent-initiated exit).

    [RATIONALE] Agents that manage server lifecycle need a way to stop the bridge
    cleanly (same pattern as filesystem-mcp server_shutdown).

    ## Return Format
    {"success": bool, "message": str}

    ## Examples
    notepadpp_shutdown(confirm=True)

    Notes:
     - confirm=True is required; a false call returns a hint.
     - HTTP mode exits the uvicorn process after a short delay; stdio mode exits the MCP server.
    """
    if not confirm:
        return {
            "success": False,
            "message": "Shutdown requires confirm=True.",
            "suggestions": ["Call notepadpp_shutdown(confirm=True) to stop the server."],
        }
    logger.warning("Shutdown requested via MCP tool")

    async def _do_exit() -> None:
        await asyncio.sleep(0.8)
        os._exit(0)

    _shutdown_task = asyncio.create_task(_do_exit())
    _ = _shutdown_task
    return {"success": True, "message": "Notepad++ MCP bridge shutting down."}


# ASGI app: FastAPI bridge + MCP streamable HTTP at /mcp
_mcp_http = mcp.http_app(path="/")
app = FastAPI(title="Notepad++ MCP", lifespan=_mcp_http.lifespan)
setup_webapp(app, mcp, controller)
app.mount("/mcp", _mcp_http)


def run() -> None:
    """Entry point: stdio MCP or FastAPI + uvicorn on the bridge port."""
    parser = argparse.ArgumentParser(description="Notepad++ MCP Server")
    parser.add_argument("--http", action="store_true", help="Run FastAPI bridge + MCP HTTP on MCP_PORT")
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
