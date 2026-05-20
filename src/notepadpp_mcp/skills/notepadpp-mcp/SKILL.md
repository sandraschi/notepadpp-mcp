# Notepad++ MCP — Agent skill

**Description:** Automate Notepad++ on Windows via pywin32 MCP bridge. Covers file operations, macro automation, session management, plugin control, text manipulation, syntax linting, and display configuration.

## Trigger Phrases

- "Open [file] in Notepad++"
- "Save the current tab"
- "Replace all [pattern] with [replacement]"
- "Run Python linter on current file"
- "Install the JSON plugin"
- "Close all tabs and start fresh"
- "Find [text] in the current document"
- "Record a macro to [action]"

## Tools (Portmanteau Pattern)

- **`file_ops(operation, file_path)`** — Open, save, close, new files. Operations: `open`, `save`, `save_as`, `close`, `new`, `info`.
- **`text_ops(operation, text, ...)`** — Text manipulation. Operations: `insert`, `replace`, `find`, `select_all`, `get_text`, `get_length`.
- **`tab_ops(operation, ...)`** — Tab/buffer management. Operations: `list`, `switch`, `close`, `close_all`, `activate_by_index`.
- **`session_ops(operation, ...)`** — Session save/load. Operations: `save_session`, `load_session`, `list_sessions`.
- **`linting_ops(operation, file_path)`** — Run linters. Operations: `python`, `javascript`, `html`, `xml`, `json`, `custom`.
- **`display_ops(operation, ...)`** — UI display. Operations: `word_wrap`, `show_whitespace`, `zoom`, `theme`.
- **`plugin_ops(operation, ...)`** — Plugin management. Operations: `discover`, `install`, `list`, `run`.
- **`status_ops(operation)`** — Server health. Operations: `health_check`, `active_tab`, `process_info`.

## Multi-step Workflows (FastMCP 3.1)

- **`agentic_notepad_workflow(workflow_prompt, available_tools)`** — Pass a natural-language goal like "open config.py, find the DEBUG flag, and toggle it". Requires sampling (Ollama or client LLM).
- **`suggest_notepad_plan(goal)`** — Quick plan via `ctx.sample` when sampling is available. Returns structured step list for manual execution.

## Workflow

1. **Status check**: `status_ops("health_check")` to confirm Notepad++ process is accessible.
2. **File target**: Use `file_ops("info")` to see active tab. Use `file_ops("open", file_path=...)` to open target.
3. **Act**: Apply text ops, linting, or plugin commands as needed.
4. **Save/close**: `file_ops("save")` or `file_ops("close")` to persist.

## Limits

- Tab **list** is often limited to the active tab (title-based) unless extended via N++ APIs.
- **Plugin install** uses UI automation toward Plugin Admin; plugin discovery uses official **nppPluginList** JSON.
- Large file operations may have pywin32 timeout limits. Use text_ops with bounded selections.

## Examples

- `file_ops("open", file_path="D:\\work\\config.py")` then `linting_ops("python", file_path="D:\\work\\config.py")`
- `plugin_ops("discover", search_term="json", limit=15)` then `plugin_ops("install", plugin_name="JSON Viewer")`
- `text_ops("find", text="TODO", case_sensitive=True)` → review results → `text_ops("replace", find_text="TODO", replace_text="DONE")`
