"""Structured documentation for the HTTP dashboard Help page (single source of truth)."""

from __future__ import annotations

from typing import Any


def get_help_manifest() -> dict[str, Any]:
    """Sections and API tables for the webapp Help UI."""
    return {
        "title": "Notepad++ MCP — documentation",
        "version": 1,
        "sections": [
            {
                "id": "mcp_server",
                "title": "MCP server (FastMCP)",
                "body_md": """## Role
The Python package exposes a **FastMCP** server named **Notepad++ MCP Server**. It runs on **Windows** with **pywin32** and automates the real Notepad++ process (window messages, menus, clipboard).

## Transports
- **stdio** (default for Claude Desktop / many MCP clients): `mcp.run_stdio_async()`.
- **HTTP bridge**: FastAPI + **uvicorn** on **127.0.0.1:10815** with MCP streamable HTTP mounted at **`/mcp`**.

## Portmanteau tools
All automation goes through consolidated tools (one tool name, `operation` parameter):
| Tool | Typical operations |
|------|---------------------|
| `file_ops` | `open`, `new`, `save`, `info` |
| `text_ops` | `insert`, `find` |
| `tab_ops` | `list`, `switch`, `close` |
| `session_ops` | `save`, `load`, `list` |
| `linting_ops` | `python`, `javascript`, `json`, `markdown`, `tools` |
| `display_ops` | display / visibility fixes |
| `plugin_ops` | `discover`, `install`, `list`, `execute` |
| `status_ops` | `help`, `system_status`, `health_check` |

Responses follow the project pattern: `success`, `summary`/`message`, `result`, and `error`/`recovery_options` on failure.

## Limitations
- **Tab list** is partial without full N++ plugin API: the server often sees the **active** tab via the **window title**.
- **Plugin install** uses UI automation toward **Plugin Admin**, not a hidden HTTP API (Notepad++ does not expose one).
""",
            },
            {
                "id": "webapp",
                "title": "Web dashboard (web_sota)",
                "body_md": """## Stack
**Vite + React + TypeScript** on **10814**, talking to the FastAPI bridge on **10815** via the dev **proxy** for `/api` and `/mcp`.

## Auth
Browser calls to `/api/*` use **HTTP Basic** credentials. Set on the server:
- `MCP_WEB_USER`
- `MCP_WEB_PASSWORD`

Mirror for the static dev server (optional):
- `VITE_MCP_WEB_USER`
- `VITE_MCP_WEB_PASSWORD`

## Pages
| Page | Purpose |
|------|---------|
| Dashboard | Bridge health, tool count, **live Notepad++ snapshot** (title, PID, file stats when path is known) |
| Editor | Focused **file name + on-disk stats** |
| Plugins | Installed DLL scan + official catalog search |
| Operations | Call MCP tools through the **HTTP invoke** bridge |
| Diagnostics | `status_ops` health + system snapshot |
| Tools Hub | MCP tool list with docstrings |
| Apps / Fleet | Other MCP apps health |

## Startup (typical)
```text
uv run uvicorn notepadpp_mcp.server:app --host 127.0.0.1 --port 10815
```
```text
cd web_sota
.\\start.ps1
```
""",
            },
            {
                "id": "notepad",
                "title": "Notepad++ integration",
                "body_md": """## What is automated
- Finding the main **Notepad++** window and the **Scintilla** child control.
- Optional **auto-start** if `NOTEPADPP_AUTO_START` is true (default).
- **Window title** is the primary source for the **active file name** (and `*` for modified).

## When file stats appear
If the title bar contains a **real path** that exists on disk (e.g. `D:\\\\work\\\\file.py - Notepad++`), the bridge resolves it and reports **size**, **mtime**, **line count** (for files under the internal size cap), and **extension**.

If you only see `Untitled` or a bare file name with no path, the server **cannot** stat the file until you save it to a known path or open via **File → Open** so the full path appears in the title.

## Executable discovery
`NOTEPADPP_PATH` overrides auto-detection under Program Files / AppData.
""",
            },
            {
                "id": "plugins",
                "title": "Plugin system",
                "body_md": """## Discovery
**plugin_ops → discover** downloads the official **nppPluginList** JSON from GitHub (same list as Plugin Admin).

## Installed plugins (this webapp)
The **Plugins** page lists **DLLs** under:
- `<Notepad++ dir>\\\\plugins\\\\`
- `%APPDATA%\\\\Notepad++\\\\plugins\\\\`
- `%LOCALAPPDATA%\\\\Notepad++\\\\plugins\\\\`

That is **filesystem truth**, not the live Plugins menu tree.

## Install / execute
- **install** / **execute** use **keyboard/menu automation**. They may require you to finish steps in **Plugin Admin** or confirm dialogs.
- Prefer **Plugin Admin** manually for reliable installs; use MCP when you want scripted *attempts* or discovery at scale.

## REST helpers
- `GET /api/plugins/discover?q=…`
- `GET /api/plugins/installed`
- `POST /api/plugins/install` with JSON `{ "plugin_name": "…" }`
""",
            },
        ],
        "rest_endpoints": [
            {
                "method": "GET",
                "path": "/api/health",
                "auth": False,
                "summary": "Liveness (no auth)",
            },
            {"method": "GET", "path": "/api/status", "auth": True, "summary": "Auth probe"},
            {
                "method": "GET",
                "path": "/api/mcp/meta",
                "auth": True,
                "summary": "Server name, instructions preview, tool list",
            },
            {
                "method": "GET",
                "path": "/api/docs/overview",
                "auth": True,
                "summary": "This manifest + endpoint table",
            },
            {
                "method": "GET",
                "path": "/api/http/routes",
                "auth": True,
                "summary": "Enumerated FastAPI routes",
            },
            {
                "method": "GET",
                "path": "/api/diagnostics",
                "auth": True,
                "summary": "status_ops health_check + system_status",
            },
            {
                "method": "GET",
                "path": "/api/editor",
                "auth": True,
                "summary": "Live N++ snapshot + file_stats when resolvable",
            },
            {
                "method": "GET",
                "path": "/api/file/stats",
                "auth": True,
                "summary": "Stat arbitrary path (size, mtime, lines)",
            },
            {
                "method": "POST",
                "path": "/api/mcp/invoke",
                "auth": True,
                "summary": "Whitelisted MCP tool invoke",
            },
            {
                "method": "GET",
                "path": "/api/plugins/discover",
                "auth": True,
                "summary": "Official plugin catalog search",
            },
            {
                "method": "GET",
                "path": "/api/plugins/installed",
                "auth": True,
                "summary": "DLLs on disk",
            },
            {
                "method": "POST",
                "path": "/api/plugins/install",
                "auth": True,
                "summary": "plugin_ops install bridge",
            },
            {
                "method": "GET",
                "path": "/api/tools",
                "auth": True,
                "summary": "Tool metadata for Tools Hub",
            },
            {"method": "GET", "path": "/api/fleet", "auth": True, "summary": "Fleet health probes"},
            {
                "method": "GET",
                "path": "/api/skills",
                "auth": True,
                "summary": "List skill:// resources",
            },
            {
                "method": "POST",
                "path": "/api/chat",
                "auth": True,
                "summary": "Placeholder AI router",
            },
        ],
    }
