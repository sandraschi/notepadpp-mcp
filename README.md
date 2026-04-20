# Notepad++ MCP Server

[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.1.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

[![CI](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml)
[![Release](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/sandraschi/notepadpp-mcp/releases)

MCP server for **Notepad++** on **Windows**. Uses **FastMCP 3.1.0** with portmanteau tools (fewer tools, same coverage), optional **HTTP bridge**, **sampling** (Ollama-compatible HTTP or client LLM), **prompts**, **`skill://` resources**, and **agentic** workflows.

**Editor vs this repo:** Notepad++s own strengths (Scintilla, plugins, macros, sessions, ) are separate from what this MCP exposes. See **[docs/EDITOR_AND_MCP_SCOPE.md](docs/EDITOR_AND_MCP_SCOPE.md)** for a clear split and a fuller editor-side overview.

---

## Requirements

| Item | Notes |
|------|--------|
| OS | Windows 10/11 (64-bit) |
| Editor | Notepad++ 8+ installed |
| Python | 3.12+ (`requires-python` in `pyproject.toml`) |
| API | **pywin32** (pulled in on Windows) |

---

## Installation

**Recommended:** [uv](https://docs.astral.sh/uv/).

From a clone of this repo:

```powershell
git clone https://github.com/sandraschi/notepadpp-mcp.git
Set-Location notepadpp-mcp
uv sync
uv run notepadpp-mcp --help
```

Or install the package in editable mode:

```powershell
uv pip install -e ".[dev]"
```

When the package is published to PyPI, you can run it with:

```text
uvx notepadpp-mcp
```

---

## Usage

### How the server runs

The published console script is **`notepadpp-mcp`** (`notepadpp_mcp.server:run` in `pyproject.toml`).

- **Default  stdio:** what most MCP hosts use (Claude Desktop, Cursor, etc.). No extra flags.
- **Optional  HTTP bridge:** FastAPI + uvicorn on `127.0.0.1`, MCP HTTP at `/mcp`.

```text
notepadpp-mcp --http --port 10815
```

Change `--port` if 10815 is taken (see central port registry if you use a fleet of MCP webapps).

### MCP client configuration

**Claude Desktop** (`claude_desktop_config.json`)  point `command`/`args` at your install. Example using `uv` from a fixed repo path:

```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/Dev/repos/notepadpp-mcp", "notepadpp-mcp"]
    }
  }
}
```

If `notepadpp-mcp` is on `PATH`:

```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "notepadpp-mcp",
      "args": []
    }
  }
}
```

**Legacy:** older docs referenced `python -m notepadpp_mcp.tools.server`. Prefer **`notepadpp-mcp`** unless you are debugging that module.

### Calling tools (conceptual)

The assistant calls MCP tools by name; you do not run these in PowerShell. Examples of **operations** inside portmanteau tools:

| Tool | Typical `operation` values |
|------|----------------------------|
| `file_ops` | `open`, `new`, `save`, `info` |
| `text_ops` | `insert`, `find` |
| `status_ops` | `help`, `system_status`, `health_check` |
| `tab_ops` | `list`, `switch`, `close` |
| `session_ops` | `save`, `load`, `list` |
| `linting_ops` | `python`, `javascript`, `json`, `markdown`,  |
| `display_ops` | `fix_invisible_text`, `fix_display_issue` |
| `plugin_ops` | `discover`, `install`, `list`, `execute` |

Also: **`suggest_notepad_plan`**, **`agentic_notepad_workflow`** (orchestration), depending on build.

### Session snapshots (`session_ops`)

- **save**  Copies Notepad++s live **`session.xml`** (typically `%APPDATA%\Notepad++\session.xml`), which lists **all open buffers**, into a named file under **`%APPDATA%\Notepad++\notepadpp-mcp-sessions\`**. Format matches what Notepad++ uses for **Load Session** / **`-openSession`**. If the live file is missing or lists no files, the server falls back to a **minimal session** built from the **active tab** path when that path exists on disk.
- **load**  Runs **`notepad++.exe -openSession "<saved.xml>"`**. Whether a **new** or **existing** instance opens files depends on your **Multi-instance** settings in Notepad++.
- **Overrides**  `NOTEPADPP_SESSION_STORAGE_DIR` (where named `*.xml` are stored), `NOTEPADPP_LIVE_SESSION_XML` (override path to the live `session.xml`, e.g. portable or `-settingsDir` layouts).

### Sampling (LLM for workflows)

Optional. Set env vars as documented in the server / `NotepadSamplingHandler`, for example:

- `NOTEPADPP_SAMPLING_BASE_URL`  OpenAI-compatible base (e.g. Ollama `http://127.0.0.1:11434/v1`)
- `NOTEPADPP_SAMPLING_MODEL`
- `NOTEPADPP_SAMPLING_USE_CLIENT_LLM`  let the MCP host run sampling when supported

---

## Tools overview (portmanteau)

| Tool | Purpose |
|------|---------|
| **file_ops** | Open, new, save, file info |
| **text_ops** | Insert / find in buffer |
| **status_ops** | Help, system status, health |
| **tab_ops** | List / switch / close tabs |
| **session_ops** | Save / load / list workspace sessions |
| **linting_ops** | Python, JS, JSON, Markdown,  (uses `ruff` / `eslint` on PATH when available) |
| **display_ops** | Invisible text / display glitches |
| **plugin_ops** | Discover / install / list / execute plugins |

Responses use a consistent dict shape: `success`, `message` or `summary`, plus `error` / `recovery_options` where relevant.

---

## Documentation in repo

- `docs/EDITOR_AND_MCP_SCOPE.md`  **Notepad++ (editor) vs this server**: strengths of the editor, boundaries of the MCP bridge
- `docs/NOTEPADPP_MACROS.md`  **Macros** (what people use them for, `shortcuts.xml`, curated-set / future tool ideas)
- `src/notepadpp_mcp/docs/`  API notes, examples, PRD where present
- `src/notepadpp_mcp/docs_manifest.py`  REST/MCP overview for the web bridge (when enabled)

---

## Development

```powershell
uv pip install -e ".[dev]"
uv run pytest src/notepadpp_mcp/tests/
uv run ruff check src/notepadpp_mcp tests
uv run ruff format src/notepadpp_mcp tests
```

Optional: `python demonstration_test.py` or project `dev.py` if present for integration smoke tests.

---

## Roadmap / TODO (extensions)

Work that is **planned or open**  good first issues for contributors:

- [ ] **Multi-instance / multi-window**  target a specific Notepad++ HWND when several are open
- [ ] **Richer plugin flows**  coordinated multi-plugin steps, better error surfaces from Plugin Admin
- [ ] **Linting**  HTML/CSS, optional config files for linters
- [ ] **Config profiles**  server-side defaults (paths, timeouts, auto-start)
- [ ] **Batch**  first-class batch file operations with progress reporting
- [ ] **Web UI**  align docs with the actual dashboard package (e.g. `web_sota/`) and ports
- [ ] **Tests / coverage**  raise coverage; keep CI green on Windows runners
- [ ] **Macros**  curated XML snippets in-repo; optional read/list/merge for `%APPDATA%\Notepad++\shortcuts.xml` (see `docs/NOTEPADPP_MACROS.md`)

Older changelog bullets (multi-instance, plugin analytics, etc.) are folded into the list above where they still apply.

---

## Troubleshooting

- **Notepad++ not found**  Install Notepad++, start it once, or enable auto-start behavior if your build supports it.
- **Windows API not available**  Use Windows; install **pywin32** in the same environment as the server.
- **Tools missing in the client**  Restart the host, check MCP logs, confirm `notepadpp-mcp` runs without errors from a terminal.
- **Session save empty / fails**  Notepad++ may not refresh `session.xml` until you have opened saved files or **restarted** the editor; ensure **Settings > Preferences > Backup** session behavior matches your expectations. For portable installs, set **`NOTEPADPP_LIVE_SESSION_XML`** to the correct `session.xml`.

---

## Changelog (short)

- **0.2.x**  **`session_ops`** persists named sessions: copies live `session.xml`, loads via **`-openSession`** (see README section *Session snapshots*).
- **0.2.0**  FastMCP 3.1.0, sampling, skills, prompts, agentic workflow, HTTP bridge + web hooks as implemented in `server.py`.
- **Earlier**  Portmanteau tool consolidation, linting and plugin tooling.

---


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

MIT  see [LICENSE](LICENSE).
