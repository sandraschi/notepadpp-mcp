# Onboarding — notepadpp-mcp

Notepad++ MCP Server needs a real Notepad++ on Windows. Until the checks below
pass, the dashboard shows sample (MOCK) data so you can explore the UI.

## 1. What you need

| Item | Notes |
|------|-------|
| OS | Windows 10/11 64-bit (the wrappee is Windows-only) |
| Editor | Notepad++ 8+ (`C:\Program Files\Notepad++\notepad++.exe` or set `NOTEPADPP_PATH`) |
| Python | 3.12+ via `uv` (`uv sync`) |
| Packages | `pywin32` (Windows-only dep, installed automatically on win32) |

No online account, no API keys, no paid service. Everything runs locally.

## 2. Sanity check (2 minutes)

```powershell
uv sync
uv run notepadpp-mcp --help
uv run pytest tests/ -q --no-cov
```

Then start the stack:

```powershell
.\start.ps1
```

Open http://localhost:10814. The backend health probe must return 200:

```powershell
Invoke-WebRequest http://127.0.0.1:10815/api/health -UseBasicParsing
```

## 3. Common pitfalls

- **Notepad++ not found**: set `NOTEPADPP_PATH` to your install, or pass
  `notepadpp_path` in the MCPB user config.
- **Port taken**: backend 10815 / frontend 10814 are the fleet registry ports.
  Change `--port` (and `fleet-start.config.ps1`) if something else owns them.
- **pywin32 import errors on non-Windows**: expected — this server only runs
  its editor bridge on Windows. File/lint/plugin-catalog tools still work.
- **MOCK badges**: sample KPIs/lists labelled MOCK clear automatically once
  the backend answers `/api/health` with 200.

## 4. Done when

- [ ] `uv run pytest tests/ -q --no-cov` passes
- [ ] `.\start.ps1` brings up backend 10815 + frontend 10814
- [ ] `/api/health` returns 200 and MOCK badges are gone
