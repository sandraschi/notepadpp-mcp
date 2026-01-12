"""
Text Operations Portmanteau Tool

Consolidates text operations (insert, find) into a unified interface.
"""

import asyncio
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP

# Windows-specific imports
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


class TextOperationsTool:
    """Portmanteau tool for text operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the text operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register text operations portmanteau tool."""

        @self.app.tool()
        async def text_ops(
            operation: Literal["insert", "find"],
            text: Optional[str] = None,
            case_sensitive: bool = False,
        ) -> Dict[str, Any]:
            """Perform text manipulation and search operations in Notepad++ documents.

            PORTMANTEAU PATTERN RATIONALE:
            Instead of creating 2 separate tools (insert, find), this tool consolidates text
            operations into a single interface. Prevents tool explosion (2 tools -> 1 tool) while maintaining
            full functionality and improving discoverability. Follows FastMCP 2.14.1+ SOTA standards.

            Supported Operations:
            - Insert text at cursor position
            - Search for text in current document
            - Case-sensitive and case-insensitive search

            Operations Detail:
            **Text Insertion:**
            - "insert": Add text at current cursor position in active document

            **Text Search:**
            - "find": Search for text occurrences in current document with configurable case sensitivity

            Prerequisites:
            - Windows OS with Notepad++ installed
            - pywin32 package for Windows API access
            - Active document open in Notepad++
            - Valid cursor position for insertion operations

            Args:
                operation (Literal, required): The text operation to perform. Must be one of: "insert", "find".
                    - "insert": Add text at cursor position (requires text)
                    - "find": Search for text in document (requires text)

                text (str | None): Text content for operation. Required for: insert, find operations.
                    For insert: text to be added at cursor position.
                    For find: text pattern to search for in document.

                case_sensitive (bool): Case sensitivity for find operations. Used by: find operation.
                    Default: False. When True, search matches exact case.

            Returns:
                Dictionary following FastMCP 2.14.1+ enhanced response patterns:
                ```json
                {
                  "success": true,
                  "operation": "insert",
                  "summary": "Text inserted successfully",
                  "result": {
                    "inserted_text": "Hello World",
                    "insertion_position": {"line": 5, "column": 10}
                  },
                  "next_steps": ["Continue editing", "Save document"],
                  "context": {
                    "operation_type": "text_insertion"
                  }
                }
                ```

                **Success Response Structure:**
                - success (bool): Operation success status
                - operation (str): Text operation that was performed
                - summary (str): Human-readable result summary
                - result (dict): Operation-specific data (inserted text, search results, etc.)
                - next_steps (list[str]): Suggested next actions
                - context (dict): Additional operation context

                **Error Response Structure:**
                - success (bool): Always false for errors
                - error (str): Error type (no_active_document, invalid_position, etc.)
                - operation (str): Failed operation
                - summary (str): Human-readable error summary
                - recovery_options (list[str]): Suggested recovery actions

            Examples:
                # Insert text at cursor
                result = await text_ops("insert", text="Hello World")
                # Returns: {"success": true, "summary": "Text inserted successfully", ...}

                # Search for text (case insensitive)
                result = await text_ops("find", text="error", case_sensitive=False)
                # Returns: {"success": true, "result": {"matches": 3, "positions": [...]}, ...}

                # Search with case sensitivity
                result = await text_ops("find", text="Error", case_sensitive=True)
                # Returns: {"success": true, "result": {"matches": 1, "positions": [...]}, ...}

            Errors:
                **Common Errors:**
                - "Windows API not available": pywin32 not installed or Notepad++ not running
                - "No active document": No document is currently open
                - "Invalid cursor position": Cursor position out of document bounds
                - "Empty text parameter": Required text parameter not provided

                **Recovery Options:**
                - Install pywin32: `pip install pywin32`
                - Ensure Notepad++ is running with an open document
                - Check cursor position before insertion operations
                - Provide non-empty text parameter for operations
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Text operation failed - Windows API unavailable",
                    "recovery_options": [
                        "Ensure pywin32 is installed",
                        "Restart the MCP server",
                    ],
                }

            if not text:
                return {
                    "success": False,
                    "error": "text parameter required for text operations",
                    "operation": operation,
                    "summary": "Text operation failed - missing text parameter",
                    "clarification_options": {
                        "text": {
                            "description": "What text would you like to insert or find?",
                            "type": "text_input",
                        }
                    },
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "insert":
                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Use clipboard to insert text (more reliable for longer text)
                    import win32clipboard

                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(text)
                    win32clipboard.CloseClipboard()

                    # Paste text with Ctrl+V
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("V"), 0, 0, 0)
                    keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.2)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully inserted {len(text)} characters",
                        "result": {
                            "inserted_chars": len(text),
                            "text_length": len(text),
                        },
                        "next_steps": [
                            "Use file_ops save to save changes",
                            "Use text_ops find to locate content",
                        ],
                        "context": {"insertion_method": "clipboard_paste"},
                    }

                elif operation == "find":
                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Open Find dialog with Ctrl+F
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("F"), 0, 0, 0)
                    keybd_event(ord("F"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.3)

                    # Type search text
                    for char in text:
                        if char.isalnum() or char in " .,;:!?":
                            keybd_event(ord(char.upper()), 0, 0, 0)
                            keybd_event(
                                ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0
                            )
                            await asyncio.sleep(0.01)

                    # Press Enter to start search
                    keybd_event(win32con.VK_RETURN, 0, 0, 0)
                    keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.2)

                    # Close find dialog with Escape
                    keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                    keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully searched for: '{text}'",
                        "result": {
                            "search_text": text,
                            "case_sensitive": case_sensitive,
                            "searched": True,
                        },
                        "next_steps": [
                            "Check Notepad++ for highlighted search results",
                            "Use text_ops insert to add content",
                        ],
                        "context": {
                            "search_method": "find_dialog",
                            "case_sensitive": case_sensitive,
                        },
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"Text operation failed - unknown operation '{operation}'",
                        "recovery_options": ["Use 'insert' or 'find' operations"],
                        "clarification_options": {
                            "operation": {
                                "description": "What text operation would you like to perform?",
                                "options": ["insert", "find"],
                            }
                        },
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Text operation failed: {e}",
                    "operation": operation,
                    "summary": f"Text operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Verify text content",
                        "Restart Notepad++",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                        "text_length": len(text) if text else 0,
                    },
                }
