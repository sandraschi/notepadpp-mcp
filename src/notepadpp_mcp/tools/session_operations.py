"""
Session Operations Portmanteau Tool

Persists named sessions as Notepad++-compatible session XML (see npp_session_store).
"""

from __future__ import annotations

import asyncio
from typing import Any, Literal

from fastmcp import FastMCP

from .. import npp_session_store
from ..editor_bridge import normalize_title_filename, try_resolve_path_from_hint


class SessionOperationsTool:
    """Portmanteau tool for session operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the session operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register session operations portmanteau tool."""

        @self.app.tool()
        async def session_ops(
            operation: Literal["save", "load", "list"],
            session_name: str | None = None,
        ) -> dict[str, Any]:
            """SESSION_OPS — Save, load, or list persisted Notepad++ workspace sessions.

            PORTMANTEAU PATTERN RATIONALE: One tool for save/load/list (TOOL_DESIGN_STANDARDS.md).

            Save copies Notepad++ live session.xml (all open buffers) into a named XML under the
            MCP storage folder, loadable by Notepad++ via -openSession. If Live session is empty,
            falls back to the active tab path when it resolves to a real file on disk.

            Operations:
            - save: Copy current session to disk as session_name.xml.
            - load: Run Notepad++ with -openSession on that saved file.
            - list: List saved session files with paths and file counts.

            Args:
                operation (Literal, required): "save" | "load" | "list".
                session_name (str | None): Required for save and load (stem; .xml added automatically).

            Returns:
                dict with success, operation, summary, result (paths, sessions, counts).

            Examples:
                await session_ops("save", session_name="morning_work")
                await session_ops("list")
                await session_ops("load", session_name="morning_work")

            Errors:
                Missing name, session not found, permissions, empty session, or Windows unavailable.
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Session operation failed - Windows API unavailable",
                    "recovery_options": [
                        "Ensure pywin32 is installed",
                        "Restart the MCP server",
                    ],
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "save":
                    if not session_name or not session_name.strip():
                        return {
                            "success": False,
                            "error": "session_name required for save operation",
                            "operation": operation,
                            "summary": "Session save failed - missing session name",
                            "clarification_options": {
                                "session_name": {
                                    "description": "What would you like to name this session?",
                                    "type": "string",
                                }
                            },
                        }

                    window_text = await self.controller.get_window_text(self.controller.hwnd)
                    fallback: list[str] = []
                    if " - Notepad++" in window_text:
                        fn = normalize_title_filename(
                            window_text.split(" - Notepad++")[0],
                        )
                        resolved = try_resolve_path_from_hint(fn)
                        if resolved:
                            fallback.append(resolved)

                    try:
                        result = await asyncio.to_thread(
                            npp_session_store.save_named_session,
                            session_name.strip(),
                            fallback_paths=fallback or None,
                        )
                    except ValueError as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "operation": operation,
                            "summary": "Session save failed",
                            "recovery_options": [
                                "Open at least one saved file in Notepad++ so session.xml lists paths",
                                "Exit and restart Notepad++ once if session.xml is missing",
                                "Set NOTEPADPP_LIVE_SESSION_XML if using a custom config directory",
                            ],
                        }
                    except OSError as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "operation": operation,
                            "summary": "Session save failed - could not read or write session files",
                            "recovery_options": [
                                "Check permissions on %APPDATA%\\Notepad++",
                                "Close other programs locking session.xml",
                            ],
                        }

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": (
                            f"Saved session '{result['session_name']}' "
                            f"({result['file_count']} file(s), source={result['source']})"
                        ),
                        "result": result,
                        "next_steps": [
                            "Use session_ops list to see saved sessions",
                            "Use session_ops load to open this session in Notepad++",
                        ],
                    }

                if operation == "load":
                    if not session_name or not session_name.strip():
                        return {
                            "success": False,
                            "error": "session_name required for load operation",
                            "operation": operation,
                            "summary": "Session load failed - missing session name",
                            "clarification_options": {
                                "session_name": {
                                    "description": "Which session would you like to load?",
                                    "type": "string",
                                }
                            },
                        }
                    try:
                        out = await asyncio.to_thread(
                            npp_session_store.load_session_subprocess,
                            session_name.strip(),
                            self.controller.notepadpp_exe,
                        )
                    except FileNotFoundError as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "operation": operation,
                            "summary": "Session load failed - file not found",
                            "recovery_options": [
                                "Use session_ops list to see valid session names",
                                "Use session_ops save to create a session first",
                            ],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Started Notepad++ with saved session '{out['session_name']}'",
                        "result": out,
                        "next_steps": [
                            "Use tab_ops list to verify open files",
                            "If nothing opens, check Multi-instance settings in Notepad++ preferences",
                        ],
                    }

                if operation == "list":
                    rows = await asyncio.to_thread(npp_session_store.list_saved_sessions)
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Found {len(rows)} saved session(s)",
                        "result": {
                            "sessions": rows,
                            "total_sessions": len(rows),
                            "storage_dir": str(npp_session_store.session_storage_dir()),
                        },
                        "next_steps": [
                            "Use session_ops load with a session name to open one",
                            "Use session_ops save to add another named snapshot",
                        ],
                    }

                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation,
                    "summary": f"Session operation failed - unknown operation '{operation}'",
                    "recovery_options": ["Use 'save', 'load', or 'list' operations"],
                    "clarification_options": {
                        "operation": {
                            "description": "What session operation would you like to perform?",
                            "options": ["save", "load", "list"],
                        }
                    },
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Session operation failed: {e}",
                    "operation": operation,
                    "summary": f"Session operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Verify session names are valid",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                        "session_name": session_name,
                    },
                }
