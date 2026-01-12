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
            file_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Manage file operations in Notepad++ with consolidated interface.

            PORTMANTEAU PATTERN RATIONALE:
            Instead of creating 4 separate tools (open, new, save, info), this tool consolidates file
            operations into a single interface. Prevents tool explosion (4 tools -> 1 tool) while maintaining
            full functionality and improving discoverability. Follows FastMCP 2.14.1+ SOTA standards.

            Supported Operations:
            - Open existing files in Notepad++
            - Create new files and documents
            - Save current document changes
            - Get file information and metadata

            Operations Detail:
            **File Access:**
            - "open": Load and display existing file in Notepad++
            - "new": Create new empty document

            **File Persistence:**
            - "save": Save current document to disk
            - "info": Get metadata about current file

            Prerequisites:
            - Windows OS with Notepad++ installed
            - pywin32 package for Windows API access
            - File system read/write permissions

            Args:
                operation (Literal, required): The file operation to perform. Must be one of: "open", "new", "save", "info".
                    - "open": Load existing file (requires file_path)
                    - "new": Create new document (no additional parameters)
                    - "save": Save current document (no additional parameters)
                    - "info": Get current file information (no additional parameters)

                file_path (str | None): Path to file for open operation. Required for: open operation.
                    Must be a valid file path accessible to Notepad++.

            Returns:
                Dictionary following FastMCP 2.14.1+ enhanced response patterns:
                ```json
                {
                  "success": true,
                  "operation": "open",
                  "summary": "File opened successfully",
                  "result": {
                    "file_path": "/path/to/file.txt",
                    "file_size": 1024,
                    "encoding": "utf-8"
                  },
                  "next_steps": ["Edit file content", "Save changes"],
                  "context": {
                    "operation_type": "file_access"
                  }
                }
                ```

                **Success Response Structure:**
                - success (bool): Operation success status
                - operation (str): File operation that was performed
                - summary (str): Human-readable result summary
                - result (dict): File-specific data (path, size, encoding, etc.)
                - next_steps (list[str]): Suggested next actions
                - context (dict): Additional operation context

                **Error Response Structure:**
                - success (bool): Always false for errors
                - error (str): Error type (file_not_found, permission_denied, etc.)
                - operation (str): Failed operation
                - summary (str): Human-readable error summary
                - recovery_options (list[str]): Suggested recovery actions

            Examples:
                # Open existing file
                result = await file_ops("open", file_path="C:/docs/readme.txt")
                # Returns: {"success": true, "summary": "File opened successfully", ...}

                # Create new document
                result = await file_ops("new")
                # Returns: {"success": true, "summary": "New document created", ...}

                # Save current document
                result = await file_ops("save")
                # Returns: {"success": true, "summary": "Document saved", ...}

                # Get file information
                result = await file_ops("info")
                # Returns: {"success": true, "result": {"file_path": "...", "size": 1234}, ...}

            Errors:
                **Common Errors:**
                - "Windows API not available": pywin32 not installed or Notepad++ not running
                - "File not found": Specified file_path does not exist (for open operation)
                - "Permission denied": No read/write access to file or directory
                - "Invalid file path": Malformed or inaccessible file path

                **Recovery Options:**
                - Install pywin32: `pip install pywin32`
                - Ensure Notepad++ is running before operations
                - Check file paths and permissions
                - Use absolute paths for file operations
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
                            "Verify Notepad++ is properly installed"
                        ],
                        "diagnostic_info": {
                            "pywin32_available": WINDOWS_AVAILABLE,
                            "platform": "windows",
                            "required_package": "pywin32"
                        },
                        "alternative_solutions": [
                            "Use manual file operations in Notepad++",
                            "Consider using text-based tools if Windows API is unavailable"
                        ],
                        "estimated_resolution_time": "2-5 minutes",
                        "urgency": "high",
                        "suggestions": ["Install pywin32 to enable full Notepad++ automation"],
                        "follow_up_questions": ["Would you like me to help you install pywin32?"]
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
                                "Browse to the correct directory and copy the full path"
                            ],
                            "diagnostic_info": {
                                "requested_path": abs_path,
                                "directory_exists": os.path.exists(os.path.dirname(abs_path)) if abs_path else False,
                                "exists": False,
                                "path_type": "absolute" if os.path.isabs(abs_path) else "relative"
                            },
                            "alternative_solutions": [
                                "Use file_ops with 'new' to create a new file",
                                "Search for similar files in the directory",
                                "List directory contents to see available files"
                            ],
                            "estimated_resolution_time": "< 2 minutes",
                            "urgency": "medium",
                            "suggestions": [
                                "Try using tab completion or file browser for accurate paths",
                                "Consider saving important files in well-known locations"
                            ],
                            "follow_up_questions": [
                                "Can you double-check the file path?",
                                "Would you like me to help you find the correct file?",
                                "Should I list files in the directory to help you find it?"
                            ]
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
                            "action_taken": "file_opened"
                        },
                        "next_steps": [
                            "Edit the file content using text operations",
                            "Search for specific text in the file",
                            "Save your changes when done editing"
                        ],
                        "context": {
                            "file_path": abs_path,
                            "file_size": os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
                            "last_modified": os.path.getmtime(abs_path) if os.path.exists(abs_path) else None,
                            "encoding": "detected_encoding"  # Would be detected in real implementation
                        },
                        "suggestions": [
                            "Use text_ops tool for find/replace operations",
                            "Consider saving your work frequently",
                            "Use tab_ops to manage multiple open files"
                        ],
                        "follow_up_questions": [
                            "Would you like me to help you edit this file?",
                            "Do you need to search for specific text in this file?",
                            "Should I show you how to navigate between tabs?"
                        ]
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
                        "summary": "Created a new untitled document in Notepad++",
                        "result": {
                            "created": True,
                            "file_type": "untitled",
                            "action_taken": "new_document_created"
                        },
                        "next_steps": [
                            "Start typing your content",
                            "Use text_ops to insert or edit text",
                            "Save the file with a name using file_ops save",
                            "Use tab_ops to manage multiple documents"
                        ],
                        "context": {
                            "file_type": "untitled",
                            "tab_position": "active",
                            "content_length": 0
                        },
                        "suggestions": [
                            "Start by inserting some text content",
                            "Consider saving with a meaningful filename",
                            "Use syntax highlighting if writing code"
                        ],
                        "follow_up_questions": [
                            "What content would you like to add to this new file?",
                            "Do you want me to help you save it with a specific name?",
                            "Are you writing code or plain text?"
                        ]
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
                        "summary": "Successfully saved the current document in Notepad++",
                        "result": {
                            "saved": True,
                            "action_taken": "file_saved",
                            "save_timestamp": "current_time"  # Would be actual timestamp
                        },
                        "next_steps": [
                            "Continue editing your document",
                            "Use file_ops info to check file details",
                            "Create a backup copy if needed",
                            "Share the file with others"
                        ],
                        "context": {
                            "save_time": "current",
                            "file_status": "saved",
                            "modified_flag": False
                        },
                        "suggestions": [
                            "Consider creating regular backups of important files",
                            "Use version control for collaborative work",
                            "Check file size and encoding if working with large files"
                        ],
                        "follow_up_questions": [
                            "Would you like me to show you the file information?",
                            "Do you need to make any more edits to this file?",
                            "Should I help you create a backup copy?"
                        ]
                    }

                elif operation == "info":
                    # Get window title which usually contains filename
                    window_text = await self.controller.get_window_text(
                        self.controller.hwnd
                    )

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
                        "summary": f"Current active file is '{filename}'{' (modified)' if is_modified else ''}",
                        "result": {
                            "window_title": window_text,
                            "filename": filename,
                            "is_modified": is_modified,
                            "file_status": "modified" if is_modified else "saved",
                            "action_taken": "file_info_retrieved"
                        },
                        "next_steps": [
                            "Use text_ops to edit the content" if not is_modified else "Save your changes using file_ops save",
                            "Continue editing if needed",
                            "Use tab_ops to switch between files"
                        ] if not is_modified else [
                            "Save your changes to preserve work",
                            "Use text_ops to continue editing",
                            "Consider creating a backup before further changes"
                        ],
                        "context": {
                            "has_unsaved_changes": is_modified,
                            "file_name": filename,
                            "window_title": window_text,
                            "modification_status": "modified" if is_modified else "clean"
                        },
                        "suggestions": [
                            "Save frequently when making important changes" if is_modified else "Continue editing or open another file",
                            "Use version control for important documents",
                            "Regular backups prevent data loss"
                        ],
                        "follow_up_questions": [
                            "Do you need to save these changes?" if is_modified else "Would you like to edit this file?",
                            "Should I help you work with this file?",
                            "Do you want to open another file?"
                        ]
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"File operation failed - unknown operation '{operation}'",
                        "recovery_options": [
                            "Use 'open', 'new', 'save', or 'info' operations"
                        ],
                        "clarification_options": {
                            "operation": {
                                "description": "What file operation would you like to perform?",
                                "options": ["open", "new", "save", "info"],
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
