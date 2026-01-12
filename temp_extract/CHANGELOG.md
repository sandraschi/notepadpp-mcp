# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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