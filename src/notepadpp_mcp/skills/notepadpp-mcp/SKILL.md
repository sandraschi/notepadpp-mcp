# Notepad++ MCP — agent skill

## When to use
- Automate **Notepad++ on Windows** (pywin32): open/save files, tabs, text insert/find, linting, plugins, display fixes.
- Use **portmanteau tools** with an `operation` parameter: `file_ops`, `text_ops`, `tab_ops`, `session_ops`, `linting_ops`, `display_ops`, `plugin_ops`, `status_ops`.

## Multi-step workflows (FastMCP 3.1)
- **`agentic_notepad_workflow`**: pass `workflow_prompt` and `available_tools` (e.g. `["file_ops","linting_ops"]`). Requires **sampling** (Ollama at `NOTEPADPP_SAMPLING_BASE_URL` or client LLM with `NOTEPADPP_SAMPLING_USE_CLIENT_LLM=1`).
- **`suggest_notepad_plan`**: quick natural-language plan via `ctx.sample` when sampling is available.

## Limits
- Tab **list** is often **active tab only** (title-based) unless extended via N++ APIs.
- **Plugin install** uses UI automation toward Plugin Admin; discovery uses official **nppPluginList** JSON.

## Typical calls
- `file_ops("info")` — active file hint from window title.
- `file_ops("open", file_path="D:\\\\work\\\\file.py")`
- `linting_ops("python", file_path="...")`
- `plugin_ops("discover", search_term="json", limit=15)`
- `status_ops("health_check")`
