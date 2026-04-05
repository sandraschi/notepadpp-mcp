"""FastAPI routes for the Notepad++ MCP web dashboard (tools, chat, skills, fleet)."""

from __future__ import annotations

import asyncio
from typing import Annotated, Any

from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .ai import AIRouter
from .auth import authenticate
from .docs_manifest import get_help_manifest
from .editor_bridge import (
    build_editor_snapshot,
    file_stats_for_path,
)
from .fleet import probe_fleet
from .plugin_catalog import enrich_installed_plugins_disk
from .tools.controller import NotepadPPController

ALLOWED_MCP_INVOKE_TOOLS: frozenset[str] = frozenset(
    {
        "file_ops",
        "text_ops",
        "tab_ops",
        "session_ops",
        "linting_ops",
        "display_ops",
        "plugin_ops",
        "status_ops",
    }
)


def _tool_result_to_dict(result: Any) -> dict[str, Any]:
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        return sc
    return {"error": "unexpected_tool_result", "detail": str(result)}


class ToolInvokeBody(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


def setup_webapp(
    app: FastAPI,
    mcp_app: FastMCP,
    controller: NotepadPPController | None = None,
) -> None:
    """Register standard SOTA web endpoints for the Notepad++ MCP dashboard."""
    ai_router = AIRouter(mcp_app)

    @app.get("/api/health")
    async def health() -> dict:
        """Public liveness probe (no auth) for fleet scanners and the Vite dev proxy."""
        return {
            "ok": True,
            "service": "notepadpp-mcp",
            "mcp": getattr(mcp_app, "name", "Notepad++ MCP Server"),
        }

    @app.get("/api/status")
    async def get_status(user: str = Depends(authenticate)) -> dict:
        return {"status": "connected", "user": user, "mcp": mcp_app.name}

    @app.get("/api/mcp/meta")
    async def mcp_meta(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Server name, instructions preview, and registered MCP tool names."""
        _ = user
        tools = await ai_router.get_tools_list()
        instr = getattr(mcp_app, "instructions", "") or ""
        return {
            "name": getattr(mcp_app, "name", "Notepad++ MCP Server"),
            "instructions_preview": instr[:1200],
            "instructions_length": len(instr),
            "tool_count": len(tools),
            "tools": tools,
        }

    @app.get("/api/docs/overview")
    async def docs_overview(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Help page manifest: Markdown sections + REST table."""
        _ = user
        return get_help_manifest()

    @app.get("/api/http/routes")
    async def http_routes_list(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Enumerated FastAPI routes (for API reference)."""
        _ = user
        rows: list[dict[str, str]] = []
        for route in app.routes:
            methods = getattr(route, "methods", None) or set()
            path = getattr(route, "path", None)
            if not path:
                continue
            if str(path).startswith("/openapi") or path in {"/docs", "/redoc"}:
                continue
            for m in sorted(methods):
                if m in ("HEAD", "OPTIONS"):
                    continue
                rows.append({"method": m, "path": str(path)})
        rows.sort(key=lambda x: (x["path"], x["method"]))
        return {"routes": rows}

    @app.get("/api/diagnostics")
    async def diagnostics_bundle(user: str = Depends(authenticate)) -> dict[str, Any]:
        """status_ops health_check + system_status in one call."""
        _ = user
        hc = await mcp_app.call_tool("status_ops", {"operation": "health_check"})
        ss = await mcp_app.call_tool("status_ops", {"operation": "system_status"})
        return {
            "health_check": _tool_result_to_dict(hc),
            "system_status": _tool_result_to_dict(ss),
        }

    @app.get("/api/file/stats")
    async def api_file_stats(
        path: str = Query(..., min_length=1, description="Absolute or resolvable file path"),
        user: str = Depends(authenticate),
    ) -> dict[str, Any]:
        """Filesystem stats for an arbitrary path (size, mtime, line count when small enough)."""
        _ = user
        return {"success": True, "stats": file_stats_for_path(path)}

    @app.post("/api/mcp/invoke")
    async def mcp_tool_invoke(
        body: Annotated[ToolInvokeBody, Body()],
        user: str = Depends(authenticate),
    ) -> dict[str, Any]:
        """Invoke a whitelisted MCP tool by name with JSON arguments (same as MCP call_tool)."""
        _ = user
        if body.tool not in ALLOWED_MCP_INVOKE_TOOLS:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "tool_not_allowed",
                    "allowed": sorted(ALLOWED_MCP_INVOKE_TOOLS),
                },
            )
        result = await mcp_app.call_tool(body.tool, body.arguments)
        return _tool_result_to_dict(result)

    @app.get("/api/editor")
    async def editor_live(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Live Notepad++ window, active file hint, tab_ops, PID, plugins on disk."""
        _ = user
        return await build_editor_snapshot(mcp_app, controller)

    @app.get("/api/plugins/discover")
    async def plugins_discover(
        user: str = Depends(authenticate),
        search_term: str | None = Query(None, alias="q"),
        category: str | None = None,
        limit: int = Query(30, ge=1, le=200),
    ) -> dict[str, Any]:
        """Official nppPluginList JSON (same as plugin_ops discover)."""
        _ = user
        result = await mcp_app.call_tool(
            "plugin_ops",
            {
                "operation": "discover",
                "search_term": search_term,
                "category": category,
                "limit": limit,
            },
        )
        return _tool_result_to_dict(result)

    @app.get("/api/plugins/installed")
    async def plugins_installed(user: str = Depends(authenticate)) -> dict[str, Any]:
        """DLLs under N++ plugin dirs plus official pl.x64.json descriptions when folder-name matches."""
        _ = user
        if not controller:
            return {
                "success": False,
                "error": "windows_api_unavailable",
                "count": 0,
                "plugins": [],
            }
        merged = await asyncio.to_thread(
            enrich_installed_plugins_disk, controller.notepadpp_exe
        )
        return {"success": True, **merged}

    class PluginInstallBody(BaseModel):
        plugin_name: str = Field(..., min_length=1)

    @app.post("/api/plugins/install")
    async def plugins_install(
        body: Annotated[PluginInstallBody, Body()],
        user: str = Depends(authenticate),
    ) -> dict[str, Any]:
        """Triggers plugin_ops install (UI automation toward Plugin Admin — see tool response)."""
        _ = user
        result = await mcp_app.call_tool(
            "plugin_ops",
            {"operation": "install", "plugin_name": body.plugin_name.strip()},
        )
        return _tool_result_to_dict(result)

    @app.get("/api/tools")
    async def list_tools(user: str = Depends(authenticate)) -> dict:
        tools = await ai_router.get_tools_list()
        return {"tools": tools}

    @app.post("/api/chat")
    async def chat(query: str = Body(..., embed=True), user: str = Depends(authenticate)) -> dict:
        response = await ai_router.route_query(query)
        return {"response": response}

    @app.get("/api/skills")
    async def list_skills(user: str = Depends(authenticate)) -> dict:
        """List skills exposed by the MCP server (skill:// URIs ending with /SKILL.md)."""
        resources = await mcp_app.list_resources()
        skills: list[dict[str, str]] = []
        for r in resources:
            raw = getattr(r, "uri", None) or getattr(r, "name", "")
            uri = str(raw) if raw is not None else ""
            if uri.startswith("skill://") and "/SKILL.md" in uri:
                name = uri.replace("skill://", "").split("/")[0]
                skills.append({"name": name, "uri": uri})
        return {"skills": skills}

    @app.get("/api/skills/{name}")
    async def get_skill_content(name: str, user: str = Depends(authenticate)) -> dict:
        """Return the main skill instruction content (SKILL.md) for the given skill name."""
        uri = f"skill://{name}/SKILL.md"
        try:
            parts = await mcp_app.read_resource(uri)
            text = ""
            if parts:
                for p in parts:
                    if hasattr(p, "text"):
                        text += getattr(p, "text", "") or ""
                    elif isinstance(p, dict) and "text" in p:
                        text += str(p["text"])
            return {"name": name, "uri": uri, "content": text or "(empty)"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Skill not found: {name}") from e

    @app.get("/api/fleet")
    async def fleet_status(user: str = Depends(authenticate)) -> dict:
        """Probe registered fleet ports for /api/health (Apps Hub)."""
        entries, fleet_meta = await probe_fleet()
        return {"fleet": entries, "fleet_meta": fleet_meta}
