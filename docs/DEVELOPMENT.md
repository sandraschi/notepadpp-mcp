# Development

## Stack

- Python 3.12, FastMCP >=3.4.4, FastAPI + uvicorn, pywin32 (Windows)
- Frontend: React 19 + Vite + Tailwind + Lucide + TanStack Query (`web_sota/`)
- Tauri 2.0 native wrapper (`native/`) with PyInstaller-frozen backend

## Setup

```powershell
uv sync                      # Python deps (uv.lock committed)
just bootstrap               # + pre-commit hooks + web npm ci
```

## Layout

| Path | Purpose |
|------|---------|
| `src/notepadpp_mcp/` | Server package |
| `src/notepadpp_mcp/tools/` | Portmanteau tool modules (registered via `server.py`) |
| `src/notepadpp_mcp/web.py` | FastAPI REST endpoints + CORS + logs ring buffer |
| `src/notepadpp_mcp/ai.py` | Chat LLM router |
| `web_sota/` | React dashboard (Vite, port 10814, proxy → 10815) |
| `native/` | Tauri wrapper (NSIS) |
| `tests/` + `src/notepadpp_mcp/tests/` | pytest suites |

## Commands

```powershell
just serve                # backend + frontend
just test                 # pytest tests/ (CI parity)
just lint / just fix      # ruff + biome
just certify              # ruff, pyright, pytest, tsc, biome
just build-native         # NSIS installer
just cua-webapp-test      # browser walk (dev loop)
just cua-nsis-test        # installed-app smoke test
just mcpb-pack            # Claude Desktop .mcpb
```

## Tool development

- Tools are portmanteaus: one function per domain with `operation: Literal[...]`
- Parameter docs live in `Annotated[..., Field(description=...)]` (no `Args:` blocks)
- Docstrings carry `## Return Format` and `## Examples`
- Returns are dicts: `{success, operation, message/summary, ...}` with `error`/`recovery_options` on failure

## Tests

- Root `tests/` mirrors CI (`pytest tests/ --no-cov`)
- `src/notepadpp_mcp/tests/` has the package unit/integration suite
- GUI-dependent paths are guarded by `NOTEPADPP_GUI_TEST=1` / `requires_notepadpp` markers
