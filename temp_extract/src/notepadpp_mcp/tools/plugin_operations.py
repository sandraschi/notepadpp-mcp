"""
Plugin Operations Portmanteau Tool

Consolidates plugin operations (discover, install, list, execute) into a unified interface.
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
            plugin_name: Optional[str] = None,
            command: Optional[str] = None,
            category: Optional[str] = None,
            search_term: Optional[str] = None,
            limit: int = 20
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates plugin operations (discover, install, list, execute) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: Plugin operation to perform ("discover", "install", "list", "execute")
                plugin_name: Plugin name (required for "install" and "execute" operations)
                command: Command to execute (required for "execute" operation)
                category: Category filter (optional for "discover" operation)
                search_term: Search term filter (optional for "discover" operation)
                limit: Maximum results (default: 20 for "discover" operation)

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if operation == "discover":
                try:
                    import requests
                    import json

                    # Official Notepad++ Plugin List URLs
                    plugin_list_urls = [
                        "https://raw.githubusercontent.com/notepad-plus-plus/nppPluginList/master/src/pluginList.json",
                        "https://api.github.com/repos/notepad-plus-plus/nppPluginList/contents/src/pluginList.json",
                    ]

                    plugins_data = None

                    # Try to fetch plugin list from GitHub
                    for url in plugin_list_urls:
                        try:
                            response = requests.get(url, timeout=10)
                            if response.status_code == 200:
                                if "api.github.com" in url:
                                    # GitHub API returns base64 encoded content
                                    import base64
                                    content = base64.b64decode(response.json()["content"]).decode("utf-8")
                                    plugins_data = json.loads(content)
                                else:
                                    plugins_data = response.json()
                                break
                        except Exception as e:
                            continue

                    if not plugins_data:
                        return {
                            "success": False,
                            "error": "Could not fetch plugin list from any source",
                            "operation": operation,
                            "summary": "Plugin discovery failed - unable to fetch plugin list",
                            "recovery_options": ["Check internet connection", "Try again later", "Check GitHub status"],
                            "context": {"sources_tried": plugin_list_urls}
                        }

                    # Process plugin data
                    plugins = []
                    if "plugins" in plugins_data:
                        for plugin in plugins_data["plugins"]:
                            # Apply filters
                            if category and plugin.get("category", "").lower() != category.lower():
                                continue
                            if search_term and search_term.lower() not in plugin.get("display-name", "").lower() and search_term.lower() not in plugin.get("description", "").lower():
                                continue

                            plugins.append({
                                "name": plugin.get("display-name", ""),
                                "description": plugin.get("description", ""),
                                "category": plugin.get("category", ""),
                                "version": plugin.get("version", ""),
                                "author": plugin.get("author", ""),
                                "homepage": plugin.get("homepage", ""),
                            })

                    # Limit results
                    plugins = plugins[:limit]

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Discovered {len(plugins)} plugins from official list",
                        "result": {"plugins": plugins, "total_found": len(plugins), "limit": limit},
                        "next_steps": ["Use plugin_ops install to install desired plugins"],
                        "context": {
                            "source": "official_notepad_plugin_list",
                            "filters_applied": {"category": category, "search_term": search_term},
                            "total_available": len(plugins_data.get("plugins", []))
                        }
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin discovery failed: {e}",
                        "operation": operation,
                        "summary": "Failed to discover plugins from official list",
                        "recovery_options": ["Check internet connection", "Verify requests library is installed"],
                        "diagnostic_info": {"exception_type": type(e).__name__}
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
                                "type": "string"
                            }
                        }
                    }

                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin install failed - Windows API unavailable",
                        "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
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
                        "result": {"plugin_name": plugin_name, "install_attempted": True},
                        "next_steps": ["Check Plugin Admin dialog in Notepad++", "Verify plugin appears in Plugins menu"],
                        "context": {
                            "method": "plugin_admin_dialog",
                            "manual_steps": f"Plugins > Plugin Admin > Search for '{plugin_name}' > Install",
                            "note": "Full automation requires Plugin Admin API integration"
                        }
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin install failed: {e}",
                        "operation": operation,
                        "plugin_name": plugin_name,
                        "summary": f"Failed to install plugin '{plugin_name}'",
                        "recovery_options": ["Try manual installation via Plugin Admin", "Check plugin name spelling"],
                        "diagnostic_info": {"exception_type": type(e).__name__}
                    }

            elif operation == "list":
                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin list failed - Windows API unavailable",
                        "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
                    }

                try:
                    await self.controller.ensure_notepadpp_running()

                    # Focus on Notepad++
                    win32gui.SetForegroundWindow(self.controller.hwnd)
                    await asyncio.sleep(0.1)

                    # Open Plugins menu with Alt+P to see installed plugins
                    # (This is a simplified approach - full enumeration would need menu parsing)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Plugin list requested - check Notepad++ Plugins menu",
                        "result": {"plugins_menu_accessed": True},
                        "next_steps": ["Check Plugins menu in Notepad++ for installed plugins"],
                        "context": {
                            "method": "menu_inspection",
                            "manual_check": "View: Plugins menu in Notepad++",
                            "limitation": "Full plugin enumeration requires menu parsing API"
                        }
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin list failed: {e}",
                        "operation": operation,
                        "summary": "Failed to access plugin list",
                        "recovery_options": ["Check Notepad++ is running", "Try manual menu inspection"],
                        "diagnostic_info": {"exception_type": type(e).__name__}
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
                                "type": "string"
                            } for param in missing
                        }
                    }

                if not self.controller:
                    return {
                        "success": False,
                        "error": "Windows API not available",
                        "operation": operation,
                        "summary": "Plugin execute failed - Windows API unavailable",
                        "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
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
                        "result": {"plugin_name": plugin_name, "command": command, "execution_attempted": True},
                        "next_steps": ["Check Notepad++ for command execution results"],
                        "context": {
                            "method": "menu_navigation",
                            "manual_alternative": f"Plugins > {plugin_name} > {command}",
                            "limitation": "Full automation requires plugin menu structure knowledge"
                        }
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Plugin execute failed: {e}",
                        "operation": operation,
                        "plugin_name": plugin_name,
                        "command": command,
                        "summary": f"Failed to execute plugin command",
                        "recovery_options": ["Try manual execution via Plugins menu", "Verify plugin and command names"],
                        "diagnostic_info": {"exception_type": type(e).__name__}
                    }

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation,
                    "summary": f"Plugin operation failed - unknown operation '{operation}'",
                    "recovery_options": ["Use 'discover', 'install', 'list', or 'execute' operations"],
                    "clarification_options": {
                        "operation": {
                            "description": "What plugin operation would you like to perform?",
                            "options": ["discover", "install", "list", "execute"]
                        }
                    }
                }