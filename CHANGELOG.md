# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive validation decorators for input parameters
- Enhanced error handling with structured logging
- GitHub Actions CI/CD pipeline with multi-version Python testing
- Dependabot configuration for automated dependency updates
- Issue and PR templates for better contribution workflow
- Glama.ai platform integration documentation

### Changed
- Replaced all `print()` statements with structured logging
- Enhanced error handling across all MCP tools
- Improved test suite with proper mocking and validation
- Updated documentation with production readiness information

### Fixed
- Test suite failures and type errors
- Windows API mock setup in tests
- Input validation for file paths and text content
- Exception handling patterns throughout codebase

## [1.1.0] - 2025-01-15

### Added
- **5 comprehensive linting tools** for Python, JavaScript, JSON, and Markdown
- **Multi-linter support** with ruff, flake8, ESLint, and fallback options
- **16 additional tests** covering all linting functionality
- **Enhanced DXT configuration** with detailed linting tool documentation
- **Total: 20 tools** for complete code quality analysis

### Technical Details
- Added `lint_python_file()` - Comprehensive Python code analysis
- Added `lint_javascript_file()` - JavaScript validation with ESLint support
- Added `lint_json_file()` - JSON syntax validation and structure analysis
- Added `lint_markdown_file()` - Markdown style and syntax validation
- Added `get_linting_tools()` - Overview of available linting capabilities

## [1.0.0] - 2025-01-10

### Added
- **15 comprehensive tools** for Notepad++ automation
- **Real Windows API integration** with pywin32
- **Advanced tab and session management**
- **18 comprehensive tests** with full coverage
- **DXT packaging** for easy installation
- **Production-ready** error handling and logging

### Core Features
- File operations: `open_file()`, `new_file()`, `save_file()`, `get_current_file_info()`
- Text operations: `insert_text()`, `find_text()`
- Status monitoring: `get_status()`, `get_system_status()`, `get_help()`
- Tab management: `list_tabs()`, `switch_to_tab()`, `close_tab()`
- Session management: `save_session()`, `load_session()`, `list_sessions()`

### Technical Implementation
- FastMCP 2.12 framework compliance
- Windows API integration via pywin32
- Asynchronous operations with proper error handling
- Comprehensive test suite with mocking
- Cross-platform path handling
- Structured logging implementation

## [0.1.0] - 2025-01-01

### Added
- Initial MCP server implementation
- Basic Notepad++ integration
- Core file operations
- Proof of concept functionality

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Contributing

When contributing to this project, please:
1. Update the CHANGELOG.md with your changes
2. Follow the existing format
3. Add entries under [Unreleased] for upcoming releases
4. Move entries to a version section when releasing

---

**Legend:**
- 🎯 Breaking change
- ✨ New feature
- 🐛 Bug fix
- 📚 Documentation
- 🔧 Maintenance
- 🧪 Testing
