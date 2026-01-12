"""
Display Operations Portmanteau Tool

Consolidates display operations (invisible text fixes, display issue fixes) into a unified interface.
"""

import asyncio
from typing import Any, Dict, Literal

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


class DisplayOperationsTool:
    """Portmanteau tool for display operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the display operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register display operations portmanteau tool."""

        @self.app.tool()
        async def display_ops(
            operation: Literal["fix_invisible_text", "fix_display_issue"]
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates display operations (invisible text fixes, display issue fixes) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: Display operation to perform ("fix_invisible_text", "fix_display_issue")

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Display operation failed - Windows API unavailable",
                    "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "fix_invisible_text":
                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Method 1: Quick theme reset via Style Configurator
                    # Open Settings menu with Alt+S
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt key
                    keybd_event(ord("S"), 0, 0, 0)
                    keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.5)

                    # Press 'S' for Style Configurator
                    keybd_event(ord("S"), 0, 0, 0)
                    keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(1.0)

                    # Navigate to theme selection and reset to default
                    # (Simplified version - full implementation would need more keyboard simulation)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Attempted to fix invisible text issue",
                        "result": {"theme_reset_attempted": True, "method": "style_configurator"},
                        "next_steps": ["Check if text is now visible in Notepad++", "Restart Notepad++ if issue persists"],
                        "context": {
                            "issue_type": "invisible_text",
                            "method_used": "theme_reset",
                            "manual_alternative": "Settings > Style Configurator > Select 'Default' theme"
                        }
                    }

                elif operation == "fix_display_issue":
                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Attempt to refresh the display
                    # Send F5 (refresh) or Ctrl+L (redraw)
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    keybd_event(ord("L"), 0, 0, 0)
                    keybd_event(ord("L"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.5)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Attempted to fix display issues",
                        "result": {"display_refresh_attempted": True, "method": "redraw"},
                        "next_steps": ["Check if display issue is resolved", "Try restarting Notepad++ if problem persists"],
                        "context": {
                            "issue_type": "display_issue",
                            "method_used": "redraw",
                            "alternative_methods": ["theme_reset", "window_refresh", "application_restart"]
                        }
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"Display operation failed - unknown operation '{operation}'",
                        "recovery_options": ["Use 'fix_invisible_text' or 'fix_display_issue' operations"],
                        "clarification_options": {
                            "operation": {
                                "description": "What display operation would you like to perform?",
                                "options": ["fix_invisible_text", "fix_display_issue"]
                            }
                        }
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Display operation failed: {e}",
                    "operation": operation,
                    "summary": f"Display operation '{operation}' encountered an error",
                    "recovery_options": ["Check Notepad++ is running", "Try manual theme reset", "Restart Notepad++"],
                    "diagnostic_info": {"exception_type": type(e).__name__, "operation": operation}
                }