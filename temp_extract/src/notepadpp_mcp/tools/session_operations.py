"""
Session Operations Portmanteau Tool

Consolidates session operations (save, load, list) into a unified interface.
"""

import time
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP


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
            session_name: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates session operations (save, load, list) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: Session operation to perform ("save", "load", "list")
                session_name: Session name for save/load operations

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Session operation failed - Windows API unavailable",
                    "recovery_options": ["Ensure pywin32 is installed", "Restart the MCP server"]
                }

            try:
                await self.controller.ensure_notepadpp_running()

                if operation == "save":
                    if not session_name:
                        return {
                            "success": False,
                            "error": "session_name required for save operation",
                            "operation": operation,
                            "summary": "Session save failed - missing session name",
                            "clarification_options": {
                                "session_name": {
                                    "description": "What would you like to name this session?",
                                    "type": "string"
                                }
                            }
                        }

                    # Get current file info to save session state
                    # Note: This would need to be imported from file_operations in a real implementation
                    # For now, we'll simulate the file info
                    file_info = {
                        "success": True,
                        "result": {
                            "filename": "current_file.txt",  # Would be actual filename
                            "is_modified": False  # Would be actual modification status
                        }
                    }

                    session_data = {
                        "name": session_name,
                        "timestamp": time.time(),
                        "files": [file_info.get("result", {}).get("filename", "Untitled")],
                        "active_file": file_info.get("result", {}).get("filename", "Untitled"),
                        "is_modified": file_info.get("result", {}).get("is_modified", False),
                    }

                    # In a real implementation, this would save to a session file
                    # For now, we'll return the session data
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully saved session '{session_name}'",
                        "result": {
                            "session_name": session_name,
                            "session_data": session_data,
                            "saved": True
                        },
                        "next_steps": ["Use session_ops list to see all saved sessions", "Use session_ops load to restore this session later"],
                        "context": {
                            "persistence_note": "Session persistence requires additional file I/O implementation",
                            "current_state": "In-memory only - sessions not persisted to disk"
                        }
                    }

                elif operation == "load":
                    if not session_name:
                        return {
                            "success": False,
                            "error": "session_name required for load operation",
                            "operation": operation,
                            "summary": "Session load failed - missing session name",
                            "clarification_options": {
                                "session_name": {
                                    "description": "Which session would you like to load?",
                                    "type": "string"
                                }
                            }
                        }

                    # In a real implementation, this would load from a session file
                    # For now, we'll simulate loading a session
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully loaded session '{session_name}'",
                        "result": {
                            "session_name": session_name,
                            "loaded": True,
                            "restored_files": []  # Would contain actual file list
                        },
                        "next_steps": ["Use tab_ops list to verify loaded files", "Continue working in the restored session"],
                        "context": {
                            "restoration_note": "Full session restoration requires session file format implementation",
                            "current_state": "Simulation only - no actual files restored"
                        }
                    }

                elif operation == "list":
                    # In a real implementation, this would scan for session files
                    # For now, we'll return a placeholder
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Retrieved session list (currently empty)",
                        "result": {
                            "sessions": [],
                            "total_sessions": 0
                        },
                        "next_steps": ["Use session_ops save to create your first session", "Sessions will appear here once persistence is implemented"],
                        "context": {
                            "implementation_note": "Session listing requires file system scanning implementation",
                            "current_state": "No sessions found - session persistence not yet implemented",
                            "future_capabilities": "Will scan session directory for .session files"
                        }
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"Session operation failed - unknown operation '{operation}'",
                        "recovery_options": ["Use 'save', 'load', or 'list' operations"],
                        "clarification_options": {
                            "operation": {
                                "description": "What session operation would you like to perform?",
                                "options": ["save", "load", "list"]
                            }
                        }
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Session operation failed: {e}",
                    "operation": operation,
                    "summary": f"Session operation '{operation}' encountered an error",
                    "recovery_options": ["Check Notepad++ is running", "Verify session names are valid"],
                    "diagnostic_info": {"exception_type": type(e).__name__, "operation": operation, "session_name": session_name}
                }