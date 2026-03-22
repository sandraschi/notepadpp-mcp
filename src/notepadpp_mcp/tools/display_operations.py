"""
Display Operations Portmanteau Tool

Consolidates display operations (invisible text fixes, display issue fixes) into a unified interface.
Theme / dark mode: edits %APPDATA%\\Notepad++\\config.xml (GUIConfig DarkMode); restart Notepad++ to apply.
"""

import asyncio
from typing import Any, Literal

from fastmcp import FastMCP

from ..npp_theme import patch_config_xml, read_theme_state, theme_status_payload

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
            operation: Literal[
                "fix_invisible_text",
                "fix_display_issue",
                "theme_status",
                "set_dark_mode",
                "set_editor_theme",
            ],
            dark_mode: bool | None = None,
            theme_xml: str | None = None,
        ) -> dict[str, Any]:
            """DISPLAY_OPS — Mitigate invisible text, display glitches, or adjust Notepad++ theme / dark mode.

            PORTMANTEAU PATTERN RATIONALE: Single entry for visibility vs general display fixes (TOOL_DESIGN_STANDARDS.md §1).

            Operations:
            - fix_invisible_text: Focus/refresh heuristics for invisible text.
            - fix_display_issue: Broader redraw/refresh path.
            - theme_status: Read config.xml DarkMode + list theme XML files from the Notepad++ install `themes` folder.
            - set_dark_mode: Set DarkMode enable (requires dark_mode=true|false). Writes config.xml; restart Notepad++.
            - set_editor_theme: Set darkThemeName (when dark mode on) or lightThemeName (when off). theme_xml basename
              e.g. Solarized.xml. For light mode, empty theme_xml clears to default stylers.

            Args:
                operation: One of the operations above.
                dark_mode: For set_dark_mode only.
                theme_xml: Theme file basename under the `themes` folder (e.g. Obsidian.xml), or empty for light default.

            Returns:
                dict with success, operation, summary, result.

            Notes:
                Notepad++ reloads these settings on startup. If Notepad++ is running, close it before editing, or it may
                overwrite config.xml on exit.

            Examples:
                await display_ops("theme_status")
                await display_ops("set_dark_mode", dark_mode=True)
                await display_ops("set_editor_theme", theme_xml="DarkModeDefault.xml")

            Errors:
                Window not found, API unavailable, or correction failed.
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Display operation failed - Windows API unavailable",
                    "recovery_options": [
                        "Ensure pywin32 is installed",
                        "Restart the MCP server",
                    ],
                }

            exe = self.controller.notepadpp_exe

            if operation == "theme_status":
                ts = theme_status_payload(exe)
                if not ts.get("success"):
                    return {
                        "success": False,
                        "operation": operation,
                        "summary": "Could not read Notepad++ theme configuration",
                        "error": ts.get("error", "unknown"),
                        "result": ts,
                    }
                return {
                    "success": True,
                    "operation": operation,
                    "summary": "Theme status and available theme files from the Notepad++ installation.",
                    "result": ts,
                }

            if operation == "set_dark_mode":
                if dark_mode is None:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": "set_dark_mode requires dark_mode=true or dark_mode=false",
                        "summary": "Missing dark_mode argument",
                        "clarification_options": {
                            "dark_mode": {"description": "Enable Notepad++ dark mode?", "type": "boolean"}
                        },
                    }
                try:
                    out = patch_config_xml(exe, dark_mode_enabled=dark_mode)
                except (OSError, ValueError, FileNotFoundError) as e:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": str(e),
                        "summary": "Failed to update config.xml",
                    }
                return {
                    "success": True,
                    "operation": operation,
                    "summary": f"Dark mode set to {'on' if dark_mode else 'off'} in config.xml. Restart Notepad++ to apply.",
                    "result": out,
                }

            if operation == "set_editor_theme":
                if theme_xml is None:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": "set_editor_theme requires theme_xml (e.g. Obsidian.xml) or empty string for light default",
                        "summary": "Missing theme_xml",
                    }
                try:
                    st = read_theme_state()
                except (OSError, ValueError, FileNotFoundError) as e:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": str(e),
                        "summary": "Could not read config.xml",
                    }
                tx = theme_xml.strip()
                try:
                    if st["dark_mode_enabled"]:
                        if not tx:
                            return {
                                "success": False,
                                "operation": operation,
                                "error": "When dark mode is enabled, theme_xml must be a themes/*.xml name",
                                "summary": "Empty theme",
                            }
                        out = patch_config_xml(exe, dark_theme_name=tx)
                    else:
                        out = patch_config_xml(
                            exe,
                            light_theme_name="" if not tx else tx,
                        )
                except (OSError, ValueError, FileNotFoundError) as e:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": str(e),
                        "summary": "Failed to update config.xml",
                    }
                return {
                    "success": True,
                    "operation": operation,
                    "summary": "Editor theme name updated in config.xml. Restart Notepad++ to apply.",
                    "result": out,
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

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Attempted to fix invisible text issue",
                        "result": {
                            "theme_reset_attempted": True,
                            "method": "style_configurator",
                        },
                        "next_steps": [
                            "Check if text is now visible in Notepad++",
                            "Restart Notepad++ if issue persists",
                            "Or use display_ops('theme_status') / set_editor_theme for config-based themes",
                        ],
                        "context": {
                            "issue_type": "invisible_text",
                            "method_used": "theme_reset",
                            "manual_alternative": "Settings > Style Configurator > Select 'Default' theme",
                        },
                    }

                if operation == "fix_display_issue":
                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Attempt to refresh the display
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
                        "result": {
                            "display_refresh_attempted": True,
                            "method": "redraw",
                        },
                        "next_steps": [
                            "Check if display issue is resolved",
                            "Try restarting Notepad++ if problem persists",
                        ],
                        "context": {
                            "issue_type": "display_issue",
                            "method_used": "redraw",
                            "alternative_methods": [
                                "theme_reset",
                                "window_refresh",
                                "application_restart",
                            ],
                        },
                    }

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation,
                    "summary": f"Display operation failed - unknown operation '{operation}'",
                    "recovery_options": [
                        "Use fix_invisible_text, fix_display_issue, theme_status, set_dark_mode, or set_editor_theme"
                    ],
                    "clarification_options": {
                        "operation": {
                            "description": "What display operation would you like to perform?",
                            "options": [
                                "fix_invisible_text",
                                "fix_display_issue",
                                "theme_status",
                                "set_dark_mode",
                                "set_editor_theme",
                            ],
                        }
                    },
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Display operation failed: {e}",
                    "operation": operation,
                    "summary": f"Display operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Try manual theme reset",
                        "Restart Notepad++",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                    },
                }
