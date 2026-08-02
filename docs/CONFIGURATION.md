# Configuration

All configuration is environment-variable driven. Copy `.env.example` to `.env`
(repo root) and adjust. There is no settings file; the webapp reads its own
`VITE_MCP_WEB_USER` / `VITE_MCP_WEB_PASSWORD` values from `web_sota/.env.local`.

## Dashboard auth (required)

| Var | Purpose |
|-----|---------|
| `MCP_WEB_USER` | Basic auth user for `/api/*` (bridge) |
| `MCP_WEB_PASSWORD` | Basic auth password. **Fail-closed**: if unset, the dashboard API returns 401 |

## Local LLM (Chat page)

| Var | Default | Purpose |
|-----|---------|---------|
| `AI_PROVIDER` | `ollama` | Provider label |
| `AI_ENDPOINT` | `http://127.0.0.1:11434/api/generate` | Ollama-compatible generate endpoint |
| `AI_MODEL` | `llama3.1-8b` | Model name |

## MCP sampling (agentic workflows)

| Var | Default | Purpose |
|-----|---------|---------|
| `NOTEPADPP_SAMPLING_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible sampling endpoint |
| `NOTEPADPP_SAMPLING_MODEL` | `llama3.1-8b` | Sampling model |
| `NOTEPADPP_SAMPLING_USE_CLIENT_LLM` | `0` | `1` = client host runs the LLM |

## Transport / bridge

| Var | Default | Purpose |
|-----|---------|---------|
| `MCP_TRANSPORT` | `stdio` | `stdio` or `http` |
| `MCP_PORT` / `NOTEPADPP_PORT` / `PORT` | `10815` | HTTP bridge port |
| `MCP_HOST` / `NOTEPADPP_HOST` | `127.0.0.1` | Bind address |
| `MCP_BRIDGE_URLS` | empty | Comma-separated MCP URLs to proxy |

## Notepad++ integration

| Var | Default | Purpose |
|-----|---------|---------|
| `NOTEPADPP_PATH` | auto-detect | Path to `notepad++.exe` |
| `NOTEPADPP_AUTO_START` | `true` | Launch Notepad++ if not running |
| `NOTEPADPP_TIMEOUT` | `30` | Operation timeout (s) |
| `NOTEPADPP_PLUGIN_LIST_URL` | official | Plugin catalog URL (mirror support) |
| `NOTEPADPP_SESSION_STORAGE_DIR` | app data | Where named sessions are stored |
| `NOTEPADPP_FLEET_REGISTRY` | empty | Path to `webapp-registry.json` for Apps Hub |

See `.env.example` for the complete annotated list.
