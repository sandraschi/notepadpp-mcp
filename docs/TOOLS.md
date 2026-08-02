# Tools

All MCP tools follow the portmanteau pattern: one tool per domain, an
`operation` enum as the first parameter, and structured dict returns.

| Tool | Operations | Description |
|------|-----------|-------------|
| `file_ops` | open, new, save, info | Open/create/save the active document; return file metadata |
| `text_ops` | insert, find | Insert text at the caret; find in the active buffer |
| `tab_ops` | list, switch, close | Manage editor tabs (0-based indices) |
| `session_ops` | save, load, list | Persist/restore named workspace sessions (XML) |
| `linting_ops` | python, javascript, json, markdown, tools | Lint disk files with available engines |
| `display_ops` | fix_invisible_text, fix_display_issue, theme_status, set_dark_mode, set_editor_theme | Rendering fixes and theme control |
| `plugin_ops` | discover, install, list, execute | Official plugin catalog + installed plugins |
| `status_ops` | help, system_status, health_check | Help system, server snapshot, connectivity |
| `lint_javascript_file` | — | ESLint JSON output (heuristic fallback) |
| `lint_json_file` | — | JSON validation + style nits |
| `lint_markdown_file` | — | Markdown structure checks |
| `notepad_dashboard` | — | Prefab UI dashboard (status, active tab, fleet) |
| `suggest_notepad_plan` | — | Sampling-based multi-step plan |
| `agentic_notepad_workflow` | — | Sampling loop with tool calls (max_iterations) |
| `notepadpp_shutdown` | — | Graceful shutdown (confirm=True) |

## Return convention

```json
{"success": true, "operation": "open", "message": "...", "result": {...}}
{"success": false, "operation": "open", "error": "...", "recovery_options": [...]}
```

## Discovery

- `status_ops(operation="help", category="file_operations")` — in-chat help
- `GET /api/tools` — machine-readable tool list for the Tools Hub
- `GET /api/mcp/meta` — tool count + instructions preview
- `skill://notepadpp-mcp/SKILL.md` — skill resource (MCP resources/read)
- `prompt://notepadpp-mcp/*` — workflow-guide, session-focus, plugin-discovery
