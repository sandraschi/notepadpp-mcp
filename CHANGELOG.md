# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-08-07 (assfix re-run: gates green)

### Fixed
- **pyright 139 → 0**: lazy `win32api/win32con/win32gui/user32/psutil/yaml` None-bindings typed
  `Any` across 12 tool files; `await` on sync `get_window_text` removed; `hwnd or 0` guards;
  npp_theme `ElementTree` generics + `assert root is not None`; link_parser structured-log
  kwargs → formatted messages; web.py dict access; FastMCP lifespan + prefab children/rows
  typed ignores; `lint_javascript_file` missing-return suppression
- **pytest collection fixed**: `from src.notepadpp_mcp...` → `from notepadpp_mcp...` in
  test_file_validator + test_link_parser → **118 passed**
- **pyright added as dev dep**; `pyrightconfig.json` added (excludes tests/ + docs/)
- Test import fix; examples.json verified 100+ entries (was a measurement artifact)

### Gates (all pass)
ruff 0 · pyright 0 · format 0 · pytest 118 passed · tsc 0 · biome clean (33 files)

### Remaining (deferred, MEDIUM)
coverage `--cov-fail-under`, Playwright e2e, tool annotations/output_schema, webapp
data-testid/fonts/contrast polish.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `plugin_ops install` now uses **direct download+extract** by default (method='direct'):
  catalog lookup by folder/display name, ZIP download (200 MB cap), safe extraction
  with path-traversal protection, DLL verification, APPDATA plugins-dir fallback when
  the install dir is not writable. The old UI-automation path is deprecated.
- `linting_ops(operation="ahk")`: AutoHotkey v2 linting - uses the fleet `ahk-lint`
  CLI when on PATH, otherwise a structural checker (bracket/brace/quote/block-comment
  balance). Scripts are never executed.
- `text_ops comment_uncomment` now uses `;` for `.ahk`/`.ahkl` files (was `//`).

### Fixed
- `plugin_ops install` no longer fakes success via Plugin Admin keystrokes - installs
  are verified by DLL presence or return an honest error.
- Overwrite-safe text operations: `text_ops write` (whole-buffer replace, guarded),
  `replace_all` (regex/case options), `goto_line`, `copy_selection`, `comment_uncomment`,
  `case`, `trim`, `line_ops` (sort/join/duplicate), `count`.
- `file_ops save_as` (guarded overwrite), `is_dirty`, `reload_from_disk` (guarded),
  `find_in_files`, `diff_buffer`; `save` now writes a timestamped `.bak` first.
- `automation_ops` portmanteau: `macro_list`, `macro_play` (saved Notepad++ macros).
- `status_ops system_status` now reports editor KPIs (running, tab state, line count, buffer length).
- Verify-after writes: transformations confirm the buffer content before reporting success.

### Security
- Write/insert guards refuse to touch a non-empty named file unless explicitly authorized
  (force/edit_ok) - generation tasks must create a fresh tab first (`file_ops new`).

### Added
- `notepadpp_shutdown` MCP tool + `POST /api/shutdown` (agent-initiated graceful stop).
- `/api/v1/health`, `/api/v1/diagnostics`, `/api/v1/system/info` endpoints (CUA-NSIS contract).
- `/api/llm/providers` + `/api/llm/discover` (Ollama/LM Studio/vLLM probe) - Settings page now shows real provider state.
- Ring-buffer activity log on the bridge (`/api/logs*`); Logging page routed and reachable from the sidebar.
- Fleet CORS standard on the bridge (tauri://localhost + LAN/Tailscale regex).
- Chat page upgrade: localStorage history (100 cap), personalities, skill context, example prompts, export/clear, provider status, data-testid attributes.
- `llms.txt`, `llms-full.txt`, `docs/CONFIGURATION.md`, `docs/DEVELOPMENT.md`, `docs/TOOLS.md`, `docs/TROUBLESHOOTING.md`.
- Session context injection: `.claude-plugin/`, rewritten `.cursorrules`, `.windsurfrules`, `.opencode/skills/session-context/`, `.github/copilot-instructions.md`.
- MCPB prompts expanded to the 3-4-100 gate (system.md 3002w, user.md 4112w, examples 100).
- Justfile recipes: `serve`, `test`, `fmt`, `mcpb-pack`, `build-native`, `certify`.
- `assets/icon.png` (256x256).

### Fixed
- `start.ps1` used undefined `$ProjectRoot` (always exited); now uses `$RepoRoot` + backend readiness poll before opening the browser.
- `run_server.py` called `uvicorn.run` without importing uvicorn; now honors `PORT` too.
- pytest collection errors: `timeout` marker declared in `pytest.ini`.
- `web_sota/backend/server.py` removed (wildcard CORS + forbidden port 8000); logs moved to the bridge.
- Root `tests/` suite green again: megatest mock-app fix, Windows-relative nonexistent paths, validator binary/line-ending detection, link-parser nanosecond timing.
- Removed tracked junk: `coverage.xml`, root `Cargo.toml`/`Cargo.lock`/`extension.toml`/`Makefile`, `src/lib.rs`, placeholder icons, `.bak` dross.
- README now references existing just recipes.

### Changed
- Tool docstrings follow the SOTA docstring protocol: `Annotated + Field` parameter docs (no `Args:`), `## Return Format`, `## Examples` on all registered tools.
- `ai.py` chat router calls the local LLM for real (was a routing-hint stub); `POST /api/chat` accepts `{query, context?}`.
- **Industrial Startup Script**: Root `start.ps1` with `-Headless`, `-BackendOnly`, and `-NoBrowser` support.
- **Improved Port Handling**: Automatic TCP squatter termination and health-check polling.
- Plugin ecosystem integration tools (4 new tools)
- Display fix tools for invisible text and theme issues (2 new tools)
- `discover_plugins()` - Discover available plugins from official Notepad++ Plugin List
- `install_plugin()` - Automated plugin installation via Plugin Admin
- `list_installed_plugins()` - List currently installed plugins
- `execute_plugin_command()` - Execute commands from installed plugins
- `fix_invisible_text()` - Comprehensive fix for invisible text issue
- `fix_display_issue()` - Fix Notepad++ display problems
- PLUGIN_ECOSYSTEM.md documentation (300+ lines)
- HTTP request support via requests library

### Changed
- Total tool count increased from 20 to 26 tools (+30%)
- Server implementation expanded to 2,424 lines (+21%)
- Enhanced Windows API integration for plugin management
- Added requests>=2.31.0 dependency for GitHub API access

### Fixed
- Display issues with invisible text (white on white)
- Theme configuration problems
- Plugin discovery and installation workflows

## [1.1.0] - 2025-09-21

### Added
- GitHub Actions CI/CD workflows
- Automated testing pipeline with coverage reporting
- Automated release workflow
- MCPB (MCP Bundle) support
- Comprehensive development tooling

### Changed
- Migrated from DXT to MCPB
- Updated Python version requirement to >=3.9
- Enhanced build configuration
- Improved development scripts

### Fixed
- Build configuration inconsistencies
- Missing CI/CD automation
- Development workflow improvements

## [0.1.0] - 2025-01-15

### Added
- Initial release
- Notepad++ MCP server implementation
- Basic file operations (open, save, new, insert text)
- Search functionality
- Tab management
- Session management
- Linting tools integration
- Development helper script

### Features
- Windows-specific Notepad++ automation
- FastMCP 2.12 compliance
- Comprehensive tool set for file manipulation
- Type checking and code quality tools
- Pre-commit hooks configuration
