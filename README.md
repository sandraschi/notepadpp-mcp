# Notepad++ MCP Server

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tools](https://img.shields.io/badge/tools-15-orange.svg)](https://github.com/sandraschi/notepadpp-mcp)
[![Tests](https://img.shields.io/badge/tests-18-brightgreen.svg)](https://github.com/sandraschi/notepadpp-mcp)

**FastMCP 2.12 compatible MCP server for comprehensive Notepad++ automation and control.**

✨ **15 powerful tools** including advanced tab and session management
🧪 **18 comprehensive tests** with real Windows API integration
🎯 **Production-ready** with structured logging and error handling

## 🚀 Quick Start

```bash
pip install notepadpp-mcp
```

Add to Claude Desktop config:
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

## 🎯 **New in v1.0: Advanced Workspace Management**

### 📑 **Tab Management Tools**
Organize and navigate multiple open files efficiently:
- **List all tabs**: See filenames, modification status, and active tab
- **Switch tabs**: Jump to any tab by index (0-based)
- **Close tabs**: Remove tabs individually or current tab

### 💾 **Session Management Tools**
Save and restore your entire workspace:
- **Save sessions**: Preserve all open files and cursor positions
- **Load sessions**: Restore complete workspace state
- **List sessions**: Browse saved workspace configurations

### 💡 **Usage Examples**
```bash
# Get comprehensive help about all tools
get_help()

# List all open tabs
list_tabs()

# Save current workspace
save_session("my_project_session")

# Load a saved session
load_session("my_project_session")

# Switch to tab 2
switch_to_tab(2)
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

## 📚 Documentation

- **[Complete API Documentation](src/notepadpp_mcp/docs/README.md)** - Comprehensive guide
- **[Product Requirements Document](src/notepadpp_mcp/docs/PRD.md)** - Vision and roadmap
- **[Configuration Examples](src/notepadpp_mcp/docs/examples/)** - Integration templates

## 🛠️ **Tools Overview** (15 Total)

| Category | Tools | Description |
|----------|-------|-------------|
| **File Operations** | 4 | Create, open, save, and inspect files |
| **Text Operations** | 2 | Insert and search text content |
| **Status & Info** | 3 | Monitor system and document state |
| **Tab Management** | 3 | Organize and navigate multiple files |
| **Session Management** | 3 | Save and restore workspace states |

**Total: 15 production-ready tools** with comprehensive Windows API integration.

## ⚡ Features

### 📁 **File Operations** (4 tools)
- `open_file` - Open files in Notepad++
- `new_file` - Create new files
- `save_file` - Save current file
- `get_current_file_info` - Get file metadata

### 📝 **Text Operations** (2 tools)
- `insert_text` - Insert text at cursor position
- `find_text` - Search text with case sensitivity options

### 📊 **Status & Information** (3 tools)
- `get_status` - Notepad++ status and window info
- `get_system_status` - Comprehensive system diagnostics
- `get_help` - Hierarchical help system

### 📑 **Tab Management** (3 tools) ✨ **NEW**
- `list_tabs` - List all open tabs with metadata
- `switch_to_tab` - Switch between tabs by index
- `close_tab` - Close tabs by index or current tab

### 💾 **Session Management** (3 tools) ✨ **NEW**
- `save_session` - Save workspace to named session
- `load_session` - Load saved sessions
- `list_sessions` - List all saved sessions

### 🔧 **Core Capabilities**
- 🎯 **Windows Integration**: Native Windows API with pywin32
- ⚡ **FastMCP 2.12**: Latest MCP framework compliance
- 📝 **Structured Logging**: Professional error handling
- 🧪 **Comprehensive Testing**: 18 tests covering all tools
- 📚 **Self-Documenting**: Built-in help system

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .[dev]

# Run comprehensive tests
python -m pytest src/notepadpp_mcp/tests/

# Format code
black src/

# Test real Notepad++ integration
python demonstration_test.py

# Development helper
python dev.py test|format|build|validate-dxt
```

### 🧪 **Testing**
- **18 comprehensive tests** covering all tools
- **Real Windows API testing** with actual Notepad++ integration
- **Demonstration script** (`demonstration_test.py`) tests live functionality
- **CI/CD ready** with automated testing pipeline

## 📄 License

MIT - see [LICENSE](LICENSE)
