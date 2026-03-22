"""
Plugin Operations Portmanteau Tool

Consolidates plugin operations (discover, install, list, execute) into a unified interface.
"""

import asyncio
import logging
from typing import Any, Literal

from fastmcp import FastMCP

from ..plugin_catalog import (
    enrich_installed_plugins_disk,
    get_plugins_list_cached,
    one_line_description,
    plugin_list_url,
)

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

_logger = logging.getLogger(__name__)


class PluginOperationsTool:
    """Portmanteau tool for plugin operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the plugin operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register plugin operations portmanteau tool."""

        @self.app.tool()
        async def plugin_ops(
            operation: Literal["discover", "install", "list", "execute"],
            plugin_name: str | None = None,
            command: str | None = None,
            category: str | None = None,
            search_term: str | None = None,
            limit: int = 20,
        ) -> dict[str, Any]:
            """PLUGIN_OPS — Discover, install, list, or invoke Notepad++ plugins.

            PORTMANTEAU PATTERN RATIONALE: One surface for plugin CRUD-style actions (TOOL_DESIGN_STANDARDS.md §1).

            Operations:
            - discover: Search/filter official list (search_term, category, limit).
            - install: Install plugin_name.
            - list: Installed plugins.
            - execute: Run command on plugin_name.

            Args:
                operation (Literal, required): "discover" | "install" | "list" | "execute".
                plugin_name (str | None): For install/execute.
                command (str | None): For execute.
                category (str | None): Optional discover filter.
                search_term (str | None): Optional discover filter.
                limit (int): Max discover results (default 20).

            Returns:
                dict with success, operation, summary, result (plugins, install status, etc.).

            Examples:
                await plugin_ops("discover", search_term="xml", limit=10)
                await plugin_ops("install", plugin_name="XMLTools")

            Errors:
                Network, permission, unknown plugin, or missing parameters; see error/summary fields.
            """
            if operation == "discover":
                try:
                    raw_list, fetch_err = get_plugins_list_cached()
                    if not raw_list:
                        return {
                            "success": False,
                            "error": fetch_err or "Could not load official plugin list",
                            "operation": operation,
                            "summary": "Plugin discovery failed — catalog unavailable",
                            "recovery_options": [
                                "Check internet connection",
                                "Set NOTEPADPP_PLUGIN_LIST_URL if using a mirror",
                                "Try again later",
                            ],
                            "context": {
                                "catalog_url": plugin_list_url(),
                                "detail": fetch_err,
                            },
                        }

                    total_available = len(raw_list)
                    plugins: list[dict[str, Any]] = []
                    st = (search_term or "").strip().lower()
                    cat = (category or "").strip().lower()

                    for plugin in raw_list:
                        if cat:
                            pc = (plugin.get("category") or "").strip().lower()
                            if pc != cat:
                                continue
                        if st:
                            dn = (plugin.get("display-name") or "").lower()
                            desc = (plugin.get("description") or "").lower()
                            fn = (plugin.get("folder-name") or "").lower()
                            if st not in dn and st not in desc and st not in fn:
                                continue

                        plugins.append(
                            {
                                "name": plugin.get("display-name", ""),
                                "folder_name": plugin.get("folder-name", ""),
                                "description": plugin.get("description", ""),
                                "description_one_line": one_line_description(
                                    plugin.get("description") or "", max_len=220
                                ),
                                "category": plugin.get("category") or "",
                                "version": plugin.get("version", ""),
                                "author": plugin.get("author", ""),
                                "homepage": plugin.get("homepage", ""),
                            }
                        )

                    plugins = plugins[:limit]

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Discovered {len(plugins)} plugins from official list",
                        "result": {
                            "plugins": plugins,
                            "total_found": len(plugins),
                            "limit": limit,
                        },
                        "next_steps": ["Use plugin_ops install to install desired plugins"],
                        "context": {
                            "source": "nppPluginList_pl_x64",
                            "catalog_url": plugin_list_url(),
                            "filters_applied": {
                                "category": category,
                                "search_term": search_term,
                            },
                            "total_available": total_available,
                        },
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin discovery failed: {e}",
                        "operation": operation,
                        "summary": "Failed to discover plugins from official list",
                        "recovery_options": [
                            "Check internet connection",
                            "Verify requests library is installed",
                        ],
                        "diagnostic_info": {"exception_type": type(e).__name__},
                    }

            elif operation == "install":
                if not plugin_name:
                    return {
                        "success": False,
                        "error": "plugin_name required for install operation",
                        "operation": operation,
                        "summary": "Plugin install failed - missing plugin name",
                        "clarification_options": {
                            "plugin_name": {
                                "description": "What plugin would you like to install?",
                                "type": "string",
                            }
                        },
                    }

                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin install failed - Windows API unavailable",
                        "recovery_options": [
                            "Ensure pywin32 is installed",
                            "Restart the MCP server",
                        ],
                    }

                try:
                    await self.controller.ensure_notepadpp_running()

                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Open Plugins menu with Alt+P
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt key
                    keybd_event(ord("P"), 0, 0, 0)
                    keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.5)

                    # Navigate to Plugin Admin (usually first option)
                    keybd_event(ord("P"), 0, 0, 0)  # Press 'P' for Plugin Admin
                    keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(1.0)

                    # In Plugin Admin, search for the plugin
                    # (This is a simplified version - full implementation would need more complex UI automation)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Attempted to install plugin '{plugin_name}'",
                        "result": {
                            "plugin_name": plugin_name,
                            "install_attempted": True,
                        },
                        "next_steps": [
                            "Check Plugin Admin dialog in Notepad++",
                            "Verify plugin appears in Plugins menu",
                        ],
                        "context": {
                            "method": "plugin_admin_dialog",
                            "manual_steps": f"Plugins > Plugin Admin > Search for '{plugin_name}' > Install",
                            "note": "Full automation requires Plugin Admin API integration",
                        },
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin install failed: {e}",
                        "operation": operation,
                        "plugin_name": plugin_name,
                        "summary": f"Failed to install plugin '{plugin_name}'",
                        "recovery_options": [
                            "Try manual installation via Plugin Admin",
                            "Check plugin name spelling",
                        ],
                        "diagnostic_info": {"exception_type": type(e).__name__},
                    }

            elif operation == "list":
                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin list failed - Windows API unavailable",
                        "recovery_options": [
                            "Ensure pywin32 is installed",
                            "Restart the MCP server",
                        ],
                    }

                try:
                    await self.controller.ensure_notepadpp_running()
                    data = enrich_installed_plugins_disk(self.controller.notepadpp_exe)
                    n = int(data.get("count") or 0)
                    m = int(data.get("catalog_matched_count") or 0)
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Found {n} plugin DLL(s) on disk; {m} matched official catalog by folder name.",
                        "result": data,
                        "next_steps": [
                            "Use description_one_line for a quick summary when catalog_match is true",
                        ],
                        "context": {"method": "filesystem_plus_catalog", "catalog_url": plugin_list_url()},
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin list failed: {e}",
                        "operation": operation,
                        "summary": "Failed to build plugin list",
                        "recovery_options": [
                            "Check Notepad++ is running",
                            "Check network if catalog enrichment fails",
                        ],
                        "diagnostic_info": {"exception_type": type(e).__name__},
                    }

            elif operation == "execute":
                if not plugin_name or not command:
                    missing = []
                    if not plugin_name:
                        missing.append("plugin_name")
                    if not command:
                        missing.append("command")

                    return {
                        "success": False,
                        "error": f"Missing required parameters: {', '.join(missing)}",
                        "operation": operation,
                        "summary": f"Plugin execute failed - missing {', '.join(missing)}",
                        "clarification_options": {
                            param: {
                                "description": f"What {param.replace('_', ' ')} would you like to use?",
                                "type": "string",
                            }
                            for param in missing
                        },
                    }

                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin execute failed - Windows API unavailable",
                        "recovery_options": [
                            "Ensure pywin32 is installed",
                            "Restart the MCP server",
                        ],
                    }

                try:
                    await self.controller.ensure_notepadpp_running()

                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Open Plugins menu with Alt+P
                    keybd_event = win32api.keybd_event
                    keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt key
                    keybd_event(ord("P"), 0, 0, 0)
                    keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
                    keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(0.5)

                    # Navigate to the plugin submenu
                    # (This is a simplified version - full navigation would need menu structure knowledge)

                    # Type the command name
                    for char in command:
                        keybd_event(ord(char.upper()), 0, 0, 0)
                        keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                        await asyncio.sleep(0.1)

                    await asyncio.sleep(0.5)

                    # Press Enter to execute
                    keybd_event(win32con.VK_RETURN, 0, 0, 0)
                    keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

                    await asyncio.sleep(1.0)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Attempted to execute '{command}' from plugin '{plugin_name}'",
                        "result": {
                            "plugin_name": plugin_name,
                            "command": command,
                            "execution_attempted": True,
                        },
                        "next_steps": ["Check Notepad++ for command execution results"],
                        "context": {
                            "method": "menu_navigation",
                            "manual_alternative": f"Plugins > {plugin_name} > {command}",
                            "limitation": "Full automation requires plugin menu structure knowledge",
                        },
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin execute failed: {e}",
                        "operation": operation,
                        "plugin_name": plugin_name,
                        "command": command,
                        "summary": "Failed to execute plugin command",
                        "recovery_options": [
                            "Try manual execution via Plugins menu",
                            "Verify plugin and command names",
                        ],
                        "diagnostic_info": {"exception_type": type(e).__name__},
                    }

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation,
                    "summary": f"Plugin operation failed - unknown operation '{operation}'",
                    "recovery_options": [
                        "Use 'discover', 'install', 'list', or 'execute' operations"
                    ],
                    "clarification_options": {
                        "operation": {
                            "description": "What plugin operation would you like to perform?",
                            "options": ["discover", "install", "list", "execute"],
                        }
                    },
                }
