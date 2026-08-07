"""
File Operations Portmanteau Tool

Consolidates file operations (open, new, save, info) into a unified interface.
"""

import asyncio
import datetime
import difflib
import os
import re
import subprocess
from pathlib import Path
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
    win32api: Any = None
    win32con: Any = None
    win32gui: Any = None


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
            operation: Annotated[
                Literal[
                    "open",
                    "new",
                    "save",
                    "save_as",
                    "info",
                    "is_dirty",
                    "reload_from_disk",
                    "find_in_files",
                    "diff_buffer",
                ],
                Field(
                    description=(
                        "Operation: open loads file_path, new creates a buffer, save persists the active buffer "
                        "(with optional timestamped backup), save_as writes the buffer to file_path, info returns file metadata, "
                        "is_dirty reports the active tab state (untitled/dirty), reload_from_disk discards buffer changes, "
                        "find_in_files searches a directory, diff_buffer compares the buffer to the file on disk."
                    )
                ),
            ],
            file_path: Annotated[
                str | None,
                Field(
                    description="Absolute path (required for open/save_as/reload_from_disk; the disk file for diff_buffer)."
                ),
            ] = None,
            backup: Annotated[bool, Field(description="Create a timestamped .bak before save (default True).")] = True,
            overwrite: Annotated[
                bool, Field(description="Allow save_as to overwrite an existing file (default False).")
            ] = False,
            force: Annotated[
                bool, Field(description="Allow reload_from_disk to discard unsaved changes (default False).")
            ] = False,
            search: Annotated[str | None, Field(description="Search pattern for find_in_files (regex).")] = None,
            glob_filter: Annotated[str, Field(description="File glob filter for find_in_files (default *).")] = "*",
            limit: Annotated[
                int, Field(description="Max results for find_in_files (default 100).", ge=1, le=500)
            ] = 100,
            case_sensitive: Annotated[
                bool, Field(description="Case-sensitive matching for find_in_files (default False).")
            ] = False,
            max_lines: Annotated[
                int, Field(description="Max diff lines for diff_buffer (default 200).", ge=10, le=2000)
            ] = 200,
        ) -> dict[str, Any]:
            """FILE_OPS — Open, create, save, inspect, and analyze documents in Notepad++.

            PORTMANTEAU PATTERN RATIONALE: Consolidates file lifecycle + analysis into one tool (see TOOL_DESIGN_STANDARDS.md §1).

            Safety: `save` backs up the on-disk file before persisting (backup=true by default);
            `save_as` refuses to overwrite an existing path unless overwrite=true;
            `reload_from_disk` refuses to discard unsaved changes unless force=true.
            For generation tasks, create a fresh tab with `new` before writing content.

            Operations:
            - open: Load file_path into the editor.
            - new: New empty buffer.
            - save: Persist the current buffer (optional timestamped .bak backup first).
            - save_as: Write the buffer to file_path and open it in Notepad++.
            - info: Metadata for the active file.
            - is_dirty: Active tab state (untitled? dirty? filename?).
            - reload_from_disk: Replace the buffer with the file on disk (guarded).
            - find_in_files: Regex search across a directory (server-side, returns matches).
            - diff_buffer: Unified diff between the active buffer and the file on disk.

            ## Return Format
            {"success": bool, "operation": str, "message": str, "result": {...}, "error": str | null}

            ## Examples
            file_ops(operation="open", file_path="C:/tmp/readme.txt")
            file_ops(operation="save")
            file_ops(operation="save_as", file_path="C:/tmp/poem.txt")
            file_ops(operation="is_dirty")
            file_ops(operation="reload_from_disk", file_path="C:/tmp/readme.txt", force=True)
            file_ops(operation="find_in_files", search="TODO", directory="C:/tmp", glob_filter="*.py")
            file_ops(operation="diff_buffer", file_path="C:/tmp/readme.txt")

            Notes:
             - Windows/pywin32 required; file not found or permission denied returns success=False with error, recovery_options and diagnostic_info.
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available - Notepad++ automation requires pywin32",
                    "error_code": "WINDOWS_API_UNAVAILABLE",
                    "operation": operation,
                    "summary": "File operation failed - Windows API unavailable",
                    "message": "The Notepad++ MCP server requires pywin32 to automate Notepad++ operations. This is a Windows-specific requirement for UI automation.",
                    "recovery_options": [
                        "Install pywin32: pip install pywin32",
                        "Ensure you're running on Windows OS",
                        "Restart the MCP server after installation",
                        "Verify Notepad++ is properly installed",
                    ],
                    "diagnostic_info": {
                        "pywin32_available": WINDOWS_AVAILABLE,
                        "platform": "windows",
                        "required_package": "pywin32",
                    },
                    "alternative_solutions": [
                        "Use manual file operations in Notepad++",
                        "Consider using text-based tools if Windows API is unavailable",
                    ],
                    "estimated_resolution_time": "2-5 minutes",
                    "urgency": "high",
                    "suggestions": ["Install pywin32 to enable full Notepad++ automation"],
                    "follow_up_questions": ["Would you like me to help you install pywin32?"],
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
                                    "type": "file_path",
                                }
                            },
                        }

                    # Convert to absolute path
                    abs_path = os.path.abspath(file_path)

                    if not os.path.exists(abs_path):
                        return {
                            "success": False,
                            "error": f"File '{os.path.basename(abs_path)}' was not found at the specified location",
                            "error_code": "FILE_NOT_FOUND",
                            "operation": operation,
                            "summary": f"Unable to open file - the path '{abs_path}' doesn't exist",
                            "message": f"I couldn't find a file at '{abs_path}'. This commonly happens due to typos in the path, moved/renamed files, or incorrect directory navigation.",
                            "recovery_options": [
                                "Double-check the file path for spelling errors",
                                "Verify the file exists in File Explorer",
                                "Use an absolute path instead of relative",
                                "Browse to the correct directory and copy the full path",
                            ],
                            "diagnostic_info": {
                                "requested_path": abs_path,
                                "directory_exists": os.path.exists(os.path.dirname(abs_path)) if abs_path else False,
                                "exists": False,
                                "path_type": "absolute" if os.path.isabs(abs_path) else "relative",
                            },
                            "alternative_solutions": [
                                "Use file_ops with 'new' to create a new file",
                                "Search for similar files in the directory",
                                "List directory contents to see available files",
                            ],
                            "estimated_resolution_time": "< 2 minutes",
                            "urgency": "medium",
                            "suggestions": [
                                "Try using tab completion or file browser for accurate paths",
                                "Consider saving important files in well-known locations",
                            ],
                            "follow_up_questions": [
                                "Can you double-check the file path?",
                                "Would you like me to help you find the correct file?",
                                "Should I list files in the directory to help you find it?",
                            ],
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
                        "summary": f"Successfully opened '{os.path.basename(abs_path)}' in Notepad++",
                        "result": {
                            "file_path": abs_path,
                            "file_name": os.path.basename(abs_path),
                            "file_size": os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
                            "action_taken": "file_opened",
                        },
                        "next_steps": [
                            "Edit the file content using text operations",
                            "Search for specific text in the file",
                            "Save your changes when done editing",
                        ],
                        "context": {
                            "file_path": abs_path,
                            "file_size": os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
                            "last_modified": os.path.getmtime(abs_path) if os.path.exists(abs_path) else None,
                            "encoding": "detected_encoding",  # Would be detected in real implementation
                        },
                        "suggestions": [
                            "Use text_ops tool for find/replace operations",
                            "Consider saving your work frequently",
                            "Use tab_ops to manage multiple open files",
                        ],
                        "follow_up_questions": [
                            "Would you like me to help you edit this file?",
                            "Do you need to search for specific text in this file?",
                            "Should I show you how to navigate between tabs?",
                        ],
                    }

                elif operation == "new":
                    # File > New (Ctrl+N) - creates an untitled tab
                    if not self.controller.new_document():
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - new tab aborted",
                            "recovery_options": ["Bring Notepad++ to the foreground and retry"],
                        }
                    await asyncio.sleep(0.3)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Created a new untitled document in Notepad++",
                        "result": {
                            "created": True,
                            "file_type": "untitled",
                            "action_taken": "new_document_created",
                        },
                        "next_steps": [
                            "Start typing your content",
                            "Use text_ops to insert or edit text",
                            "Save the file with a name using file_ops save",
                            "Use tab_ops to manage multiple documents",
                        ],
                        "context": {
                            "file_type": "untitled",
                            "tab_position": "active",
                            "content_length": 0,
                        },
                        "suggestions": [
                            "Start by inserting some text content",
                            "Consider saving with a meaningful filename",
                            "Use syntax highlighting if writing code",
                        ],
                        "follow_up_questions": [
                            "What content would you like to add to this new file?",
                            "Do you want me to help you save it with a specific name?",
                            "Are you writing code or plain text?",
                        ],
                    }

                elif operation == "save":
                    tab_state = self.controller.get_active_tab_state()
                    backup_path = None
                    disk_path = tab_state.get("path") or ""
                    if backup and disk_path and os.path.exists(disk_path) and not tab_state["untitled"]:
                        # Timestamped backup of the on-disk file BEFORE the app's Ctrl+S overwrites it
                        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_path = f"{disk_path}.{ts}.bak"
                        try:
                            with open(disk_path, "rb") as src, open(backup_path, "wb") as dst:
                                dst.write(src.read())
                        except OSError:
                            backup_path = None
                    # Save via File > Save (Ctrl+S)
                    if not self.controller.save_current():
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - save aborted",
                            "recovery_options": ["Bring Notepad++ to the foreground and retry"],
                        }
                    await asyncio.sleep(0.3)

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": "Successfully saved the current document in Notepad++"
                        + (f" (backup: {backup_path})" if backup_path else ""),
                        "result": {
                            "saved": True,
                            "action_taken": "file_saved",
                            "backup_path": backup_path,
                            "target_tab": tab_state,
                        },
                        "next_steps": [
                            "Continue editing your document",
                            "Use file_ops info to check file details",
                            "Create a backup copy if needed",
                            "Share the file with others",
                        ],
                        "context": {
                            "save_time": "current",
                            "file_status": "saved",
                            "modified_flag": False,
                        },
                        "suggestions": [
                            "Consider creating regular backups of important files",
                            "Use version control for collaborative work",
                            "Check file size and encoding if working with large files",
                        ],
                        "follow_up_questions": [
                            "Would you like me to show you the file information?",
                            "Do you need to make any more edits to this file?",
                            "Should I help you create a backup copy?",
                        ],
                    }

                elif operation == "info":
                    tab_state = self.controller.get_active_tab_state()
                    filename = tab_state["filename"] or "Untitled"
                    is_modified = tab_state["dirty"]
                    disk_path = tab_state.get("path") or ""
                    disk_mtime = None
                    disk_size = None
                    if disk_path and os.path.exists(disk_path):
                        try:
                            st = os.stat(disk_path)
                            disk_mtime = datetime.datetime.fromtimestamp(st.st_mtime).isoformat()
                            disk_size = st.st_size
                        except OSError:
                            pass

                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Current active file is '{filename}'{' (modified)' if is_modified else ''}",
                        "result": {
                            "window_title": tab_state["title"],
                            "filename": filename,
                            "path": disk_path,
                            "is_modified": is_modified,
                            "is_untitled": tab_state["untitled"],
                            "disk_modified": disk_mtime,
                            "disk_size": disk_size,
                            "file_status": "modified" if is_modified else "saved",
                            "action_taken": "file_info_retrieved",
                        },
                        "next_steps": [
                            "Use text_ops to edit the content"
                            if not is_modified
                            else "Save your changes using file_ops save",
                            "Continue editing if needed",
                            "Use tab_ops to switch between files",
                        ]
                        if not is_modified
                        else [
                            "Save your changes to preserve work",
                            "Use text_ops to continue editing",
                            "Consider creating a backup before further changes",
                        ],
                        "context": {
                            "has_unsaved_changes": is_modified,
                            "file_name": filename,
                            "window_title": tab_state["title"],
                            "modification_status": "modified" if is_modified else "clean",
                        },
                        "suggestions": [
                            "Save frequently when making important changes"
                            if is_modified
                            else "Continue editing or open another file",
                            "Use version control for important documents",
                            "Regular backups prevent data loss",
                        ],
                        "follow_up_questions": [
                            "Do you need to save these changes?"
                            if is_modified
                            else "Would you like to edit this file?",
                            "Should I help you work with this file?",
                            "Do you want to open another file?",
                        ],
                    }

                elif operation == "is_dirty":
                    tab_state = self.controller.get_active_tab_state()
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": (
                            f"Tab '{tab_state['filename'] or 'Untitled'}' is "
                            f"{'dirty (unsaved changes)' if tab_state['dirty'] else 'clean'}"
                            f"{' (untitled)' if tab_state['untitled'] else ''}"
                        ),
                        "result": tab_state,
                        "next_steps": [
                            "Use file_ops save to persist changes" if tab_state["dirty"] else "No action needed",
                            "Use file_ops save_as to write to a path" if tab_state["untitled"] else "Tab has a path",
                        ],
                    }

                elif operation == "save_as":
                    if not file_path:
                        return {
                            "success": False,
                            "error": "file_path required for save_as",
                            "operation": operation,
                            "summary": "save_as requires a target path",
                            "recovery_options": ["Provide file_path to write the buffer to"],
                        }
                    abs_path = os.path.abspath(file_path)
                    parent = os.path.dirname(abs_path)
                    if not os.path.isdir(parent):
                        return {
                            "success": False,
                            "error": "directory_missing",
                            "operation": operation,
                            "summary": f"Target directory does not exist: {parent}",
                            "recovery_options": ["Create the directory first", "Use an existing directory"],
                        }
                    if os.path.exists(abs_path) and not overwrite:
                        return {
                            "success": False,
                            "error": "file_exists",
                            "operation": operation,
                            "summary": f"Refusing to overwrite existing file: {abs_path}",
                            "recovery_options": [
                                "file_ops(operation='save_as', file_path=..., overwrite=true) to replace it",
                                "Choose a different file_path",
                            ],
                        }
                    buffer_text, _source = self.controller.get_buffer_text()
                    with open(abs_path, "w", encoding="utf-8", newline="") as f:
                        f.write(buffer_text)
                    # Open the saved file in Notepad++ so the app switches to it
                    subprocess.Popen(
                        [self.controller.notepadpp_exe, abs_path],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    await asyncio.sleep(0.5)
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Saved buffer to {abs_path} ({len(buffer_text)} chars)",
                        "result": {"file_path": abs_path, "written_chars": len(buffer_text), "opened_in_editor": True},
                        "next_steps": [
                            "Close the old untitled tab if it is still open: tab_ops(operation='close')",
                            "Continue editing in the newly opened tab",
                        ],
                    }

                elif operation == "reload_from_disk":
                    if not file_path:
                        return {
                            "success": False,
                            "error": "file_path required for reload_from_disk",
                            "operation": operation,
                            "summary": "reload_from_disk requires the file path to reload",
                            "recovery_options": ["Provide file_path of the file to reload"],
                        }
                    abs_path = os.path.abspath(file_path)
                    if not os.path.exists(abs_path):
                        return {
                            "success": False,
                            "error": "file_not_found",
                            "operation": operation,
                            "summary": f"File not found: {abs_path}",
                            "recovery_options": ["Check the path", "Use file_ops open to create/load it"],
                        }
                    tab_state = self.controller.get_active_tab_state()
                    if tab_state["dirty"] and not force:
                        return {
                            "success": False,
                            "error": "unsaved_changes",
                            "operation": operation,
                            "summary": "Refusing to discard unsaved changes in the active tab",
                            "recovery_options": [
                                "file_ops(operation='reload_from_disk', file_path=..., force=true) to discard changes",
                                "file_ops(operation='save') first to keep them",
                            ],
                            "context": tab_state,
                        }
                    with open(abs_path, encoding="utf-8", errors="replace") as f:
                        disk_text = f.read()
                    if not self.controller.set_buffer_text(disk_text):
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - reload aborted",
                            "recovery_options": ["Bring Notepad++ to the foreground and retry"],
                        }
                    if not self.controller.verify_buffer(disk_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Reload ran but verification failed",
                            "recovery_options": ["Retry once"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Reloaded buffer from {abs_path} ({len(disk_text)} chars) - verified",
                        "result": {
                            "file_path": abs_path,
                            "loaded_chars": len(disk_text),
                            "discarded_changes": tab_state["dirty"],
                        },
                    }

                elif operation == "find_in_files":
                    if not search or not file_path:
                        return {
                            "success": False,
                            "error": "missing_parameters",
                            "operation": operation,
                            "summary": "find_in_files requires a search pattern and a directory",
                            "recovery_options": ["Provide search (regex) and file_path (directory)"],
                        }
                    root = os.path.abspath(file_path)
                    if not os.path.isdir(root):
                        return {
                            "success": False,
                            "error": "directory_missing",
                            "operation": operation,
                            "summary": f"Not a directory: {root}",
                            "recovery_options": ["Provide an existing directory path"],
                        }
                    try:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        pattern = re.compile(search, flags)
                    except re.error as e:
                        return {
                            "success": False,
                            "error": "invalid_regex",
                            "operation": operation,
                            "summary": f"Invalid regular expression: {e}",
                        }
                    hits: list[dict[str, Any]] = []
                    total_files = 0
                    for p in Path(root).rglob(glob_filter):
                        if not p.is_file():
                            continue
                        total_files += 1
                        try:
                            if p.stat().st_size > 2 * 1024 * 1024:
                                continue
                            with open(p, encoding="utf-8", errors="replace") as f:
                                for lineno, line in enumerate(f, start=1):
                                    if len(hits) >= limit:
                                        break
                                    if pattern.search(line):
                                        hits.append(
                                            {
                                                "file": str(p),
                                                "line": lineno,
                                                "text": line.rstrip()[:300],
                                            }
                                        )
                                if len(hits) >= limit:
                                    break
                        except OSError:
                            continue
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Found {len(hits)} match(es) across {total_files} file(s)",
                        "result": {
                            "matches": hits,
                            "match_count": len(hits),
                            "files_scanned": total_files,
                            "truncated": len(hits) >= limit,
                        },
                        "next_steps": [
                            "Use file_ops open to open a matched file",
                            "Narrow the glob_filter to reduce noise",
                        ],
                    }

                elif operation == "diff_buffer":
                    if not file_path:
                        return {
                            "success": False,
                            "error": "file_path required for diff_buffer",
                            "operation": operation,
                            "summary": "diff_buffer requires the disk file path to compare against",
                            "recovery_options": ["Provide file_path of the file on disk"],
                        }
                    abs_path = os.path.abspath(file_path)
                    if not os.path.exists(abs_path):
                        return {
                            "success": False,
                            "error": "file_not_found",
                            "operation": operation,
                            "summary": f"File not found: {abs_path}",
                        }
                    buffer_text, _source = self.controller.get_buffer_text()
                    with open(abs_path, encoding="utf-8", errors="replace") as f:
                        disk_text = f.read()
                    if buffer_text == disk_text:
                        return {
                            "success": True,
                            "operation": operation,
                            "summary": "Buffer matches the file on disk - no differences",
                            "result": {"identical": True, "diff_lines": 0},
                        }
                    diff = list(
                        difflib.unified_diff(
                            disk_text.splitlines(),
                            buffer_text.splitlines(),
                            fromfile=os.path.basename(abs_path) + " (disk)",
                            tofile=os.path.basename(abs_path) + " (buffer)",
                            lineterm="",
                            n=2,
                        )
                    )
                    truncated = len(diff) > max_lines
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Buffer differs from disk ({len(diff)} diff lines)"
                        + (" - truncated" if truncated else ""),
                        "result": {
                            "identical": False,
                            "diff": diff[:max_lines],
                            "diff_lines": len(diff),
                            "truncated": truncated,
                        },
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"File operation failed - unknown operation '{operation}'",
                        "recovery_options": [
                            "Use 'open', 'new', 'save', 'save_as', 'info', 'is_dirty', 'reload_from_disk', 'find_in_files', or 'diff_buffer' operations"
                        ],
                        "clarification_options": {
                            "operation": {
                                "description": "What file operation would you like to perform?",
                                "options": [
                                    "open",
                                    "new",
                                    "save",
                                    "save_as",
                                    "info",
                                    "is_dirty",
                                    "reload_from_disk",
                                    "find_in_files",
                                    "diff_buffer",
                                ],
                            }
                        },
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"File operation failed: {e}",
                    "operation": operation,
                    "summary": f"File operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Verify file permissions",
                        "Restart Notepad++",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                    },
                }
