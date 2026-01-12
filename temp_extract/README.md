# Notepad++ MCP Server

[![CI](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml)
[![Release](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.1-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-64-passing-brightgreen.svg)](https://github.com/sandraschi/notepadpp-mcp)
[![Coverage](https://img.shields.io/badge/coverage-21%25-orange.svg)](https://github.com/sandraschi/notepadpp-mcp)
[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/sandraschi/notepadpp-mcp/releases)

MCP server for Notepad++ automation with portmanteau tool consolidation. FastMCP 2.14.1 compliant with structured logging and Windows API integration.

## Installation

### MCPB Package Installation
Download and install the MCPB package from [Releases](https://github.com/sandraschi/notepadpp-mcp/releases).

### Python Installation
```bash
# Install from PyPI
pip install notepadpp-mcp

# Or install from source
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .
```

### ⚙️ **Claude Desktop Configuration**
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "notepadpp-mcp",
      "args": []
    }
  }
}
```

### 🔧 **Manual Configuration** (if needed)
```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "python",
      "args": ["-m", "notepadpp_mcp.tools.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

## 📋 Requirements

### 🖥️ **System Requirements**
- **Windows 10/11** (64-bit)
- **Notepad++ 8.0+** installed and accessible
- **Python 3.10+** with pip
- **pywin32** for Windows API integration

### Dependencies
- FastMCP 2.14.1+ - MCP framework
- structlog 23.0.0+ - Structured JSON logging
- pywin32 - Windows API bindings
- psutil - System monitoring

### 🚨 **Important Notes**
- Notepad++ must be installed on the system
- Server requires Windows API access (pywin32)
- First run may require Notepad++ to be started manually

## Tool Organization

The server uses portmanteau tools following FastMCP 2.14.1+ standards. Each tool consolidates related operations to prevent tool explosion while maintaining functionality.

### Usage Examples
```bash
# File operations
file_ops("open", file_path="document.txt")
file_ops("save")
file_ops("info")

# Text operations
text_ops("insert", text="Hello World")
text_ops("find", text="search term")

# Status operations
status_ops("help")
status_ops("system_status")
status_ops("health_check")
```

## 📁 Project Structure

```
notepadpp-mcp/
├── src/notepadpp_mcp/
│   ├── tools/          # MCP server implementation
│   ├── docs/           # Documentation and examples
│   ├── tests/          # Test suite
│   └── dxt/            # DXT packaging configuration
├── pyproject.toml      # Package configuration
├── README.md           # This file
└── LICENSE             # MIT license
```

## Documentation

- [API Documentation](src/notepadpp_mcp/docs/README.md) - Tool reference and usage examples
- [Architecture](src/notepadpp_mcp/docs/PRD.md) - System design and implementation details

## Tools Overview (8 Portmanteau Tools)

| Tool | Operations | Description |
|------|------------|-------------|
| **file_ops** | open, new, save, info | File management operations |
| **text_ops** | insert, find | Text manipulation and search |
| **status_ops** | help, system_status, health_check | System status and help |
| **tab_ops** | list, switch, close | Tab navigation and management |
| **session_ops** | save, load, list | Workspace session management |
| **linting_ops** | python, javascript, json, markdown, tools | Code quality analysis |
| **display_ops** | fix_invisible_text, fix_display_issue | Display and theme fixes |
| **plugin_ops** | discover, install, list, execute | Plugin ecosystem management |

All tools follow FastMCP 2.14.1+ portmanteau pattern with enhanced response patterns.

## Portmanteau Tools

### file_ops
Consolidates file operations: open, new, save, info
- Open files in Notepad++
- Create new files
- Save current file
- Get file metadata

### text_ops
Consolidates text operations: insert, find
- Insert text at cursor position
- Search text with options

### status_ops
Consolidates status operations: help, system_status, health_check
- Hierarchical help system
- System diagnostics
- Health checks

### tab_ops
Consolidates tab operations: list, switch, close
- List open tabs with metadata
- Switch between tabs by index
- Close tabs by index

### session_ops
Consolidates session operations: save, load, list
- Save workspace sessions
- Load saved sessions
- List available sessions

### linting_ops
Consolidates linting operations: python, javascript, json, markdown, tools
- Python analysis (ruff/flake8)
- JavaScript validation (ESLint)
- JSON syntax checking
- Markdown style validation

### display_ops
Consolidates display operations: fix_invisible_text, fix_display_issue
- Fix invisible text issues
- Fix display problems

### plugin_ops
Consolidates plugin operations: discover, install, list, execute
- Discover plugins from official list
- Install plugins via Plugin Admin
- List installed plugins
- Execute plugin commands

### Core Capabilities
- Windows API integration with pywin32
- FastMCP 2.14.1+ compliance with portmanteau pattern
- Structured JSON logging to stderr
- 64 tests covering all portmanteau tools
- Enhanced response patterns (summary, next_steps, recovery_options)
- Multi-linter support with fallback options
- Code quality analysis for multiple languages
- Plugin ecosystem integration

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .[dev]

# Run comprehensive tests
pytest src/notepadpp_mcp/tests/

# Run with coverage
pytest src/notepadpp_mcp/tests/ --cov=src/notepadpp_mcp --cov-report=html

# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Via Makefile
make test
make test-coverage
make lint
make format
make check  # Run all checks

# Test real Notepad++ integration
python demonstration_test.py

# Development helper
python dev.py test|format|build|validate-dxt
```

### 🧪 **Testing**
- **64 comprehensive tests** covering all tools including linting and plugin functionality
- **Real Windows API testing** with actual Notepad++ integration
- **Demonstration script** (`demonstration_test.py`) tests live functionality
- **CI/CD ready** with automated testing pipeline
- **Multi-linter testing** with ruff, flake8, and ESLint integration
- **Plugin ecosystem testing** with GitHub API mocking

## 🏗️ Architecture

### 🎯 **Core Components**
- **NotepadPPController** - Windows API integration layer
- **FastMCP Server** - MCP protocol implementation
- **Tool Decorators** - Automatic tool registration
- **Structured Logging** - Professional error handling

### 🔧 **Integration Flow**
1. **MCP Client** (Claude Desktop) → **FastMCP Server**
2. **Server** → **NotepadPPController** → **Windows API**
3. **Windows API** → **Notepad++ Application** → **User Interface**

### 📁 **File Structure**
```
src/notepadpp_mcp/
├── tools/server.py     # Main MCP server (2424 lines)
├── tests/              # Comprehensive test suite (64 tests)
├── docs/               # Documentation and examples
│   ├── README.md       # API documentation
│   ├── PRD.md          # Product requirements
│   └── PLUGIN_ECOSYSTEM.md  # Plugin integration guide
└── dxt/                # DXT packaging configuration
```

## 🐛 Troubleshooting

### ❌ **Common Issues**

#### **"Notepad++ not found"**
```bash
# Check if Notepad++ is installed
python demonstration_test.py

# Install Notepad++
# Download from: https://notepad-plus-plus.org/downloads/
# Or via Chocolatey: choco install notepadplusplus
```

#### **"Windows API not available"**
```bash
# Install pywin32
pip install pywin32

# Restart Python environment
# Try running demonstration script again
python demonstration_test.py
```

#### **"Server not connecting"**
```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "python",
      "args": ["-m", "notepadpp_mcp.tools.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

#### **"Tools not appearing in Claude"**
1. **Restart Claude Desktop** after configuration
2. **Check logs** in Claude developer console
3. **Verify Notepad++** is running on the system
4. **Run demonstration** script to test functionality

### 🆘 **Getting Help**

#### **Run Diagnostics**
```bash
# Test all functionality
python demonstration_test.py

# Check tool availability
python -c "from notepadpp_mcp.tools.server import app; print('Tools:', len(app._tools))"
```

#### **Debug Mode**
```bash
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run server with debug output
python -m notepadpp_mcp.tools.server
```

#### Manual Testing
```python
# Test portmanteau tools
from notepadpp_mcp.tools.server import file_ops, status_ops

# Get file info
info = await file_ops("info")
print("File info:", info)

# Get help
help_info = await status_ops("help")
print("Help:", help_info)
```

## 🤝 Contributing

### 📝 **Development Setup**
```bash
# Clone repository
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp

# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest

# Format code
ruff format src/

# Build MCPB package
python dev.py build
```

### 🐛 **Reporting Issues**
1. **Run demonstration script** first: `python demonstration_test.py`
2. **Check existing issues** on GitHub
3. **Include error logs** and system information
4. **Test with different Notepad++ versions** if possible

### Feature Requests
- Check existing portmanteau tools before proposing new ones
- Consider Windows API limitations
- Test with real Notepad++ workflows
- Follow FastMCP 2.14.1+ portmanteau patterns

## Changelog

### v1.2.0 - SOTA Compliance & Portmanteau Consolidation
- Portmanteau tool consolidation (26 → 8 tools)
- FastMCP 2.14.1+ compliance with enhanced response patterns
- Plugin ecosystem integration
- Display fix tools
- Updated MCPB packaging

### v1.1.0 - Linting Tools
- Multi-language linting support
- Code quality analysis tools
- Enhanced testing coverage

### v1.0.0 - Core Release
- Initial Notepad++ automation tools
- Windows API integration
- MCP server implementation

### **Planned Features**
- **Multi-instance support** for multiple Notepad++ windows
- **Advanced plugin workflows** with multiple plugin coordination
- **Plugin analytics** and usage monitoring
- **Custom plugin support** for user-developed plugins
- **HTML/CSS linting** tools for web development
- **Configuration files** for custom settings
- **Batch operations** for multiple file processing

## 📄 License

MIT - see [LICENSE](LICENSE)
