# Notepad++ MCP Server

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tools](https://img.shields.io/badge/tools-26-orange.svg)](https://github.com/sandraschi/notepadpp-mcp)

MCP Server for automating and controlling Notepad++ through the Model Context Protocol. **26 powerful tools** including plugin management, display fixes, and code quality analysis.

## 🚀 Features

- 🔍 **File Operations**: Open, create, and manage files in Notepad++
- 📝 **Text Manipulation**: Insert, replace, and edit text content
- 🔎 **Search & Replace**: Powerful find/replace functionality
- 📊 **Status Queries**: Get current file info, cursor position, selection
- 🎯 **Windows Integration**: Native Windows API communication
- ⚡ **FastMCP 2.12**: Built on latest MCP framework
- 🔧 **Production Ready**: Comprehensive error handling and testing

## 📁 Project Structure

```
notepadpp-mcp/
├── src/notepadpp_mcp/
│   ├── tools/          # MCP server implementation
│   │   ├── server.py   # Main FastMCP server
│   │   └── __init__.py
│   ├── docs/           # Documentation and examples
│   │   ├── README.md   # This comprehensive guide
│   │   ├── PRD.md      # Product Requirements Document
│   │   ├── PLUGIN_ECOSYSTEM.md  # Plugin integration guide
│   │   └── examples/   # Usage examples and configs
│   ├── tests/          # Test suite
│   │   ├── conftest.py
│   │   └── test_server.py
│   ├── dxt/            # DXT packaging configuration
│   │   └── dxt.toml
│   └── __init__.py
├── pyproject.toml      # Package configuration
├── README.md           # Quick start guide
└── LICENSE             # MIT license
```

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- Notepad++ installed on Windows
- FastMCP 2.12 or higher

### Install from PyPI

```bash
pip install notepadpp-mcp
```

### Install from Source

```bash
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .[dev]
```

## ⚙️ Configuration

### Claude Desktop Configuration

Add to your Claude Desktop config file (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "notepadpp-mcp": {
      "command": "notepadpp-mcp",
      "args": [],
      "env": {
        "NOTEPADPP_AUTO_START": "true",
        "NOTEPADPP_TIMEOUT": "30"
      }
    }
  }
}
```

### Environment Variables

- `NOTEPADPP_PATH`: Custom path to Notepad++ executable (optional)
- `NOTEPADPP_TIMEOUT`: Command timeout in seconds (default: 30)
- `NOTEPADPP_AUTO_START`: Auto-start Notepad++ if not running (default: true)

## 🎯 MCP Tools Available

### File Operations
- **`get_status()`** - Get Notepad++ status and information
- **`open_file(file_path: str)`** - Open a file in Notepad++
- **`new_file()`** - Create a new untitled document
- **`save_file()`** - Save the current file
- **`get_current_file_info()`** - Get current file information

### Text Operations  
- **`insert_text(text: str)`** - Insert text at cursor position
- **`find_text(search: str, case_sensitive: bool = False)`** - Search for text

### Display Fixes
- **`fix_invisible_text()`** - Fix invisible text (white-on-white) in main editor
- **`fix_display_issue()`** - Fix general display issues like black-on-black text

### Plugin Management (NEW!)
- **`discover_plugins(category: str = None, search_term: str = None, limit: int = 20)`** - Discover available plugins from official Plugin List
- **`install_plugin(plugin_name: str)`** - Install a plugin using Plugin Admin
- **`list_installed_plugins()`** - List currently installed plugins
- **`execute_plugin_command(plugin_name: str, command: str)`** - Execute commands from installed plugins

## 📚 Usage Examples

### Basic File Operations

```python
# Check Notepad++ status
status = await get_status()

# Open a file
await open_file("C:/path/to/file.txt")

# Create new file
await new_file()

# Save current file
await save_file()

# Get current file info
file_info = await get_current_file_info()
```

### Text Operations

```python
# Insert text at cursor
await insert_text("Hello, World!")

# Search for text
results = await find_text("search term", case_sensitive=True)
```

### Display Fixes

```python
# Fix invisible text (white-on-white)
await fix_invisible_text()

# Fix general display issues
await fix_display_issue()
```

### Plugin Management (NEW!)

```python
# Discover available plugins
plugins = await discover_plugins(category="file_ops", limit=10)

# Search for specific plugins
json_plugins = await discover_plugins(search_term="JSON")

# Install a plugin
await install_plugin("NppFTP")

# List installed plugins
installed = await list_installed_plugins()

# Execute plugin commands
await execute_plugin_command("Compare", "Compare with clipboard")
```

## 🏗️ Architecture

### Windows Integration
- Uses `pywin32` for Windows API integration
- Communicates with Notepad++ via window messages and automation
- Handles multiple Notepad++ instances gracefully

### FastMCP 2.12 Compliance
- **Async/await** patterns throughout
- **Type hints** with mypy compliance
- **Stdio protocol** compliance (no print statements)
- **Error isolation** - operations don't crash the server

### Error Handling
- Comprehensive error handling for file operations
- Timeout protection for long-running operations
- Graceful degradation when Notepad++ is not available

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e ".[dev]"
pre-commit install
```

### Development Workflow

```bash
# Run tests
python -m pytest src/notepadpp_mcp/tests/

# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Development helper script
python dev.py test|format|build|validate-dxt
```

### Testing

The project includes comprehensive tests with Windows API mocking for CI/CD compatibility:

```bash
# Run all tests
pytest src/notepadpp_mcp/tests/

# Run with coverage
pytest --cov=src/notepadpp_mcp src/notepadpp_mcp/tests/

# Run specific test file
pytest src/notepadpp_mcp/tests/test_server.py
```

## 📦 DXT Packaging

This project is configured for Anthropic DXT packaging:

```bash
# Validate DXT configuration
dxt validate src/notepadpp_mcp/dxt/dxt.toml

# Pack for distribution
dxt pack src/notepadpp_mcp/dxt/dxt.toml
```

## ⚠️ Limitations

- **Windows-only** (Notepad++ is Windows-exclusive)
- Requires Notepad++ to be installed and accessible
- Basic text operations focus (advanced features TBD)
- File encoding detection relies on Notepad++ defaults

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest src/notepadpp_mcp/tests/`
5. Format code: `black src/ && isort src/`
6. Submit a pull request

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting  
- **mypy** for type checking
- **pytest** for testing
- **pre-commit** hooks for quality gates

## 📄 License

MIT License - see [LICENSE](../../../LICENSE) file for details.

## 📋 Changelog

### v0.1.0 (Current)
- ✅ FastMCP 2.12 compliance
- ✅ Basic file operations (open, save, new)
- ✅ Text manipulation (insert, find)
- ✅ Status queries and file information
- ✅ Windows automation integration
- ✅ Comprehensive test suite
- ✅ DXT packaging ready
- ✅ Production-ready error handling

## 🆘 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/sandraschi/notepadpp-mcp/issues)
- 📚 **Documentation**: This README and inline code docs
- 🔌 **Plugin Integration**: [Plugin Ecosystem Guide](PLUGIN_ECOSYSTEM.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sandraschi/notepadpp-mcp/discussions)

## 🔌 Notepad++ Plugin Ecosystem

### Official Plugin List

The [Notepad++ Plugin List](https://github.com/notepad-plus-plus/nppPluginList) is the official collection of Notepad++ plugins maintained by the Notepad++ team. This repository provides:

- **📦 Plugin Repository**: Official collection of 1,400+ starred plugins
- **🔒 Security**: Binary-encapsulated JSON list signed with certificates to prevent tampering
- **🔄 Plugin Admin Integration**: Powers the built-in Plugin Admin in Notepad++ for easy installation/update/deletion
- **🏗️ Build System**: Automated validation and packaging pipeline
- **📋 Multiple Architectures**: Support for 32-bit, 64-bit, and ARM64 plugins

### Plugin List Resources

- **32-Bit Plugin List**: [32-Bit Plugin List](https://github.com/notepad-plus-plus/nppPluginList)
- **64-Bit Plugin List**: [64-Bit Plugin List](https://github.com/notepad-plus-plus/nppPluginList)
- **64-Bit ARM Plugin List**: [64-Bit ARM Plugin List](https://github.com/notepad-plus-plus/nppPluginList)
- **Documentation**: [Plugin Admin Guide](https://npp-user-manual.org/docs/plugins/#plugins-admin)
- **Community Support**: [Plugin Support Forum](https://community.notepad-plus-plus.org/topic/16566/support-for-plugins-admin-npppluginlist)

### Integration with Notepad++ MCP Server

Our MCP server can leverage the Notepad++ plugin ecosystem through:

#### Plugin Management Tools
- **Plugin Discovery**: Query available plugins from the official list
- **Plugin Installation**: Install plugins via Plugin Admin integration
- **Plugin Commands**: Execute plugin-specific commands and macros
- **Plugin Status**: Check plugin status and configuration

#### Supported Plugin Categories
- **Code Analysis**: Linting, formatting, and syntax checking plugins
- **File Operations**: Advanced file management and comparison tools
- **Text Processing**: Regex, encoding, and transformation utilities
- **Development Tools**: Git integration, project management, and debugging
- **Language Support**: Syntax highlighting and language-specific features

#### Example Plugin Integrations
```python
# Install a plugin from the official list
await install_plugin("NppFTP")  # FTP client plugin

# Execute plugin commands
await execute_plugin_command("Compare", "Compare with clipboard")

# Get plugin information
plugin_info = await get_plugin_info("JSON Viewer")
```

### Plugin Development Guidelines

If you're developing plugins that work with our MCP server:

1. **Follow Official Standards**: Ensure your plugin meets [Notepad++ Plugin Development Guidelines](https://github.com/notepad-plus-plus/nppPluginList)
2. **MCP Compatibility**: Design plugin APIs that can be easily integrated with MCP tools
3. **Error Handling**: Implement robust error handling for MCP integration
4. **Documentation**: Provide clear documentation for MCP tool integration

### Future Plugin Integration Features

- **🔍 Plugin Discovery**: Browse and search the official plugin list
- **📥 Automated Installation**: Install plugins directly through MCP commands
- **⚙️ Plugin Configuration**: Configure plugin settings via MCP tools
- **🔄 Plugin Updates**: Check for and install plugin updates
- **📊 Plugin Analytics**: Monitor plugin usage and performance

## 🔗 Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - Framework for building MCP servers
- [Model Context Protocol](https://modelcontextprotocol.io/) - Open standard for AI model integration
- [Notepad++](https://notepad-plus-plus.org/) - The free source code editor
- [Notepad++ Plugin List](https://github.com/notepad-plus-plus/nppPluginList) - Official plugin repository

---

**Built with ❤️ for the Claude Desktop and MCP ecosystem**
