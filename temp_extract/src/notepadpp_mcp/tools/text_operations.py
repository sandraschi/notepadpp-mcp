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
            case_sensitive: bool = False
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates text operations (insert, find) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: Text operation to perform ("insert", "find")
                text: Text content (required for both operations)
                case_sensitive: Case sensitivity for find operations (default: False)

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Text operation failed - Windows API unavailable",
                    "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
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
                            "type": "text_input"
                        }
                    }
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
                        "result": {"inserted_chars": len(text), "text_length": len(text)},
                        "next_steps": ["Use file_ops save to save changes", "Use text_ops find to locate content"],
                        "context": {"insertion_method": "clipboard_paste"}
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
                            keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
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
                        "result": {"search_text": text, "case_sensitive": case_sensitive, "searched": True},
                        "next_steps": ["Check Notepad++ for highlighted search results", "Use text_ops insert to add content"],
                        "context": {"search_method": "find_dialog", "case_sensitive": case_sensitive}
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
                                "options": ["insert", "find"]
                            }
                        }
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Text operation failed: {e}",
                    "operation": operation,
                    "summary": f"Text operation '{operation}' encountered an error",
                    "recovery_options": ["Check Notepad++ is running", "Verify text content", "Restart Notepad++"],
                    "diagnostic_info": {"exception_type": type(e).__name__, "operation": operation, "text_length": len(text) if text else 0}
                }