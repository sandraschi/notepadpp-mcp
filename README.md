# Notepad++ MCP Server

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FastMCP 2.12 compatible MCP server for Notepad++ automation and control.

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

## ⚡ Features

- 🔍 **File Operations**: Open, create, save files in Notepad++
- 📝 **Text Manipulation**: Insert text, search content
- 📊 **Status Queries**: Get file info and document state
- 🎯 **Windows Integration**: Native Windows API communication
- ⚡ **FastMCP 2.12**: Latest MCP framework compliance
- 🔧 **Production Ready**: Comprehensive error handling and testing

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .[dev]

# Run tests
python -m pytest src/notepadpp_mcp/tests/

# Format code
black src/

# Development helper
python dev.py test|format|build|validate-dxt
```

## 📄 License

MIT - see [LICENSE](LICENSE)
