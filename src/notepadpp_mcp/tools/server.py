"""
Notepad++ MCP Server

FastMCP 2.14.1 compliant MCP server for Notepad++ automation and control.
Provides comprehensive file operations, text manipulation, and UI control.

REFACTORED: Tools separated into individual modules for maintainability.
Portmanteau pattern implemented to consolidate related operations.

Status: Beta - Actively developed, API may change
"""

import asyncio
import sys

from fastmcp import FastMCP

# Tool imports
from .file_operations import FileOperationsTool
from .text_operations import TextOperationsTool
from .status_operations import StatusOperationsTool
from .tab_operations import TabOperationsTool
from .session_operations import SessionOperationsTool
from .linting_operations import LintingOperationsTool
from .display_operations import DisplayOperationsTool
from .plugin_operations import PluginOperationsTool

# Windows-specific imports for controller
try:
    import win32api
    import win32con
    import win32gui

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    win32api = None
    win32con = None
    win32gui = None

# Import the Notepad++ controller
from .controller import NotepadPPController

# Global controller instance
controller = NotepadPPController() if WINDOWS_AVAILABLE else None

# Create FastMCP app
app = FastMCP(
    "Notepad++ MCP Server",
    instructions="""You are Notepad++ MCP Server, a comprehensive automation server for Notepad++ text editor on Windows.

CORE CAPABILITIES:
- File Operations: Open, create, save files in Notepad++
- Text Operations: Insert text, search content with case sensitivity
- Tab Management: List, switch, and close tabs
- Session Management: Save and restore workspace states
- Code Quality: Lint Python, JavaScript, JSON, and Markdown files
- Display Fixes: Fix invisible text and display issues
- Plugin Ecosystem: Discover, install, and manage 1,400+ official plugins

USAGE PATTERNS:
1. File Operations: Use file_ops() to open/save files, text_ops() for editing
2. Tab Management: Use tab_ops() to manage open documents
3. Session Management: Use session_ops() to save/restore workspaces
4. Code Quality: Use linting_ops() for comprehensive code analysis
5. Display Issues: Use display_ops() to fix UI problems
6. Plugin Management: Use plugin_ops() to discover and install plugins

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
""",
)

# Initialize tool managers
file_tool = FileOperationsTool(app, controller)
text_tool = TextOperationsTool(app, controller)
status_tool = StatusOperationsTool(app, controller)
tab_tool = TabOperationsTool(app, controller)
session_tool = SessionOperationsTool(app, controller)
linting_tool = LintingOperationsTool(app, controller)
display_tool = DisplayOperationsTool(app, controller)
plugin_tool = PluginOperationsTool(app, controller)

# Register all tools
file_tool.register_tools()
text_tool.register_tools()
status_tool.register_tools()
tab_tool.register_tools()
session_tool.register_tools()
linting_tool.register_tools()
display_tool.register_tools()
plugin_tool.register_tools()


async def main() -> None:
    """Main entry point for the MCP server."""
    if not WINDOWS_AVAILABLE:
        print("ERROR: This MCP server requires Windows and pywin32", file=sys.stderr)
        sys.exit(1)

    await app.run_stdio_async()


def run() -> None:
    """Synchronous entry point for compatibility."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
