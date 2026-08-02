# Troubleshooting

## Dashboard API returns 401 everywhere

Auth is off by default (open localhost). A 401 means `MCP_WEB_USER` / `MCP_WEB_PASSWORD`
are set in `.env` and the request doesn't match. Either fix the credentials, or clear
both values (and the `VITE_MCP_WEB_*` mirrors in `web_sota/.env.local`) to run open.
Restart the bridge after changes.

## Chat says "Local LLM is not reachable"

- Start Ollama (`ollama serve`) or point `AI_ENDPOINT`/`AI_MODEL` at another
  OpenAI-compatible server in `.env`
- The Settings page shows provider probe results (`/api/llm/providers`)

## Tools fail with "Windows API not available"

- pywin32 is not importable. Run `uv sync` on Windows; verify with
  `python -c "import win32api"`

## Notepad++ is not detected / auto-start fails

- Set `NOTEPADPP_PATH` to the full path of `notepad++.exe`
- Check `status_ops(operation="health_check")` output for the failure reason

## Bridge won't start (port 10815 in use)

```powershell
Get-NetTCPConnection -LocalPort 10815 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
or just re-run `start.ps1` (it clears zombies).

## `just cua-nsis-test` fails on the health phase

- The installer must be built first (`just build-native`)
- Config lives in `scripts/cua-nsis-config.json`; health path must be `/api/v1/health`
- Run `just cua-webapp-test` for a dev-loop check without building

## pytest fails during collection

- Root `tests/` uses the `timeout` marker - it is declared in `pytest.ini`.
  If you add a new marker, declare it there too (`--strict-markers`).

## Native build: "Failed to fetch" in the installed app

- The Tauri app loads `http://127.0.0.1:10815` - verify CORS covers
  `tauri://localhost` (see `src/notepadpp_mcp/web.py`) and that
  `native/tauri.conf.json` bundles `.env.example`, not `.env`.

## Need more help

- `docs/NOTEPADPP_MACROS.md` — macro reference
- `INSTALL.md` — install guide
- Open an issue at https://github.com/sandraschi/notepadpp-mcp/issues
