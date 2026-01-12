"""
File Operations Portmanteau Tool

Consolidates file operations (open, new, save, info) into a unified interface.
"""

import asyncio
import os
import subprocess
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


class FileOperationsTool:
    """Portmanteau tool for file operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the file operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register file operations portmanteau tool."""

        @self.app.tool()
        async def file_ops(
            operation: Literal["open", "new", "save", "info"],
            file_path: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates file operations (open, new, save, info) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: File operation to perform ("open", "new", "save", "info")
                file_path: Path to file (required for "open" operation)

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "File operation failed - Windows API unavailable",
                    "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "open":
                    if not file_path:
                        return {
                            "success": False,
                            "error": "file_path required for open operation",
                            "operation": operation,
                            "summary": "File open failed - missing path parameter",
                            "clarification_options": {
                                "file_path": {
                                    "description": "What file would you like to open?",
                                    "type": "file_path"
                                }
                            }
                        }

                    # Convert to absolute path
                    abs_path = os.path.abspath(file_path)

                    if not os.path.exists(abs_path):
                        return {
                            "success": False,
                            "error": f"File not found: {abs_path}",
                            "operation": operation,
                            "summary": f"Failed to open file - {abs_path} not found",
                            "recovery_options": ["Check file path spelling", "Verify file exists", "Provide absolute path"],
                            "diagnostic_info": {"requested_path": abs_path, "exists": False}
                        }

                    # Use subprocess to open file (Notepad++ command line)
                    subprocess.Popen(
                        [self.controller.notepadpp_exe, abs_path],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    # Wait a moment for file to load
                    await asyncio.sleep(0.5)

                    return {
                        "success": True,
                        "operation": operation,
                        "file_path": abs_path,
                        "summary": f"Successfully opened file: {os.path.basename(abs_path)}",
                        "result": {"file_path": abs_path, "opened": True},
                        "next_steps": ["Use text_ops to edit content", "Use file_ops save to save changes"],
                        "context": {"file_size": os.path.getsize(abs_path) if os.path.exists(abs_path) else 0}
                    }

                elif operation == "new":
                    # Send Ctrl+N to create new file
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Simulate Ctrl+N
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("N"), 0, 0, 0)
                    keybd_event(ord("N"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.2)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Successfully created new file",
                        "result": {"created": True},
                        "next_steps": ["Use text_ops to add content", "Use file_ops save to save the file"],
                        "context": {"file_type": "untitled"}
                    }

                elif operation == "save":
                    # Send Ctrl+S to save file
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Simulate Ctrl+S
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("S"), 0, 0, 0)
                    keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.3)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Successfully saved current file",
                        "result": {"saved": True},
                        "next_steps": ["Continue editing or use file_ops info to check status"],
                        "context": {"save_time": "current"}
                    }

                elif operation == "info":
                    # Get window title which usually contains filename
                    window_text = await self.controller.get_window_text(self.controller.hwnd)

                    # Parse filename from window title
                    # Notepad++ title format: "filename - Notepad++"
                    filename = "Untitled"
                    if " - Notepad++" in window_text:
                        filename = window_text.split(" - Notepad++")[0]

                    # Check if file is modified (usually indicated by *)
                    is_modified = "*" in window_text

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Current file: {filename}",
                        "result": {
                            "window_title": window_text,
                            "filename": filename,
                            "is_modified": is_modified
                        },
                        "next_steps": ["Use text_ops to edit content" if not is_modified else "Use file_ops save to save changes"],
                        "context": {"has_unsaved_changes": is_modified}
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"File operation failed - unknown operation '{operation}'",
                        "recovery_options": ["Use 'open', 'new', 'save', or 'info' operations"],
                        "clarification_options": {
                            "operation": {
                                "description": "What file operation would you like to perform?",
                                "options": ["open", "new", "save", "info"]
                            }
                        }
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"File operation failed: {e}",
                    "operation": operation,
                    "summary": f"File operation '{operation}' encountered an error",
                    "recovery_options": ["Check Notepad++ is running", "Verify file permissions", "Restart Notepad++"],
                    "diagnostic_info": {"exception_type": type(e).__name__, "operation": operation}
                }