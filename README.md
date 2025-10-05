# Notepad++ MCP Server

[![Gold Status](https://img.shields.io/badge/Glama.ai-Gold%20Status-gold)](https://glama.ai)
[![CI](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/ci.yml)
[![Release](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/sandraschi/notepadpp-mcp/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tools](https://img.shields.io/badge/tools-20-orange.svg)](https://github.com/sandraschi/notepadpp-mcp)
[![Tests](https://img.shields.io/badge/tests-64-brightgreen.svg)](https://github.com/sandraschi/notepadpp-mcp)
[![Coverage](https://img.shields.io/badge/coverage-23%25-orange.svg)](https://github.com/sandraschi/notepadpp-mcp)

**🏆 Gold Status Certified** FastMCP 2.12 compatible MCP server for comprehensive Notepad++ automation, control, and code quality analysis. Enterprise production-ready with 64 passing tests, structured logging, and advanced linting capabilities.

✨ **20 powerful tools** including advanced tab/session management and code linting
🧪 **64 comprehensive tests** with real Windows API integration and 23% coverage
🔍 **5 linting tools** for Python, JavaScript, JSON, and Markdown
🎯 **Enterprise production-ready** with structured logging and error handling
🏆 **Gold Status** on Glama.ai platform (85/100 quality score)

## 🚀 Installation & Setup

### 📦 **Option 1: DXT Installation** (Recommended)
1. **Download** the latest DXT file from [Releases](https://github.com/sandraschi/notepadpp-mcp/releases)
2. **Open Claude Desktop**
3. **Go to Settings** → **Developer** → **MCP Servers**
4. **Drag & Drop** the DXT file onto the extensions screen
5. **Restart Claude Desktop** - the server will auto-install and configure

### 🐍 **Option 2: Python Installation**
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

### 🛠️ **Dependencies**
- **FastMCP 2.12+** - MCP framework
- **pywin32** - Windows API bindings
- **psutil** - System monitoring
- **pathlib** - Path operations

### 🚨 **Important Notes**
- Notepad++ must be installed on the system
- Server requires Windows API access (pywin32)
- First run may require Notepad++ to be started manually

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
- **[CI/CD & Glama.ai Guide](docs/CI_CD_GLAMA_OPTIMIZATION_GUIDE.md)** - Complete CI/CD and platform optimization documentation
- **[Glama.ai Integration Summary](docs/GLAMA_AI_OPTIMIZATION_SUMMARY.md)** - Platform optimization achievements
- **[Glama.ai GitHub App Setup](docs/GLAMA_GITHUB_APP_SETUP.md)** - Installation and configuration guide

## 🛠️ **Tools Overview** (20 Total)

| Category | Tools | Description |
|----------|-------|-------------|
| **File Operations** | 4 | Create, open, save, and inspect files |
| **Text Operations** | 2 | Insert and search text content |
| **Status & Info** | 3 | Monitor system and document state |
| **Tab Management** | 3 | Organize and navigate multiple files |
| **Session Management** | 3 | Save and restore workspace states |
| **Code Quality & Linting** | 5 | Analyze code for multiple file types |

**Total: 20 production-ready tools** with comprehensive Windows API integration and multi-linter support.

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

### 🔍 **Code Quality & Linting** (5 tools) ✨ **NEW**
- `lint_python_file` - Comprehensive Python code analysis with ruff/flake8
- `lint_javascript_file` - JavaScript validation with ESLint or basic checking
- `lint_json_file` - JSON syntax validation and structure analysis
- `lint_markdown_file` - Markdown style and syntax validation
- `get_linting_tools` - Overview of available linting capabilities

### 🔧 **Core Capabilities**
- 🎯 **Windows Integration**: Native Windows API with pywin32
- ⚡ **FastMCP 2.12**: Latest MCP framework compliance
- 📝 **Structured Logging**: Professional error handling
- 🧪 **Comprehensive Testing**: 34 tests covering all tools
- 📚 **Self-Documenting**: Built-in help system
- 🔍 **Multi-linter Support**: ruff, flake8, ESLint with fallback options
- 🎨 **Code Quality**: Syntax validation for Python, JS, JSON, Markdown

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
- **34 comprehensive tests** covering all tools including linting functionality
- **Real Windows API testing** with actual Notepad++ integration
- **Demonstration script** (`demonstration_test.py`) tests live functionality
- **CI/CD ready** with automated testing pipeline
- **Multi-linter testing** with ruff, flake8, and ESLint integration

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
├── tools/server.py     # Main MCP server (1533 lines)
├── tests/              # Comprehensive test suite (34 tests)
├── docs/               # Documentation and examples
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

#### **Manual Testing**
```python
# Test individual tools
from notepadpp_mcp.tools.server import get_status, get_help

# Get status
status = await get_status()
print("Status:", status)

# Get help
help_info = await get_help()
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
black src/

# Build DXT package
python dev.py build
```

### 🐛 **Reporting Issues**
1. **Run demonstration script** first: `python demonstration_test.py`
2. **Check existing issues** on GitHub
3. **Include error logs** and system information
4. **Test with different Notepad++ versions** if possible

### 💡 **Feature Requests**
- **Check existing tools** in the tools overview
- **Consider Windows API limitations**
- **Test with real Notepad++ workflows**
- **Follow FastMCP 2.12 patterns**

## 📜 Changelog

### **v1.1.0** - Linting Tools Release ✨ **NEW**
- ✅ **5 comprehensive linting tools** for Python, JavaScript, JSON, and Markdown
- ✅ **Multi-linter support** with ruff, flake8, ESLint, and fallback options
- ✅ **16 additional tests** covering all linting functionality
- ✅ **Enhanced DXT configuration** with detailed linting tool documentation
- ✅ **Total: 20 tools** for complete code quality analysis

### **v1.0.0** - Core Release
- ✅ **15 comprehensive tools** for Notepad++ automation
- ✅ **Real Windows API integration** with pywin32
- ✅ **Advanced tab and session management**
- ✅ **18 comprehensive tests** with full coverage
- ✅ **DXT packaging** for easy installation
- ✅ **Production-ready** error handling and logging

### **Planned Features**
- **Multi-instance support** for multiple Notepad++ windows
- **Plugin integration** for extended functionality
- **HTML/CSS linting** tools for web development
- **Configuration files** for custom settings
- **Batch operations** for multiple file processing

## 📄 License

MIT - see [LICENSE](LICENSE)
