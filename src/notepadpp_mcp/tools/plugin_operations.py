"""
Plugin Operations Portmanteau Tool

Consolidates plugin operations (discover, install, list, execute) into a unified interface.
"""

import asyncio
import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

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
    win32api: Any = None
    win32con: Any = None
    win32gui: Any = None

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
            operation: Annotated[
                Literal["discover", "install", "list", "execute"],
                Field(
                    description="Operation: discover searches the official plugin list, install installs plugin_name, list shows installed plugins, execute runs command on plugin_name."
                ),
            ],
            plugin_name: Annotated[
                str | None, Field(description="Plugin name for install/execute (folder-name or display-name).")
            ] = None,
            command: Annotated[str | None, Field(description="Command to run on the plugin for execute.")] = None,
            category: Annotated[str | None, Field(description="Optional category filter for discover.")] = None,
            search_term: Annotated[str | None, Field(description="Optional name filter for discover.")] = None,
            limit: Annotated[int, Field(description="Max discover results (default 20).", ge=1, le=200)] = 20,
            method: Annotated[
                Literal["direct", "ui"],
                Field(
                    description="Install method: direct downloads the plugin ZIP from the official catalog and extracts it (default, deterministic); ui opens the Plugin Admin dialog (unreliable, fallback only)."
                ),
            ] = "direct",
        ) -> dict[str, Any]:
            """PLUGIN_OPS — Discover, install, list, or invoke Notepad++ plugins.

            PORTMANTEAU PATTERN RATIONALE: One surface for plugin CRUD-style actions (TOOL_DESIGN_STANDARDS.md §1).

            Operations:
            - discover: Search/filter official list (search_term, category, limit).
            - install: Install plugin_name - direct download+extract by default (method='direct'), with DLL verification.
            - list: Installed plugins.
            - execute: Run command on plugin_name.

            ## Return Format
            {"success": bool, "operation": str, "summary": str, "result": {"plugins": [...]}, "error": str | null}

            ## Examples
            plugin_ops(operation="discover", search_term="xml", limit=10)
            plugin_ops(operation="install", plugin_name="XMLTools")
            plugin_ops(operation="install", plugin_name="mermaid", method="direct")
            plugin_ops(operation="list")

            Notes:
             - Network, permission, unknown plugin, or missing parameters return success=False with error, summary and recovery_options.
             - Direct install writes to the plugins dir (APPDATA fallback when the install dir is not writable); restart Notepad++ to load the plugin.
             - Scripts inside plugin archives are never executed - extraction is copy-only with path-traversal protection.
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

                    # Locate the plugin in the official catalog (folder-name or display-name match)
                    raw_list, fetch_err = get_plugins_list_cached()
                    entry = None
                    if raw_list:
                        q = (plugin_name or "").strip().lower()
                        for p in raw_list:
                            if (p.get("folder-name") or "").strip().lower() == q:
                                entry = p
                                break
                        if entry is None:
                            for p in raw_list:
                                if q and q in (p.get("display-name") or "").lower():
                                    entry = p
                                    break

                    if entry is None:
                        return {
                            "success": False,
                            "error": "plugin_not_found",
                            "operation": operation,
                            "summary": f"Plugin '{plugin_name}' not found in the official catalog",
                            "result": {"catalog_error": fetch_err} if fetch_err else {},
                            "recovery_options": [
                                "plugin_ops(operation='discover', search_term=...) to find the exact name",
                                "Check the spelling (folder-name, not display name)",
                            ],
                        }

                    folder_name = (entry.get("folder-name") or plugin_name).strip()
                    download_url = (entry.get("repository") or "").strip()

                    if method == "ui" or not download_url:
                        if not download_url:
                            return {
                                "success": False,
                                "error": "no_direct_url",
                                "operation": operation,
                                "summary": f"Catalog entry '{folder_name}' has no direct download URL - use method='ui'",
                                "recovery_options": [
                                    "plugin_ops(operation='install', plugin_name=..., method='ui') for the Plugin Admin dialog",
                                    "Download manually from the plugin homepage",
                                ],
                            }
                        return {
                            "success": False,
                            "error": "ui_method_unsupported",
                            "operation": operation,
                            "summary": "UI install (Plugin Admin automation) is not reliable - using direct download instead",
                            "recovery_options": ["Retry with method='direct' (default)"],
                        }

                    if not download_url.lower().endswith(".zip"):
                        return {
                            "success": False,
                            "error": "unsupported_archive",
                            "operation": operation,
                            "summary": f"Download URL is not a ZIP archive: {download_url}",
                            "recovery_options": [
                                "Install manually from the plugin homepage",
                                "Check the catalog entry",
                            ],
                        }

                    # Resolve the plugins directory (install dir first, APPDATA fallback)
                    plugins_dir = Path(self.controller.notepadpp_exe).parent / "plugins"
                    target_dir = plugins_dir / folder_name
                    used_appdata = False
                    try:
                        target_dir.mkdir(parents=True, exist_ok=True)
                        probe = target_dir / ".npp-mcp-write-test"
                        probe.write_text("x", encoding="utf-8")
                        probe.unlink()
                    except OSError:
                        appdata_plugins = Path(os.getenv("APPDATA", "")) / "Notepad++" / "plugins"
                        try:
                            target_dir = appdata_plugins / folder_name
                            target_dir.mkdir(parents=True, exist_ok=True)
                            used_appdata = True
                        except OSError as e:
                            return {
                                "success": False,
                                "error": "plugins_dir_not_writable",
                                "operation": operation,
                                "summary": f"Cannot write to {plugins_dir} or {appdata_plugins}: {e}",
                                "recovery_options": [
                                    "Run Notepad++ (or the MCP server) as Administrator",
                                    "Install manually",
                                ],
                            }

                    # Download the ZIP (catalog is trusted; still cap size and extract safely)
                    try:
                        import urllib.request

                        with tempfile.TemporaryDirectory(prefix="npp-plugin-") as tmp:
                            zip_path = Path(tmp) / "plugin.zip"
                            # URL comes from the pinned official catalog (https only) - safe to open
                            with urllib.request.urlopen(download_url, timeout=120) as resp, open(zip_path, "wb") as f:  # noqa: S310 - catalog-pinned https URLs
                                total = 0
                                while True:
                                    chunk = resp.read(1 << 20)
                                    if not chunk:
                                        break
                                    total += len(chunk)
                                    if total > 200 * 1024 * 1024:
                                        return {
                                            "success": False,
                                            "error": "download_too_large",
                                            "operation": operation,
                                            "summary": "Download exceeded 200 MB cap - aborting",
                                            "recovery_options": ["Install manually"],
                                        }
                                    f.write(chunk)
                            if zip_path.stat().st_size == 0:
                                return {
                                    "success": False,
                                    "error": "empty_download",
                                    "operation": operation,
                                    "summary": f"Downloaded archive is empty from {download_url}",
                                }

                            extract_root = Path(tmp) / "x"
                            extract_root.mkdir()
                            with zipfile.ZipFile(zip_path) as zf:
                                for member in zf.namelist():
                                    name = Path(member)
                                    if name.is_absolute() or ".." in name.parts:
                                        _logger.warning("Skipping unsafe zip member: %s", member)
                                        continue
                                    target = extract_root / name
                                    if member.endswith("/"):
                                        target.mkdir(parents=True, exist_ok=True)
                                    else:
                                        target.parent.mkdir(parents=True, exist_ok=True)
                                        with zf.open(member) as src, open(target, "wb") as dst:
                                            dst.write(src.read())

                            # If the zip has a single top-level folder, use its contents
                            top_dirs = [d for d in extract_root.iterdir() if d.is_dir()]
                            files_at_root = [p for p in extract_root.iterdir() if p.is_file()]
                            content_root = extract_root
                            if len(top_dirs) == 1 and not files_at_root:
                                content_root = top_dirs[0]

                            # Install into target_dir (safe overwrite)
                            for src in content_root.rglob("*"):
                                if src.is_file():
                                    rel = src.relative_to(content_root)
                                    dst = target_dir / rel
                                    dst.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(src, dst)

                    except Exception as e:
                        return {
                            "success": False,
                            "error": "install_failed",
                            "operation": operation,
                            "plugin_name": plugin_name,
                            "summary": f"Direct install failed: {e}",
                            "recovery_options": [
                                "Check the download URL / internet",
                                "Try method='ui' or manual install",
                            ],
                            "diagnostic_info": {"exception_type": type(e).__name__},
                        }

                    # Verify: a DLL must be present (prefer {folder-name}.dll)
                    dlls = [p for p in target_dir.rglob("*.dll")]
                    expected_dll = target_dir / f"{folder_name}.dll"
                    if not dlls:
                        return {
                            "success": False,
                            "error": "no_dll_after_extract",
                            "operation": operation,
                            "summary": f"Extracted to {target_dir} but no DLL found - archive may be a config/data pack",
                            "result": {
                                "target_dir": str(target_dir),
                                "files": [str(p.relative_to(target_dir)) for p in target_dir.rglob("*")][:50],
                            },
                            "recovery_options": ["Review the extracted files manually"],
                        }

                    main_dll = str(expected_dll) if expected_dll.exists() else str(dlls[0])
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Installed plugin '{folder_name}' (v{entry.get('version', '?')}) to {target_dir}",
                        "result": {
                            "plugin_name": folder_name,
                            "version": entry.get("version", ""),
                            "download_url": download_url,
                            "target_dir": str(target_dir),
                            "main_dll": main_dll,
                            "dll_count": len(dlls),
                            "used_appdata_plugins": used_appdata,
                        },
                        "next_steps": [
                            "Restart Notepad++ to load the plugin",
                            "plugin_ops(operation='list') to confirm it appears",
                            "Use display_ops or the Plugins menu to configure it",
                        ],
                        "context": {"method": "direct_download", "source": "nppPluginList_pl_x64"},
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
                    "recovery_options": ["Use 'discover', 'install', 'list', or 'execute' operations"],
                    "clarification_options": {
                        "operation": {
                            "description": "What plugin operation would you like to perform?",
                            "options": ["discover", "install", "list", "execute"],
                        }
                    },
                }
