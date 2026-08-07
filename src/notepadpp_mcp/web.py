"""FastAPI routes for the Notepad++ MCP web dashboard (tools, chat, skills, fleet)."""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import deque
from typing import Annotated, Any
from uuid import uuid4

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
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


class ActivityLog:
    """In-memory ring-buffer activity log (fleet pattern: /api/logs*)."""

    def __init__(self, max_entries: int = 2000) -> None:
        self.max_entries = max_entries
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def add(self, level: str, kind: str, detail: str, meta: dict[str, Any] | None = None) -> str:
        eid = f"{time.time():.6f}.{uuid4().hex[:6]}"
        self._entries.append(
            {
                "id": eid,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "level": level.upper(),
                "kind": kind,
                "detail": detail,
                "meta": meta or {},
            }
        )
        return eid

    def info(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("INFO", kind, detail, meta)

    def warn(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("WARNING", kind, detail, meta)

    def error(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("ERROR", kind, detail, meta)

    def query(
        self,
        limit: int = 50,
        offset: int = 0,
        level: str | None = None,
        kind: str | None = None,
        search: str | None = None,
        sort: str = "desc",
    ) -> dict[str, Any]:
        entries = list(self._entries)
        if level:
            order = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            minimum = order.get(level.upper(), 1)
            entries = [e for e in entries if order.get(e["level"], 1) >= minimum]
        if kind:
            entries = [e for e in entries if e["kind"] == kind]
        if search:
            q = search.lower()
            entries = [e for e in entries if q in e["detail"].lower()]
        entries.sort(key=lambda e: e["id"], reverse=(sort == "desc"))
        total = len(entries)
        page = entries[offset : offset + limit]
        return {
            "entries": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "max_entries": self.max_entries,
            "sort": sort,
        }

    def stats(self) -> dict[str, Any]:
        levels: dict[str, int] = {}
        kinds: dict[str, int] = {}
        for e in self._entries:
            levels[e["level"]] = levels.get(e["level"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        return {
            "total": len(self._entries),
            "max_entries": self.max_entries,
            "levels": levels,
            "kinds": kinds,
        }

    def export(self, format: str = "json", **filters: Any) -> str:
        result = self.query(limit=self.max_entries, **filters)
        if format == "csv":
            import csv
            import io

            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["id", "timestamp", "level", "kind", "detail", "meta"])
            for e in result["entries"]:
                writer.writerow([e["id"], e["timestamp"], e["level"], e["kind"], e["detail"], json.dumps(e["meta"])])
            return buf.getvalue()
        return json.dumps(result["entries"], indent=2)

    def clear(self) -> None:
        self._entries.clear()


LLM_PROVIDER_PORTS: dict[str, int] = {"ollama": 11434, "lm_studio": 1234, "vllm": 8000}


async def _probe_llm_providers() -> dict[str, Any]:
    """Probe local LLM endpoints (Ollama / LM Studio / vLLM) - fleet glom-on pattern."""
    providers: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, port in LLM_PROVIDER_PORTS.items():
            try:
                if name == "ollama":
                    r = await client.get(f"http://127.0.0.1:{port}/api/tags")
                    r.raise_for_status()
                    models = [{"name": m.get("name", "")} for m in r.json().get("models", [])]
                else:
                    r = await client.get(f"http://127.0.0.1:{port}/v1/models")
                    r.raise_for_status()
                    models = [{"name": m.get("id", "")} for m in r.json().get("data", [])]
                providers[name] = {
                    "base": f"http://127.0.0.1:{port}",
                    "port": port,
                    "models": [m for m in models if m.get("name")],
                }
            except Exception:
                providers[name] = {"base": f"http://127.0.0.1:{port}", "port": port, "models": []}
    return providers


def setup_webapp(
    app: FastAPI,
    mcp_app: FastMCP,
    controller: NotepadPPController | None = None,
) -> None:
    """Register standard SOTA web endpoints for the Notepad++ MCP dashboard."""
    ai_router = AIRouter(mcp_app)

    # Fleet CORS standard (tauri_nsis_building.md / CORS_STANDARD.md):
    # explicit Tauri origins + unconditional LAN/Tailscale/localhost regex.
    _tauri = os.environ.get("NOTEPADPP_MCP_TAURI", "").lower() in ("1", "true", "yes")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:10814",
            "http://127.0.0.1:10814",
            "http://localhost:10815",
            "http://127.0.0.1:10815",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        ],
        allow_origin_regex=(
            r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost"
            r"|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _ = _tauri

    activity_log = ActivityLog()
    app.state.activity_log = activity_log

    def _log_endpoints() -> None:
        """Register /api/logs* ring-buffer endpoints on the bridge app."""

        @app.get("/api/logs")
        async def get_logs(
            request: Request,
            limit: int = 50,
            offset: int = 0,
            level: str | None = None,
            kind: str | None = None,
            search: str | None = None,
            sort: str = "desc",
        ) -> dict[str, Any]:
            log: ActivityLog = request.app.state.activity_log
            return log.query(limit=limit, offset=offset, level=level, kind=kind, search=search, sort=sort)

        @app.get("/api/logs/stats")
        async def logs_stats(request: Request) -> dict[str, Any]:
            log: ActivityLog = request.app.state.activity_log
            return log.stats()

        @app.get("/api/logs/export")
        async def logs_export(
            request: Request,
            format: str = "json",
            level: str | None = None,
            kind: str | None = None,
            search: str | None = None,
        ) -> Response:
            log: ActivityLog = request.app.state.activity_log
            content = log.export(format=format, level=level, kind=kind, search=search)
            media = "text/csv" if format == "csv" else "application/json"
            return Response(
                content=content,
                media_type=media,
                headers={"Content-Disposition": f'attachment; filename="logs.{format}"'},
            )

        @app.delete("/api/logs")
        async def clear_logs(request: Request) -> dict[str, Any]:
            log: ActivityLog = request.app.state.activity_log
            log.clear()
            return {"success": True, "message": "Logs cleared."}

    _log_endpoints()

    @app.get("/api/health")
    async def health() -> dict:
        """Public liveness probe (no auth) for fleet scanners and the Vite dev proxy."""
        activity_log.info("health", "liveness probe")
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
        merged = await asyncio.to_thread(enrich_installed_plugins_disk, controller.notepadpp_exe)
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

    class ChatBody(BaseModel):
        query: str = Field(..., min_length=1, max_length=8000)
        context: str | None = Field(None, max_length=4000)

    @app.post("/api/chat")
    async def chat(
        body: Annotated[ChatBody, Body()],
        user: str = Depends(authenticate),
    ) -> dict:
        response = await ai_router.route_query(body.query, context=body.context)
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
                        text += str(p.get("text", ""))
            return {"name": name, "uri": uri, "content": text or "(empty)"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Skill not found: {name}") from e

    @app.get("/api/fleet")
    async def fleet_status(user: str = Depends(authenticate)) -> dict:
        """Probe registered fleet ports for /api/health (Apps Hub)."""
        entries, fleet_meta = await probe_fleet()
        return {"fleet": entries, "fleet_meta": fleet_meta}

    # ---- CUA-NSIS v1 aliases (cua_nsis_smoke_testing.md / tauri_nsis_building.md) ----

    @app.get("/api/v1/health")
    async def health_v1() -> dict:
        """CUA-NSIS smoke-test health endpoint."""
        return await health()

    @app.get("/api/v1/diagnostics")
    async def diagnostics_v1(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Full diagnostics: tool list, system info, errors (CUA-NSIS standard shape)."""
        _ = user
        hc = await mcp_app.call_tool("status_ops", {"operation": "health_check"})
        ss = await mcp_app.call_tool("status_ops", {"operation": "system_status"})
        tools = await ai_router.get_tools_list()
        return {
            "status": "ok",
            "server": "notepadpp-mcp",
            "version": getattr(mcp_app, "version", "0.2.0"),
            "uptime_seconds": round(time.time() - _start_ts),
            "tool_count": len(tools),
            "tools": [{"name": t["name"]} for t in tools],
            "system": {"windows": True},
            "errors": [],
            "health_check": _tool_result_to_dict(hc),
            "system_status": _tool_result_to_dict(ss),
        }

    @app.get("/api/v1/system/info")
    async def system_info_v1(user: str = Depends(authenticate)) -> dict[str, Any]:
        """CUA feature-route smoke target."""
        _ = user
        ss = await mcp_app.call_tool("status_ops", {"operation": "system_status"})
        return _tool_result_to_dict(ss)

    # ---- Local LLM discovery (glom-on) ----

    @app.get("/api/llm/providers")
    async def llm_providers(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Probe Ollama / LM Studio / vLLM and return detected providers with models."""
        _ = user
        providers = await _probe_llm_providers()
        return {"providers": providers}

    @app.get("/api/llm/discover")
    async def llm_discover(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Alias of /api/llm/providers for the Chat page provider status indicator."""
        _ = user
        providers = await _probe_llm_providers()
        detected = {k: v for k, v in providers.items() if v["models"]}
        return {"providers": providers, "detected": detected}

    # ---- Self-termination (agentic_macros.md: shutdown tool/endpoint) ----

    @app.post("/api/shutdown")
    async def shutdown(user: str = Depends(authenticate)) -> dict[str, Any]:
        """Graceful shutdown of the bridge process (restart via launcher/operator)."""
        _ = user
        activity_log.warn("shutdown", "Bridge shutdown requested via /api/shutdown")

        async def _do_exit() -> None:
            await asyncio.sleep(0.8)
            os._exit(0)

        _shutdown_task = asyncio.create_task(_do_exit())
        _ = _shutdown_task
        return {"success": True, "message": "Bridge shutting down."}


_start_ts = time.time()
