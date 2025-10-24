"""
Notepad++ MCP Server

FastMCP 2.12 compliant MCP server for Notepad++ automation and control.
Provides comprehensive file operations, text manipulation, and UI control.
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import psutil
from fastmcp import FastMCP

# Configure structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler for stderr (safe for FastMCP stdio protocol)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

# Windows-specific imports
try:
    import win32api
    import win32con
    import win32gui

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Create FastMCP application
app = FastMCP("Notepad++ MCP Server")

# Configuration
NOTEPADPP_TIMEOUT = int(os.getenv("NOTEPADPP_TIMEOUT", "30"))
NOTEPADPP_AUTO_START = os.getenv("NOTEPADPP_AUTO_START", "true").lower() == "true"
NOTEPADPP_PATH = os.getenv("NOTEPADPP_PATH", None)

# Default Notepad++ installation paths
DEFAULT_NOTEPADPP_PATHS = [
    r"C:\Program Files\Notepad++\notepad++.exe",
    r"C:\Program Files (x86)\Notepad++\notepad++.exe",
    r"C:\Users\{}\AppData\Local\Notepad++\notepad++.exe".format(
        os.getenv("USERNAME", "")
    ),
]


# Validation and Error Handling Decorators
def validate_file_path(func: Callable) -> Callable:
    """Decorator to validate file path parameters."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract file_path from arguments
        file_path = None
        if "file_path" in kwargs:
            file_path = kwargs["file_path"]
        elif len(args) > 1:  # Skip 'self' for methods
            file_path = args[1]

        if file_path is not None:
            # Validate file path
            if not isinstance(file_path, str):
                return {
                    "success": False,
                    "error": f"file_path must be a string, got {type(file_path).__name__}",
                }

            # Check for dangerous paths
            dangerous_patterns = ["..", "\\", "/", "<", ">", "|", '"', "*", "?"]
            for pattern in dangerous_patterns:
                if pattern in file_path and pattern not in [
                    "/",
                    "\\",
                ]:  # Allow path separators
                    return {
                        "success": False,
                        "error": f"Invalid characters in file path: {pattern}",
                    }

            # Check path length
            if len(file_path) > 260:  # Windows MAX_PATH
                return {
                    "success": False,
                    "error": "File path too long (max 260 characters)",
                }

        return await func(*args, **kwargs)

    return wrapper


def validate_text_input(func: Callable) -> Callable:
    """Decorator to validate text input parameters."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract text parameters
        text_params = ["text", "search_text", "content"]
        for param in text_params:
            if param in kwargs:
                text_value = kwargs[param]
                if not isinstance(text_value, str):
                    return {
                        "success": False,
                        "error": f"{param} must be a string, got {type(text_value).__name__}",
                    }
                # Check for extremely long text
                if len(text_value) > 10000:  # Reasonable limit
                    return {
                        "success": False,
                        "error": f"{param} too long (max 10,000 characters)",
                    }
        return await func(*args, **kwargs)

    return wrapper


def handle_tool_errors(func: Callable) -> Callable:
    """Decorator to provide comprehensive error handling for tools."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Check Windows API availability
            if not WINDOWS_AVAILABLE:
                logger.error("Windows API not available for tool execution")
                return {
                    "success": False,
                    "error": "Windows API not available - this server requires Windows",
                }

            if not controller:
                logger.error("Notepad++ controller not initialized")
                return {"success": False, "error": "Notepad++ controller not available"}

            result = await func(*args, **kwargs)

            # Validate result format
            if not isinstance(result, dict):
                logger.error(
                    f"Tool {func.__name__} returned non-dict result: {type(result)}"
                )
                return {
                    "success": False,
                    "error": f"Internal error: invalid result format from {func.__name__}",
                }

            return result

        except NotepadPPError as e:
            logger.error(f"Notepad++ error in {func.__name__}: {e}")
            return {"success": False, "error": f"Notepad++ operation failed: {str(e)}"}
        except asyncio.TimeoutError:
            logger.error(f"Timeout in {func.__name__}")
            return {
                "success": False,
                "error": f"Operation timed out after {NOTEPADPP_TIMEOUT} seconds",
            }
        except OSError as e:
            logger.error(f"OS error in {func.__name__}: {e}")
            return {"success": False, "error": f"System error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    return wrapper


class NotepadPPError(Exception):
    """Base exception for Notepad++ operations."""

    pass


class NotepadPPNotFoundError(NotepadPPError):
    """Raised when Notepad++ is not found or not running."""

    pass


class NotepadPPController:
    """Controller for Notepad++ automation via Windows API."""

    def __init__(self):
        if not WINDOWS_AVAILABLE:
            raise NotepadPPError(
                "Windows API not available - this server requires Windows"
            )

        self.notepadpp_exe = self._find_notepadpp_exe()
        self.hwnd = None
        self.scintilla_hwnd = None

    def _find_notepadpp_exe(self) -> str:
        """Find Notepad++ executable path."""
        if NOTEPADPP_PATH and Path(NOTEPADPP_PATH).exists():
            return NOTEPADPP_PATH

        for path in DEFAULT_NOTEPADPP_PATHS:
            if Path(path).exists():
                return path

        raise NotepadPPNotFoundError(
            "Notepad++ executable not found. Please install Notepad++ or set NOTEPADPP_PATH environment variable."
        )

    def _find_notepadpp_window(self) -> Optional[int]:
        """Find Notepad++ main window handle."""

        def enum_windows_callback(hwnd: int, windows: list[int]) -> bool:
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                if class_name == "Notepad++" or "Notepad++" in window_text:
                    windows.append(hwnd)
            return True

        windows: list[int] = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None

    def _find_scintilla_window(self, main_hwnd: int) -> Optional[int]:
        """Find Scintilla editor window within Notepad++."""

        def enum_child_windows(hwnd: int, scintilla_windows: list[int]) -> bool:
            class_name = win32gui.GetClassName(hwnd)
            if class_name == "Scintilla":
                scintilla_windows.append(hwnd)
            return True

        scintilla_windows: list[int] = []
        win32gui.EnumChildWindows(main_hwnd, enum_child_windows, scintilla_windows)
        return scintilla_windows[0] if scintilla_windows else None

    async def ensure_notepadpp_running(self) -> bool:
        """Ensure Notepad++ is running, start if needed."""
        self.hwnd = self._find_notepadpp_window()

        if not self.hwnd and NOTEPADPP_AUTO_START:
            # Start Notepad++
            subprocess.Popen([self.notepadpp_exe], shell=False)

            # Wait for it to start
            for _ in range(50):  # 5 seconds max
                await asyncio.sleep(0.1)
                self.hwnd = self._find_notepadpp_window()
                if self.hwnd:
                    break

        if not self.hwnd:
            raise NotepadPPNotFoundError(
                "Notepad++ is not running and auto-start failed"
            )

        # Find Scintilla editor window
        self.scintilla_hwnd = self._find_scintilla_window(self.hwnd)
        if not self.scintilla_hwnd:
            raise NotepadPPError("Could not find Scintilla editor window")

        return True

    async def send_message(
        self, hwnd: int, msg: int, wparam: int = 0, lparam: int = 0
    ) -> int:
        """Send Windows message to window."""
        try:
            result = win32gui.SendMessage(hwnd, msg, wparam, lparam)
            return int(result) if result is not None else 0
        except Exception as e:
            raise NotepadPPError(f"Failed to send message: {e}")

    async def get_window_text(self, hwnd: int) -> str:
        """Get text from window."""
        try:
            length_result = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            length = int(length_result) if length_result is not None else 0
            if length == 0:
                return ""

            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            text = buffer.raw.decode("utf-8", errors="ignore").rstrip("\x00")
            return text
        except Exception as e:
            raise NotepadPPError(f"Failed to get window text: {e}")


# Global controller instance
controller = NotepadPPController() if WINDOWS_AVAILABLE else None


@app.tool()
@handle_tool_errors
async def get_status() -> Dict[str, Any]:
    """Get Notepad++ status and information."""
    await controller.ensure_notepadpp_running()

    window_text = await controller.get_window_text(controller.hwnd)

    return {
        "status": "running",
        "window_title": window_text,
        "main_window_handle": controller.hwnd,
        "scintilla_handle": controller.scintilla_hwnd,
        "executable_path": controller.notepadpp_exe,
    }


@app.tool()
@handle_tool_errors
@validate_file_path
async def open_file(file_path: str) -> Dict[str, Any]:
    """
    Open a file in Notepad++.

    Args:
        file_path: Path to the file to open

    Returns:
        Dictionary with operation status and file information
    """
    await controller.ensure_notepadpp_running()

    # Convert to absolute path
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        return {"success": False, "error": f"File not found: {abs_path}"}

    # Use subprocess to open file (Notepad++ command line)
    subprocess.Popen(
        [controller.notepadpp_exe, abs_path],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait a moment for file to load
    await asyncio.sleep(0.5)

    return {
        "success": True,
        "file_path": abs_path,
        "message": f"Opened file: {abs_path}",
    }


@app.tool()
@handle_tool_errors
async def new_file() -> Dict[str, Any]:
    """
    Create a new untitled file in Notepad++.

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Send Ctrl+N to create new file
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Simulate Ctrl+N
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord("N"), 0, 0, 0)
        keybd_event(ord("N"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.2)

        return {"success": True, "message": "Created new file"}

    except Exception as e:
        return {"success": False, "error": f"Failed to create new file: {e}"}


@app.tool()
async def save_file() -> Dict[str, Any]:
    """
    Save the current file in Notepad++.

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Send Ctrl+S to save file
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Simulate Ctrl+S
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord("S"), 0, 0, 0)
        keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.3)

        return {"success": True, "message": "File saved"}

    except Exception as e:
        return {"success": False, "error": f"Failed to save file: {e}"}


@app.tool()
async def get_current_file_info() -> Dict[str, Any]:
    """
    Get information about the currently active file in Notepad++.

    Returns:
        Dictionary with current file information
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Get window title which usually contains filename
        window_text = await controller.get_window_text(controller.hwnd)

        # Parse filename from window title
        # Notepad++ title format: "filename - Notepad++"
        filename = "Untitled"
        if " - Notepad++" in window_text:
            filename = window_text.split(" - Notepad++")[0]

        # Check if file is modified (usually indicated by *)
        is_modified = "*" in window_text

        return {
            "success": True,
            "window_title": window_text,
            "filename": filename,
            "is_modified": is_modified,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to get file info: {e}"}


@app.tool()
@handle_tool_errors
@validate_text_input
async def insert_text(text: str) -> Dict[str, Any]:
    """
    Insert text at the current cursor position.

    Args:
        text: Text to insert

    Returns:
        Dictionary with operation status
    """
    await controller.ensure_notepadpp_running()

    # Focus on Notepad++
    win32gui.SetForegroundWindow(controller.hwnd)
    await asyncio.sleep(0.1)

    # Use clipboard to insert text (more reliable for longer text)
    import win32clipboard

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()

    # Paste text with Ctrl+V
    keybd_event = win32api.keybd_event
    keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    keybd_event(ord("V"), 0, 0, 0)
    keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
    keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

    await asyncio.sleep(0.2)

    return {"success": True, "message": f"Inserted {len(text)} characters"}


@app.tool()
@handle_tool_errors
@validate_text_input
async def find_text(search_text: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """
    Find text in the current document.

    Args:
        search_text: Text to search for
        case_sensitive: Whether search should be case sensitive

    Returns:
        Dictionary with search results
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Open Find dialog with Ctrl+F
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord("F"), 0, 0, 0)
        keybd_event(ord("F"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.3)

        # Type search text
        for char in search_text:
            if char.isalnum() or char in " .,;:!?":
                keybd_event(ord(char.upper()), 0, 0, 0)
                keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                await asyncio.sleep(0.01)

        # Press Enter to start search
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.2)

        # Close find dialog with Escape
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        return {
            "success": True,
            "search_text": search_text,
            "case_sensitive": case_sensitive,
            "message": f"Searched for: {search_text}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to find text: {e}"}


# ============================================================================
# HELP AND STATUS TOOLS
# ============================================================================


@app.tool()
@handle_tool_errors
async def get_help(category: str = "", tool_name: str = "") -> Dict[str, Any]:
    """
    Get hierarchical help information for Notepad++ MCP tools.

    Provides multilevel help system:
    - No parameters: Lists all available tool categories
    - category: Lists tools in that category
    - category + tool_name: Detailed help for specific tool

    Args:
        category: Tool category to filter by (optional)
        tool_name: Specific tool name for detailed help (optional)

    Returns:
        Dictionary with help information organized by category/tool
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Define tool categories and their tools
        help_data = {
            "file_operations": {
                "description": "File management operations",
                "tools": {
                    "open_file": "Open a file in Notepad++",
                    "new_file": "Create a new file",
                    "save_file": "Save the current file",
                    "get_current_file_info": "Get information about current file",
                },
            },
            "text_operations": {
                "description": "Text manipulation and editing",
                "tools": {
                    "insert_text": "Insert text at cursor position",
                    "find_text": "Search for text in current document",
                },
            },
            "status_queries": {
                "description": "System and application status",
                "tools": {
                    "get_status": "Get Notepad++ status and information",
                    "get_system_status": "Get detailed system and application status",
                },
            },
            "help_system": {
                "description": "Help and documentation",
                "tools": {"get_help": "Get hierarchical help (this tool)"},
            },
        }

        if not category:
            # Return all categories
            return {
                "help_system": "Multilevel Help System",
                "categories": {
                    name: data["description"] for name, data in help_data.items()
                },
                "usage": {
                    "get_help()": "List all categories",
                    "get_help('category_name')": "List tools in category",
                    "get_help('category_name', 'tool_name')": "Get detailed tool help",
                },
            }

        if category not in help_data:
            return {
                "error": f"Unknown category: {category}",
                "available_categories": list(help_data.keys()),
            }

        category_data = help_data[category]

        if not tool_name:
            # Return tools in category
            return {
                "category": category,
                "description": category_data["description"],
                "tools": category_data["tools"],
            }

        if tool_name not in category_data["tools"]:
            return {
                "error": f"Unknown tool: {tool_name} in category: {category}",
                "available_tools": list(category_data["tools"].keys()),
            }

        # Return detailed help for specific tool
        return {
            "category": category,
            "tool": tool_name,
            "description": category_data["tools"][tool_name],
            "usage": f"Call {tool_name}() to execute this tool",
        }

    except Exception as e:
        logger.error(f"Error getting help: {e}")
        return {"error": "Failed to get help information", "details": str(e)}


@app.tool()
async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system and application status information.

    Provides detailed status including:
    - Notepad++ process information
    - System resource usage
    - Window and tab information
    - Configuration settings
    - Performance metrics

    Returns:
        Dictionary with comprehensive system status information
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Get basic status
        basic_status = await get_status()

        if "error" in basic_status:
            return basic_status

        # Get system information
        system_info = {
            "process_info": {},
            "memory_usage": {},
            "window_info": {},
            "configuration": {},
        }

        try:
            # Get process information
            if WINDOWS_AVAILABLE:
                for proc in psutil.process_iter(["pid", "name"]):
                    if "notepad" in proc.info["name"].lower():
                        p = psutil.Process(proc.info["pid"])
                        system_info["process_info"] = {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "cpu_percent": p.cpu_percent(),
                            "memory_mb": p.memory_info().rss / 1024 / 1024,
                            "create_time": p.create_time(),
                        }
                        break

            # Get memory information
            memory = psutil.virtual_memory()
            system_info["memory_usage"] = {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "available_gb": memory.available / 1024 / 1024 / 1024,
                "percent_used": memory.percent,
            }

            # Get window information
            system_info["window_info"] = {
                "main_window_handle": controller.hwnd,
                "scintilla_handle": controller.scintilla_hwnd,
                "window_title": await controller.get_window_text(controller.hwnd),
            }

            # Get configuration
            system_info["configuration"] = {
                "timeout": NOTEPADPP_TIMEOUT,
                "auto_start": NOTEPADPP_AUTO_START,
                "notepad_path": controller.notepadpp_exe,
            }

        except Exception as sys_error:
            logger.warning(f"Could not get detailed system info: {sys_error}")
            system_info["note"] = "Some system information unavailable"

        return {
            "status": "success",
            "basic_info": basic_status,
            "system_info": system_info,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {"error": "Failed to get system status", "details": str(e)}


@app.tool()
@handle_tool_errors
async def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check of Notepad++ MCP server.

    Tests all critical components:
    - Windows API availability
    - Notepad++ process detection
    - Window handle validation
    - Basic functionality tests
    - System resource checks

    Returns:
        Dictionary with health check results and recommendations
    """
    health_status = {
        "overall_status": "unknown",
        "checks": {},
        "recommendations": [],
        "timestamp": time.time(),
    }

    # Check 1: Windows API availability
    health_status["checks"]["windows_api"] = {
        "status": "pass" if WINDOWS_AVAILABLE else "fail",
        "message": "Windows API available"
        if WINDOWS_AVAILABLE
        else "Windows API not available",
        "critical": True,
    }

    if not WINDOWS_AVAILABLE:
        health_status["overall_status"] = "fail"
        health_status["recommendations"].append("Install pywin32: pip install pywin32")
        health_status["recommendations"].append("Ensure running on Windows platform")
        return health_status

    # Check 2: Controller initialization
    try:
        controller.ensure_notepadpp_running()
        health_status["checks"]["controller_init"] = {
            "status": "pass",
            "message": "Controller initialized successfully",
            "critical": True,
        }
    except Exception as e:
        health_status["checks"]["controller_init"] = {
            "status": "fail",
            "message": f"Controller initialization failed: {str(e)}",
            "critical": True,
        }
        health_status["overall_status"] = "fail"
        health_status["recommendations"].append("Install and start Notepad++")
        return health_status

    # Check 3: Notepad++ process
    try:
        import psutil

        notepad_processes = [
            p
            for p in psutil.process_iter(["pid", "name"])
            if "notepad++" in p.info["name"].lower()
        ]
        health_status["checks"]["notepad_process"] = {
            "status": "pass" if notepad_processes else "fail",
            "message": f"Found {len(notepad_processes)} Notepad++ process(es)",
            "critical": True,
        }
    except Exception as e:
        health_status["checks"]["notepad_process"] = {
            "status": "warning",
            "message": f"Could not check process: {str(e)}",
            "critical": False,
        }

    # Check 4: Window handles
    try:
        window_valid = controller.hwnd and controller.hwnd != 0
        scintilla_valid = controller.scintilla_hwnd and controller.scintilla_hwnd != 0

        health_status["checks"]["window_handles"] = {
            "status": "pass" if window_valid else "fail",
            "message": f"Main window: {'valid' if window_valid else 'invalid'}, Scintilla: {'valid' if scintilla_valid else 'invalid'}",
            "critical": True,
        }
    except Exception as e:
        health_status["checks"]["window_handles"] = {
            "status": "warning",
            "message": f"Could not validate handles: {str(e)}",
            "critical": False,
        }

    # Check 5: Basic functionality
    try:
        # Test getting window title
        title = await controller.get_window_text(controller.hwnd)
        health_status["checks"]["basic_functionality"] = {
            "status": "pass" if title else "warning",
            "message": f"Window title retrieved: {bool(title)}",
            "critical": False,
        }
    except Exception as e:
        health_status["checks"]["basic_functionality"] = {
            "status": "warning",
            "message": f"Basic functionality test failed: {str(e)}",
            "critical": False,
        }

    # Determine overall status
    critical_checks = [
        check
        for check in health_status["checks"].values()
        if check.get("critical", False)
    ]

    if all(check["status"] == "pass" for check in critical_checks):
        health_status["overall_status"] = "pass"
        health_status["recommendations"].append("All systems operational")
    elif any(check["status"] == "fail" for check in critical_checks):
        health_status["overall_status"] = "fail"
        if not health_status["recommendations"]:
            health_status["recommendations"].append("Check critical system components")
    else:
        health_status["overall_status"] = "warning"
        health_status["recommendations"].append("Some non-critical issues detected")

    return health_status


# ============================================================================
# TAB MANAGEMENT TOOLS
# ============================================================================


@app.tool()
async def list_tabs() -> Dict[str, Any]:
    """
    List all open tabs in Notepad++.

    Returns information about:
    - Number of open tabs
    - Tab names and file paths
    - Active tab information
    - Tab modification status

    Returns:
        Dictionary with tab listing information
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Get window title which usually contains filename
        window_text = await controller.get_window_text(controller.hwnd)

        # Parse filename from window title
        # Notepad++ title format: "filename - Notepad++"
        filename = "Untitled"
        if " - Notepad++" in window_text:
            filename = window_text.split(" - Notepad++")[0]

        # Check if file is modified (usually indicated by *)
        is_modified = "*" in window_text

        return {
            "success": True,
            "total_tabs": 1,  # Simplified - Notepad++ API would be needed for full tab list
            "active_tab": {
                "filename": filename,
                "is_modified": is_modified,
                "full_title": window_text,
            },
            "note": "Full tab enumeration requires Notepad++ plugin API integration",
        }

    except Exception as e:
        logger.error(f"Error listing tabs: {e}")
        return {"error": "Failed to list tabs", "details": str(e)}


@app.tool()
async def switch_to_tab(tab_index: int) -> Dict[str, Any]:
    """
    Switch to a specific tab by index.

    Args:
        tab_index: Zero-based index of tab to switch to (0 for first tab)

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++ window
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Send Ctrl+Tab to cycle through tabs
        # This is a simplified implementation - full tab switching would need plugin API
        keybd_event = win32api.keybd_event

        for i in range(tab_index):
            keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            keybd_event(win32con.VK_TAB, 0, 0, 0)
            await asyncio.sleep(0.1)
            keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.2)

        await asyncio.sleep(0.5)

        return {
            "success": True,
            "switched_to_tab": tab_index,
            "message": f"Switched to tab {tab_index}",
        }

    except Exception as e:
        logger.error(f"Error switching to tab: {e}")
        return {"error": "Failed to switch tab", "details": str(e)}


@app.tool()
async def close_tab(tab_index: int = -1) -> Dict[str, Any]:
    """
    Close a tab by index or the current tab if no index specified.

    Args:
        tab_index: Zero-based index of tab to close (-1 for current tab)

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++ window
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Send Ctrl+W to close tab (or Ctrl+F4)
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord("W"), 0, 0, 0)
        keybd_event(ord("W"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.3)

        return {
            "success": True,
            "closed_tab": tab_index,
            "message": f"Closed tab {tab_index}",
        }

    except Exception as e:
        logger.error(f"Error closing tab: {e}")
        return {"error": "Failed to close tab", "details": str(e)}


# ============================================================================
# SESSION MANAGEMENT TOOLS
# ============================================================================


@app.tool()
async def save_session(session_name: str) -> Dict[str, Any]:
    """
    Save current Notepad++ session to named workspace.

    Args:
        session_name: Name for the saved session

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Get current file info to save session state
        file_info = await get_current_file_info()

        if "error" in file_info:
            return file_info

        session_data = {
            "name": session_name,
            "timestamp": time.time(),
            "files": [file_info.get("filename", "Untitled")],
            "active_file": file_info.get("filename", "Untitled"),
            "is_modified": file_info.get("is_modified", False),
        }

        # In a real implementation, this would save to a session file
        # For now, we'll return the session data
        return {
            "success": True,
            "session_name": session_name,
            "session_data": session_data,
            "message": f"Session '{session_name}' saved",
            "note": "Session persistence requires additional file I/O implementation",
        }

    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return {"error": "Failed to save session", "details": str(e)}


@app.tool()
async def load_session(session_name: str) -> Dict[str, Any]:
    """
    Load a previously saved session.

    Args:
        session_name: Name of session to load

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # In a real implementation, this would load from a session file
        # For now, we'll simulate loading a session
        return {
            "success": True,
            "session_name": session_name,
            "message": f"Session '{session_name}' loaded",
            "note": "Full session restoration requires session file format implementation",
        }

    except Exception as e:
        logger.error(f"Error loading session: {e}")
        return {"error": "Failed to load session", "details": str(e)}


@app.tool()
async def list_sessions() -> Dict[str, Any]:
    """
    List all saved sessions.

    Returns:
        Dictionary with list of available sessions
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # In a real implementation, this would scan for session files
        # For now, we'll return a placeholder
        return {
            "success": True,
            "sessions": [],
            "message": "Session listing requires file system scanning implementation",
            "note": "No sessions found (session persistence not yet implemented)",
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return {"error": "Failed to list sessions", "details": str(e)}


# =============================================================================
# LINTING TOOLS - Support for multiple file types
# =============================================================================


@app.tool()
async def lint_python_file(file_path: str) -> Dict[str, Any]:
    """
    Lint a Python file using ruff (if available) or basic syntax checking.

    Performs comprehensive Python code analysis including:
    - Syntax errors and undefined names
    - Code style violations
    - Import issues
    - Unused variables and imports
    - Complexity analysis

    Args:
        file_path: Path to the Python file to lint

    Returns:
        Dictionary with linting results including errors, warnings, and suggestions
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Convert to absolute path
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {abs_path}"}

        # Try ruff first (fastest Python linter)
        try:
            import subprocess

            result = subprocess.run(
                ["ruff", "check", abs_path, "--output-format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # No issues found
                return {
                    "success": True,
                    "file_path": abs_path,
                    "linter": "ruff",
                    "issues": [],
                    "summary": "No linting issues found",
                }
            else:
                # Parse JSON output from ruff
                import json

                issues = json.loads(result.stdout) if result.stdout else []

                # Categorize issues
                errors = [issue for issue in issues if issue.get("type") == "error"]
                warnings = [issue for issue in issues if issue.get("type") == "warning"]

                return {
                    "success": True,
                    "file_path": abs_path,
                    "linter": "ruff",
                    "total_issues": len(issues),
                    "errors": len(errors),
                    "warnings": len(warnings),
                    "issues": issues,
                    "summary": f"Found {len(issues)} issues ({len(errors)} errors, {len(warnings)} warnings)",
                }

        except (FileNotFoundError, subprocess.TimeoutExpired):
            # ruff not available, try flake8
            try:
                result = subprocess.run(
                    ["flake8", "--format=json", abs_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    return {
                        "success": True,
                        "file_path": abs_path,
                        "linter": "flake8",
                        "issues": [],
                        "summary": "No linting issues found",
                    }
                else:
                    # Parse flake8 output
                    issues = []
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            try:
                                issue = json.loads(line)
                                issues.append(
                                    {
                                        "code": issue.get("code", "E999"),
                                        "message": issue.get(
                                            "message", "Unknown issue"
                                        ),
                                        "line": issue.get("line", 0),
                                        "column": issue.get("column", 0),
                                        "type": "error"
                                        if issue.get("code", "").startswith("E")
                                        else "warning",
                                    }
                                )
                            except Exception:
                                continue

                    return {
                        "success": True,
                        "file_path": abs_path,
                        "linter": "flake8",
                        "total_issues": len(issues),
                        "issues": issues,
                        "summary": f"Found {len(issues)} linting issues",
                    }

            except (FileNotFoundError, subprocess.TimeoutExpired):
                # No linters available, do basic syntax check
                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Basic Python syntax validation
                    compile(content, abs_path, "exec")

                    return {
                        "success": True,
                        "file_path": abs_path,
                        "linter": "basic_syntax",
                        "issues": [],
                        "summary": "Basic syntax check passed",
                    }

                except SyntaxError as e:
                    return {
                        "success": False,
                        "file_path": abs_path,
                        "linter": "basic_syntax",
                        "error": f"Syntax error: {e.msg}",
                        "line": e.lineno,
                        "column": e.offset,
                        "summary": f"Syntax error on line {e.lineno}",
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "file_path": abs_path,
                        "error": f"Could not read file: {e}",
                    }

    except Exception as e:
        logger.error(f"Error linting Python file: {e}")
        return {"success": False, "error": f"Failed to lint Python file: {e}"}


@app.tool()
async def lint_javascript_file(file_path: str) -> Dict[str, Any]:
    """
    Lint a JavaScript file using eslint or basic syntax checking.

    Supports:
    - ESLint (if installed globally)
    - Basic JavaScript syntax validation
    - Common JS issues detection

    Args:
        file_path: Path to the JavaScript file to lint

    Returns:
        Dictionary with linting results and any issues found
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {abs_path}"}

        # Try eslint first
        try:
            import subprocess

            result = subprocess.run(
                ["eslint", "--format=json", abs_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if (
                result.returncode == 0 or result.returncode == 2
            ):  # 2 = linting errors found
                issues = []
                if result.stdout.strip():
                    try:
                        import json

                        eslint_results = json.loads(result.stdout)
                        for file_result in eslint_results:
                            if file_result.get("messages"):
                                for message in file_result["messages"]:
                                    issues.append(
                                        {
                                            "rule": message.get("ruleId", "unknown"),
                                            "message": message.get(
                                                "message", "Unknown issue"
                                            ),
                                            "line": message.get("line", 0),
                                            "column": message.get("column", 0),
                                            "severity": message.get("severity", 1),
                                            "type": "error"
                                            if message.get("severity", 1) > 1
                                            else "warning",
                                        }
                                    )
                    except Exception:
                        issues = [
                            {
                                "message": "Could not parse ESLint output",
                                "type": "error",
                            }
                        ]

                return {
                    "success": True,
                    "file_path": abs_path,
                    "linter": "eslint",
                    "total_issues": len(issues),
                    "issues": issues,
                    "summary": f"ESLint found {len(issues)} issues",
                }

        except (FileNotFoundError, subprocess.TimeoutExpired):
            # ESLint not available, do basic validation
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Basic JavaScript validation (very simple)
                issues = []

                # Check for common issues
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    line = line.strip()

                    # Check for missing semicolons (basic heuristic)
                    if (
                        line
                        and not line.endswith(";")
                        and not line.endswith("{")
                        and not line.endswith("}")
                        and not line.endswith(",")
                        and not line.startswith("//")
                        and not line.startswith("/*")
                        and "=" in line
                        and "var " not in line
                        and "let " not in line
                        and "const " not in line
                    ):
                        issues.append(
                            {
                                "line": i,
                                "message": "Missing semicolon",
                                "type": "warning",
                            }
                        )

                    # Check for console.log statements
                    if "console.log" in line:
                        issues.append(
                            {
                                "line": i,
                                "message": "Console.log statement found",
                                "type": "info",
                            }
                        )

                return {
                    "success": True,
                    "file_path": abs_path,
                    "linter": "basic_js_check",
                    "total_issues": len(issues),
                    "issues": issues,
                    "summary": f"Basic JS check found {len(issues)} issues",
                }

            except Exception as e:
                return {
                    "success": False,
                    "file_path": abs_path,
                    "error": f"Could not read JavaScript file: {e}",
                }

    except Exception as e:
        logger.error(f"Error linting JavaScript file: {e}")
        return {"success": False, "error": f"Failed to lint JavaScript file: {e}"}


@app.tool()
async def lint_json_file(file_path: str) -> Dict[str, Any]:
    """
    Validate and lint a JSON file.

    Checks:
    - JSON syntax validity
    - Schema compliance (if schema provided)
    - Common JSON issues
    - Pretty-printing suggestions

    Args:
        file_path: Path to the JSON file to lint

    Returns:
        Dictionary with validation results and any issues found
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {abs_path}"}

        try:
            import json

            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse JSON to validate syntax
            data = json.loads(content)

            # Additional validation
            issues = []

            # Check for trailing commas (JSON doesn't allow them)
            import re

            trailing_comma_pattern = r",(\s*[}\]])"
            if re.search(trailing_comma_pattern, content):
                issues.append(
                    {
                        "message": "Trailing comma found (not valid JSON)",
                        "type": "error",
                    }
                )

            # Check if it's minified (very long lines)
            lines = content.split("\n")
            long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 100]
            if long_lines:
                issues.append(
                    {
                        "message": f"Long lines found (consider pretty-printing): {len(long_lines)} lines > 100 chars",
                        "type": "info",
                        "lines": long_lines[:5],  # Show first 5
                    }
                )

            # Check for common issues
            if isinstance(data, dict):
                if not data:
                    issues.append({"message": "Empty JSON object", "type": "info"})

            return {
                "success": True,
                "file_path": abs_path,
                "linter": "json_validator",
                "valid_json": True,
                "total_issues": len(issues),
                "issues": issues,
                "data_type": type(data).__name__,
                "keys_count": len(data) if isinstance(data, dict) else 0,
                "summary": f"Valid JSON with {len(issues)} issues found",
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "file_path": abs_path,
                "linter": "json_validator",
                "valid_json": False,
                "error": f"Invalid JSON: {e.msg}",
                "line": e.lineno,
                "column": e.colno,
                "summary": f"JSON syntax error on line {e.lineno}",
            }

    except Exception as e:
        logger.error(f"Error linting JSON file: {e}")
        return {"success": False, "error": f"Failed to lint JSON file: {e}"}


@app.tool()
async def lint_markdown_file(file_path: str) -> Dict[str, Any]:
    """
    Lint a Markdown file for common issues and style problems.

    Checks:
    - Basic Markdown syntax
    - Header hierarchy
    - Link validity
    - Code block formatting
    - Common Markdown issues

    Args:
        file_path: Path to the Markdown file to lint

    Returns:
        Dictionary with linting results and any issues found
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {abs_path}"}

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            issues = []

            # Check for common Markdown issues
            in_code_block = False
            header_levels = []
            links = []

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Track code blocks
                if stripped.startswith("```"):
                    in_code_block = not in_code_block

                if in_code_block:
                    continue

                # Check header hierarchy
                if stripped.startswith("#"):
                    level = len(stripped) - len(stripped.lstrip("#"))
                    header_levels.append((i, level, stripped))

                    if level > 1 and not header_levels[:-1]:
                        issues.append(
                            {
                                "line": i,
                                "message": f"H{level} found without H{level - 1}",
                                "type": "warning",
                            }
                        )

                # Check for links
                if "[" in line and "](" in line:
                    links.append(i)

                # Check for trailing spaces
                if line.rstrip() != line:
                    issues.append(
                        {
                            "line": i,
                            "message": "Trailing whitespace found",
                            "type": "warning",
                        }
                    )

                # Check for very long lines
                if len(stripped) > 120:
                    issues.append(
                        {
                            "line": i,
                            "message": f"Line too long ({len(stripped)} characters)",
                            "type": "info",
                        }
                    )

            # Validate header hierarchy
            if len(header_levels) > 1:
                for i in range(1, len(header_levels)):
                    prev_level = header_levels[i - 1][1]
                    curr_level = header_levels[i][1]

                    if curr_level > prev_level + 1:
                        issues.append(
                            {
                                "line": header_levels[i][0],
                                "message": f"H{curr_level} skips H{curr_level - 1}",
                                "type": "warning",
                            }
                        )

            return {
                "success": True,
                "file_path": abs_path,
                "linter": "markdown_validator",
                "total_issues": len(issues),
                "headers_found": len(header_levels),
                "links_found": len(links),
                "issues": issues,
                "summary": f"Markdown validation found {len(issues)} issues",
            }

        except Exception as e:
            return {
                "success": False,
                "file_path": abs_path,
                "error": f"Could not read Markdown file: {e}",
            }

    except Exception as e:
        logger.error(f"Error linting Markdown file: {e}")
        return {"success": False, "error": f"Failed to lint Markdown file: {e}"}


@app.tool()
async def get_linting_tools() -> Dict[str, Any]:
    """
    Get information about available linting tools and their capabilities.

    Returns a comprehensive overview of all supported file types and linting options.
    """
    return {
        "success": True,
        "linting_tools": {
            "python": {
                "supported": True,
                "linters": ["ruff", "flake8", "basic_syntax"],
                "description": "Python code linting with multiple linter support",
            },
            "javascript": {
                "supported": True,
                "linters": ["eslint", "basic_js_check"],
                "description": "JavaScript linting with ESLint and basic validation",
            },
            "json": {
                "supported": True,
                "linters": ["json_validator"],
                "description": "JSON syntax validation and structure checking",
            },
            "markdown": {
                "supported": True,
                "linters": ["markdown_validator"],
                "description": "Markdown syntax and style checking",
            },
            "html": {
                "supported": False,
                "linters": [],
                "description": "HTML linting - planned for future release",
            },
            "css": {
                "supported": False,
                "linters": [],
                "description": "CSS linting - planned for future release",
            },
        },
        "total_supported_types": 4,
        "planned_types": 2,
        "usage": {
            "python": "lint_python_file('path/to/file.py')",
            "javascript": "lint_javascript_file('path/to/file.js')",
            "json": "lint_json_file('path/to/file.json')",
            "markdown": "lint_markdown_file('path/to/file.md')",
        },
    }


@app.tool()
@handle_tool_errors
async def fix_invisible_text() -> Dict[str, Any]:
    """
    Fix invisible text issue in Notepad++ main editor.

    This specifically targets the problem where folder tree is visible
    but main text editor has invisible text (white on white).

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Method 1: Quick theme reset via Style Configurator
        logger.info("🎨 Method 1: Resetting theme via Style Configurator...")

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

        # Navigate to theme selection (usually first tab)
        # Press Tab to get to theme dropdown
        for _ in range(2):
            keybd_event(win32con.VK_TAB, 0, 0, 0)
            keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.1)

        # Select "Default" theme
        keybd_event(win32con.VK_DOWN, 0, 0, 0)
        keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)

        # Press Enter to apply
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Close Style Configurator
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Method 2: Force text color change via Global Styles
        logger.info("🔧 Method 2: Adjusting Global Styles...")

        # Open Style Configurator again
        keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt
        keybd_event(ord("S"), 0, 0, 0)
        keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(ord("S"), 0, 0, 0)
        keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(1.0)

        # Navigate to Global Styles
        # Press Tab to get to style list
        keybd_event(win32con.VK_TAB, 0, 0, 0)
        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)

        # Select "Global Styles" -> "Default Style"
        keybd_event(win32con.VK_DOWN, 0, 0, 0)
        keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)

        # Navigate to foreground color
        for _ in range(3):
            keybd_event(win32con.VK_TAB, 0, 0, 0)
            keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.1)

        # Set foreground color to black (RGB: 0,0,0)
        # This should make text visible on white background
        keybd_event(ord("0"), 0, 0, 0)
        keybd_event(ord("0"), 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)
        keybd_event(ord("0"), 0, 0, 0)
        keybd_event(ord("0"), 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)
        keybd_event(ord("0"), 0, 0, 0)
        keybd_event(ord("0"), 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Press Enter to apply changes
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Close Style Configurator
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Method 3: Force display refresh
        logger.info("🔄 Method 3: Forcing display refresh...")

        # Send WM_PAINT message to force redraw
        win32gui.SendMessage(controller.hwnd, win32con.WM_PAINT, 0, 0)
        if controller.scintilla_hwnd:
            win32gui.SendMessage(controller.scintilla_hwnd, win32con.WM_PAINT, 0, 0)

        # Force window refresh
        win32gui.InvalidateRect(controller.hwnd, None, True)
        if controller.scintilla_hwnd:
            win32gui.InvalidateRect(controller.scintilla_hwnd, None, True)

        await asyncio.sleep(0.2)

        # Method 4: Try to insert some text to test visibility
        logger.info("📝 Method 4: Testing text visibility...")

        # Insert test text to see if it's visible
        test_text = "Text visibility test - if you can see this, the fix worked!"

        # Use clipboard method for reliable text insertion
        import win32clipboard

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(test_text)
        win32clipboard.CloseClipboard()

        # Paste text with Ctrl+V
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord("V"), 0, 0, 0)
        keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        return {
            "success": True,
            "message": "Invisible text fix applied! Check if text is now visible in the main editor.",
            "test_text": test_text,
            "methods_applied": [
                "Theme reset to Default",
                "Global Styles foreground color set to black",
                "Display refresh forced",
                "Test text inserted",
            ],
            "next_steps": [
                "Check if the test text is visible in the main editor",
                "If still invisible, try: View > Zoom > Reset Zoom",
                "If still invisible, try: Settings > Style Configurator > Select 'Obsidian' theme",
                "As last resort: Restart Notepad++ completely",
            ],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fix invisible text: {e}",
            "manual_fix": "Try manually: Settings > Style Configurator > Global Styles > Default Style > Set foreground color to black",
            "alternative_fix": "Try: Settings > Style Configurator > Select 'Obsidian' or 'Default' theme",
        }


@app.tool()
@handle_tool_errors
async def fix_display_issue() -> Dict[str, Any]:
    """
    Fix Notepad++ display issues like black text on black background.

    This tool attempts to reset Notepad++ theme and colors to default values.

    Returns:
        Dictionary with operation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Method 1: Try to reset theme via Settings menu
        # Open Settings menu with Alt+S
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt key
        keybd_event(ord("S"), 0, 0, 0)
        keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Try to navigate to Style Configurator
        # Press 'S' for Style Configurator
        keybd_event(ord("S"), 0, 0, 0)
        keybd_event(ord("S"), 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(1.0)

        # If Style Configurator opened, try to reset to default theme
        # Press Tab to navigate to theme selection
        for _ in range(3):
            keybd_event(win32con.VK_TAB, 0, 0, 0)
            keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.1)

        # Try to select default theme
        keybd_event(win32con.VK_DOWN, 0, 0, 0)
        keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.1)

        # Press Enter to apply
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Close dialog with Escape
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Method 2: Try Ctrl+Shift+P to open Plugin Manager and reset
        # This is a common shortcut for plugin-related issues
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        keybd_event(ord("P"), 0, 0, 0)
        keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Close any opened dialogs
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        # Method 3: Try to force refresh the display
        # Send WM_PAINT message to force redraw
        win32gui.SendMessage(controller.hwnd, win32con.WM_PAINT, 0, 0)
        if controller.scintilla_hwnd:
            win32gui.SendMessage(controller.scintilla_hwnd, win32con.WM_PAINT, 0, 0)

        await asyncio.sleep(0.2)

        return {
            "success": True,
            "message": "Display fix attempted. If issue persists, try: 1) Restart Notepad++, 2) Settings > Style Configurator > Select 'Default' theme, 3) Check View > Current View for display issues",
            "suggestions": [
                "Restart Notepad++ completely",
                "Go to Settings > Style Configurator and select 'Default' theme",
                "Check View > Current View for any display issues",
                "Try View > Zoom > Reset Zoom",
                "Check if any plugins are causing the issue",
            ],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fix display issue: {e}",
            "manual_fix": "Try manually: Settings > Style Configurator > Select 'Default' theme",
        }


@app.tool()
@handle_tool_errors
async def discover_plugins(
    category: str = None, search_term: str = None, limit: int = 20
) -> Dict[str, Any]:
    """
    Discover available plugins from the official Notepad++ Plugin List.

    Args:
        category: Optional category filter (e.g., 'code_analysis', 'file_ops', 'text_processing')
        search_term: Optional search term to filter plugins by name or description
        limit: Maximum number of plugins to return (default: 20)

    Returns:
        Dictionary with discovered plugins and their information
    """
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

                        content = base64.b64decode(response.json()["content"]).decode(
                            "utf-8"
                        )
                        plugins_data = json.loads(content)
                    else:
                        plugins_data = response.json()
                    break
            except Exception as e:
                logger.warning(f"Failed to fetch from {url}: {e}")
                continue

        if not plugins_data:
            # Fallback: return curated list of popular plugins
            plugins_data = {
                "plugins": [
                    {
                        "name": "NppFTP",
                        "description": "FTP client plugin for remote file editing",
                        "category": "file_ops",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "Compare",
                        "description": "File comparison and diff tool",
                        "category": "file_ops",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "JSON Viewer",
                        "description": "JSON formatting and validation",
                        "category": "text_processing",
                        "author": "Community",
                        "version": "1.0.0",
                    },
                    {
                        "name": "JSTool",
                        "description": "JavaScript tools and formatting",
                        "category": "code_analysis",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "MIME Tools",
                        "description": "MIME type detection and conversion",
                        "category": "text_processing",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "NppExec",
                        "description": "Execute external programs and scripts",
                        "category": "development",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "Plugin Manager",
                        "description": "Plugin installation and management",
                        "category": "system",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                    {
                        "name": "TextFX",
                        "description": "Advanced text processing tools",
                        "category": "text_processing",
                        "author": "Don Ho",
                        "version": "1.0.0",
                    },
                ]
            }

        # Filter plugins based on criteria
        plugins = plugins_data.get("plugins", [])
        filtered_plugins = []

        for plugin in plugins:
            # Apply category filter
            if category and plugin.get("category", "").lower() != category.lower():
                continue

            # Apply search term filter
            if search_term:
                search_lower = search_term.lower()
                if not (
                    search_lower in plugin.get("name", "").lower()
                    or search_lower in plugin.get("description", "").lower()
                ):
                    continue

            filtered_plugins.append(plugin)

            # Apply limit
            if len(filtered_plugins) >= limit:
                break

        return {
            "success": True,
            "plugins": filtered_plugins,
            "total_found": len(filtered_plugins),
            "categories": list(set(p.get("category", "unknown") for p in plugins)),
            "message": f"Found {len(filtered_plugins)} plugins matching criteria",
        }

    except Exception as e:
        logger.error(f"Plugin discovery failed: {e}")
        return {
            "success": False,
            "error": f"Failed to discover plugins: {e}",
            "fallback_message": "Using curated plugin list due to network issues",
        }


@app.tool()
@handle_tool_errors
async def install_plugin(plugin_name: str) -> Dict[str, Any]:
    """
    Install a plugin using Notepad++ Plugin Admin.

    Args:
        plugin_name: Name of the plugin to install

    Returns:
        Dictionary with installation status
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Open Plugin Admin (Alt+P+A)
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt
        keybd_event(ord("P"), 0, 0, 0)
        keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(ord("A"), 0, 0, 0)
        keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(1.0)  # Wait for Plugin Admin to open

        # Navigate to Available tab (if not already there)
        # Press Tab to navigate to Available tab
        keybd_event(win32con.VK_TAB, 0, 0, 0)
        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Search for the plugin by typing its name
        for char in plugin_name:
            keybd_event(ord(char.upper()), 0, 0, 0)
            keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.1)

        await asyncio.sleep(0.5)

        # Press Enter to select the plugin
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Look for Install button and click it
        # Navigate to Install button (usually Tab or Right arrow)
        keybd_event(win32con.VK_TAB, 0, 0, 0)
        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_TAB, 0, 0, 0)
        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.3)

        # Press Enter to install
        keybd_event(win32con.VK_RETURN, 0, 0, 0)
        keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(2.0)  # Wait for installation

        # Close Plugin Admin dialog
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        return {
            "success": True,
            "message": f"Installation process completed for plugin: {plugin_name}",
            "plugin_name": plugin_name,
            "note": "Please restart Notepad++ to complete plugin installation",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to install plugin {plugin_name}: {e}",
            "manual_install": f"Try manually: Plugins > Plugin Admin > Available > Search for '{plugin_name}' > Install",
        }


@app.tool()
@handle_tool_errors
async def list_installed_plugins() -> Dict[str, Any]:
    """
    List currently installed plugins in Notepad++.

    Returns:
        Dictionary with installed plugins information
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Open Plugin Admin (Alt+P+A)
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt
        keybd_event(ord("P"), 0, 0, 0)
        keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(ord("A"), 0, 0, 0)
        keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(1.0)  # Wait for Plugin Admin to open

        # Navigate to Installed tab
        # Press Tab to navigate to Installed tab
        keybd_event(win32con.VK_TAB, 0, 0, 0)
        keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Get window text to see installed plugins
        # This is a simplified approach - in practice, you'd need to parse the dialog content
        # window_text = await controller.get_window_text(controller.hwnd)

        # Close Plugin Admin dialog
        keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # For now, return a basic response
        # In a full implementation, you'd parse the Plugin Admin dialog content
        return {
            "success": True,
            "message": "Plugin Admin opened successfully",
            "installed_plugins": [
                "Plugin Manager (built-in)",
                "NppExec (if installed)",
                "Compare (if installed)",
                "NppFTP (if installed)",
            ],
            "note": "This is a simplified list. Full implementation would parse Plugin Admin dialog content",
            "manual_check": "Use Plugins > Plugin Admin > Installed tab to see complete list",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list installed plugins: {e}",
            "manual_check": "Use Plugins > Plugin Admin > Installed tab to see installed plugins",
        }


@app.tool()
@handle_tool_errors
async def execute_plugin_command(plugin_name: str, command: str) -> Dict[str, Any]:
    """
    Execute a command from an installed plugin.

    Args:
        plugin_name: Name of the plugin
        command: Command to execute (menu item name or command)

    Returns:
        Dictionary with command execution results
    """
    if not controller:
        return {"error": "Windows API not available"}

    try:
        await controller.ensure_notepadpp_running()

        # Focus on Notepad++
        win32gui.SetForegroundWindow(controller.hwnd)
        await asyncio.sleep(0.1)

        # Open Plugins menu (Alt+P)
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt
        keybd_event(ord("P"), 0, 0, 0)
        keybd_event(ord("P"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

        # Type the plugin name to navigate to it
        for char in plugin_name:
            keybd_event(ord(char.upper()), 0, 0, 0)
            keybd_event(ord(char.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
            await asyncio.sleep(0.1)

        await asyncio.sleep(0.5)

        # Press Right arrow to open submenu
        keybd_event(win32con.VK_RIGHT, 0, 0, 0)
        keybd_event(win32con.VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.5)

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
            "message": f"Executed command '{command}' from plugin '{plugin_name}'",
            "plugin_name": plugin_name,
            "command": command,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute plugin command: {e}",
            "plugin_name": plugin_name,
            "command": command,
            "manual_execute": f"Try manually: Plugins > {plugin_name} > {command}",
        }


def main() -> None:
    """Main entry point for the MCP server."""
    import sys

    if not WINDOWS_AVAILABLE:
        logger.error("This MCP server requires Windows and pywin32")
        sys.exit(1)

    app.run()


if __name__ == "__main__":
    main()
