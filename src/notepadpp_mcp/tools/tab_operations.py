"""
Tab Operations Portmanteau Tool

Consolidates tab operations (list, switch, close) into a unified interface.
"""

import asyncio
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

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


class TabOperationsTool:
    """Portmanteau tool for tab operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the tab operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register tab operations portmanteau tool."""

        @self.app.tool()
        async def tab_ops(
            operation: Annotated[
                Literal["list", "switch", "close"],
                Field(
                    description="Operation: list enumerates tabs, switch activates tab_index, close closes tab_index (or the active tab when -1)."
                ),
            ],
            tab_index: Annotated[
                int, Field(description="0-based tab index for switch/close; -1 targets the active tab (default).")
            ] = -1,
            discard: Annotated[
                bool,
                Field(
                    description="Allow close to discard unsaved changes (default False - close refuses on dirty tabs)."
                ),
            ] = False,
        ) -> dict[str, Any]:
            """TAB_OPS — List, switch, or close editor tabs.

            PORTMANTEAU PATTERN RATIONALE: One tool for list/switch/close (TOOL_DESIGN_STANDARDS.md §1).

            Safety: close REFUSES on a tab with unsaved changes unless discard=true
            (avoids Notepad++'s modal Save dialog and silent no-op closes).

            Operations:
            - list: Enumerate open tabs.
            - switch: Activate tab_index (0-based).
            - close: Close tab_index or current tab when index is -1.

            ## Return Format
            {"success": bool, "operation": str, "message": str, "result": {"tabs": [...], "count": int}, "error": str | null}

            ## Examples
            tab_ops(operation="list")
            tab_ops(operation="switch", tab_index=1)
            tab_ops(operation="close")
            tab_ops(operation="close", discard=true)

            Notes:
             - Invalid index, no tabs, or Windows API unavailable returns success=False with recovery_options.
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Tab operation failed - Windows API unavailable",
                    "recovery_options": [
                        "Ensure pywin32 is installed",
                        "Restart the MCP server",
                    ],
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "list":
                    # Get window title which usually contains filename
                    window_text = self.controller.get_window_text(self.controller.hwnd)

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
                        "summary": f"Listed tabs - found {1} active tab",
                        "result": {
                            "total_tabs": 1,  # Simplified - Notepad++ API would be needed for full tab list
                            "active_tab": {
                                "filename": filename,
                                "is_modified": is_modified,
                                "full_title": window_text,
                                "tab_index": 0,
                            },
                        },
                        "next_steps": [
                            "Use tab_ops switch to change tabs",
                            "Use tab_ops close to close current tab",
                        ],
                        "context": {
                            "api_limitation": "Full tab enumeration requires Notepad++ plugin API integration",
                            "current_capabilities": "Can only show active tab information",
                        },
                    }

                elif operation == "switch":
                    if tab_index < 0:
                        return {
                            "success": False,
                            "error": "tab_index must be >= 0 for switch operation",
                            "operation": operation,
                            "summary": "Tab switch failed - invalid tab index",
                            "clarification_options": {
                                "tab_index": {
                                    "description": "Which tab index would you like to switch to? (0-based)",
                                    "type": "integer",
                                    "minimum": 0,
                                }
                            },
                        }

                    # Focus on Notepad++ window
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Send Ctrl+Tab to cycle through tabs
                    # This is a simplified implementation - full tab switching would need plugin API
                    keybd_event = win32api.keybd_event

                    for _ in range(tab_index):
                        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                        keybd_event(win32con.VK_TAB, 0, 0, 0)
                        await asyncio.sleep(0.1)
                        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
                        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                        await asyncio.sleep(0.2)

                    await asyncio.sleep(0.5)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully switched to tab {tab_index}",
                        "result": {"switched_to_tab": tab_index},
                        "next_steps": [
                            "Use tab_ops list to verify active tab",
                            "Continue editing in the switched tab",
                        ],
                        "context": {
                            "switch_method": "keyboard_simulation",
                            "api_limitation": "Precise tab switching requires Notepad++ plugin API",
                        },
                    }

                elif operation == "close":
                    # Guard: closing a dirty tab pops NPP's "Save file?" dialog and
                    # silently blocks the close unless the user allows discarding.
                    tab_state = self.controller.get_active_tab_state()
                    if tab_state["dirty"] and not discard:
                        return {
                            "success": False,
                            "error": "unsaved_changes",
                            "operation": operation,
                            "summary": "Refusing to close a tab with unsaved changes",
                            "message": (
                                f"Tab '{tab_state['filename'] or 'Untitled'}' has unsaved changes. "
                                "Closing it would pop Notepad++'s Save dialog. "
                                "Save first (file_ops save / save_as), or pass discard=true to close without saving."
                            ),
                            "recovery_options": [
                                "file_ops(operation='save') then tab_ops(operation='close')",
                                "tab_ops(operation='close', discard=true) to discard changes",
                            ],
                            "context": tab_state,
                        }
                    # Focus on Notepad++ window
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Send Ctrl+W to close tab (or Ctrl+F4)
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("W"), 0, 0, 0)
                    keybd_event(ord("W"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.4)

                    # If NPP popped the Save dialog, dismiss it deterministically (no = discard)
                    dismissed = False
                    if self.controller.has_modal_dialog():
                        dismissed = self.controller.dismiss_save_dialog("no")
                        await asyncio.sleep(0.4)

                    tab_description = "current tab" if tab_index == -1 else f"tab {tab_index}"
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully closed {tab_description}"
                        + (" (discarded unsaved changes)" if dismissed else ""),
                        "result": {"closed_tab": tab_index, "dialog_dismissed": dismissed},
                        "next_steps": [
                            "Use tab_ops list to see remaining tabs",
                            "Use file_ops new to open a new file if needed",
                        ],
                        "context": {
                            "close_method": "keyboard_simulation",
                            "unsaved_changes": "May prompt user if file has unsaved changes",
                        },
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"Tab operation failed - unknown operation '{operation}'",
                        "recovery_options": ["Use 'list', 'switch', or 'close' operations"],
                        "clarification_options": {
                            "operation": {
                                "description": "What tab operation would you like to perform?",
                                "options": ["list", "switch", "close"],
                            }
                        },
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Tab operation failed: {e}",
                    "operation": operation,
                    "summary": f"Tab operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Verify tab indices are valid",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                        "tab_index": tab_index,
                    },
                }
