# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Dashboard auth now fails closed: `MCP_WEB_USER` / `MCP_WEB_PASSWORD` must be set explicitly (no hardcoded default password). `.env.example` added.
- Tauri bundle resources now ship `.env.example` instead of `.env`.

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
