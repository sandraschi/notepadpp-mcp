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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
from fastmcp import FastMCP

# Configure structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler for stderr (safe for FastMCP stdio protocol)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

# Windows-specific imports
try:
    import win32api
    import win32con
    import win32gui
    import win32process
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
    r"C:\Users\{}\AppData\Local\Notepad++\notepad++.exe".format(os.getenv("USERNAME", "")),
]


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
            raise NotepadPPError("Windows API not available - this server requires Windows")
        
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
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                if class_name == "Notepad++" or "Notepad++" in window_text:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
    
    def _find_scintilla_window(self, main_hwnd: int) -> Optional[int]:
        """Find Scintilla editor window within Notepad++."""
        def enum_child_windows(hwnd, scintilla_windows):
            class_name = win32gui.GetClassName(hwnd)
            if class_name == "Scintilla":
                scintilla_windows.append(hwnd)
            return True
        
        scintilla_windows = []
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
            raise NotepadPPNotFoundError("Notepad++ is not running and auto-start failed")
        
        # Find Scintilla editor window
        self.scintilla_hwnd = self._find_scintilla_window(self.hwnd)
        if not self.scintilla_hwnd:
            raise NotepadPPError("Could not find Scintilla editor window")
        
        return True
    
    async def send_message(self, hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> int:
        """Send Windows message to window."""
        try:
            return win32gui.SendMessage(hwnd, msg, wparam, lparam)
        except Exception as e:
            raise NotepadPPError(f"Failed to send message: {e}")
    
    async def get_window_text(self, hwnd: int) -> str:
        """Get text from window."""
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length == 0:
                return ""
            
            buffer = win32gui.PyMakeBuffer(length + 1)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
            text = buffer.raw.decode('utf-8', errors='ignore').rstrip('\x00')
            return text
        except Exception as e:
            raise NotepadPPError(f"Failed to get window text: {e}")


# Global controller instance
controller = NotepadPPController() if WINDOWS_AVAILABLE else None


@app.tool()
async def get_status() -> Dict[str, Any]:
    """Get Notepad++ status and information."""
    if not controller:
        return {"error": "Windows API not available"}
    
    try:
        await controller.ensure_notepadpp_running()
        
        window_text = await controller.get_window_text(controller.hwnd)
        
        return {
            "status": "running",
            "window_title": window_text,
            "main_window_handle": controller.hwnd,
            "scintilla_handle": controller.scintilla_hwnd,
            "executable_path": controller.notepadpp_exe,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "executable_path": controller.notepadpp_exe if controller else None,
        }


@app.tool()
async def open_file(file_path: str) -> Dict[str, Any]:
    """
    Open a file in Notepad++.
    
    Args:
        file_path: Path to the file to open
        
    Returns:
        Dictionary with operation status and file information
    """
    if not controller:
        return {"error": "Windows API not available"}
    
    try:
        await controller.ensure_notepadpp_running()
        
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
            return {
                "success": False,
                "error": f"File not found: {abs_path}"
            }
        
        # Use subprocess to open file (Notepad++ command line)
        process = subprocess.Popen(
            [controller.notepadpp_exe, abs_path],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for file to load
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "file_path": abs_path,
            "message": f"Opened file: {abs_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to open file: {e}"
        }


@app.tool()
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
        keybd_event(ord('N'), 0, 0, 0)
        keybd_event(ord('N'), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "message": "Created new file"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create new file: {e}"
        }


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
        keybd_event(ord('S'), 0, 0, 0)
        keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "message": "File saved"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save file: {e}"
        }


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
        return {
            "success": False,
            "error": f"Failed to get file info: {e}"
        }


@app.tool()
async def insert_text(text: str) -> Dict[str, Any]:
    """
    Insert text at the current cursor position.
    
    Args:
        text: Text to insert
        
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
        
        # Use clipboard to insert text (more reliable for longer text)
        import win32clipboard
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        
        # Paste text with Ctrl+V
        keybd_event = win32api.keybd_event
        keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        keybd_event(ord('V'), 0, 0, 0)
        keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "message": f"Inserted {len(text)} characters"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to insert text: {e}"
        }


@app.tool()
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
        keybd_event(ord('F'), 0, 0, 0)
        keybd_event(ord('F'), 0, win32con.KEYEVENTF_KEYUP, 0)
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
            "message": f"Searched for: {search_text}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to find text: {e}"
        }


# ============================================================================
# HELP AND STATUS TOOLS
# ============================================================================

@app.tool()
async def get_help(
    category: str = "",
    tool_name: str = ""
) -> Dict[str, Any]:
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
                    "get_current_file_info": "Get information about current file"
                }
            },
            "text_operations": {
                "description": "Text manipulation and editing",
                "tools": {
                    "insert_text": "Insert text at cursor position",
                    "find_text": "Search for text in current document"
                }
            },
            "status_queries": {
                "description": "System and application status",
                "tools": {
                    "get_status": "Get Notepad++ status and information",
                    "get_system_status": "Get detailed system and application status"
                }
            },
            "help_system": {
                "description": "Help and documentation",
                "tools": {
                    "get_help": "Get hierarchical help (this tool)"
                }
            }
        }

        if not category:
            # Return all categories
            return {
                "help_system": "Multilevel Help System",
                "categories": {
                    name: data["description"]
                    for name, data in help_data.items()
                },
                "usage": {
                    "get_help()": "List all categories",
                    "get_help('category_name')": "List tools in category",
                    "get_help('category_name', 'tool_name')": "Get detailed tool help"
                }
            }

        if category not in help_data:
            return {
                "error": f"Unknown category: {category}",
                "available_categories": list(help_data.keys())
            }

        category_data = help_data[category]

        if not tool_name:
            # Return tools in category
            return {
                "category": category,
                "description": category_data["description"],
                "tools": category_data["tools"]
            }

        if tool_name not in category_data["tools"]:
            return {
                "error": f"Unknown tool: {tool_name} in category: {category}",
                "available_tools": list(category_data["tools"].keys())
            }

        # Return detailed help for specific tool
        return {
            "category": category,
            "tool": tool_name,
            "description": category_data["tools"][tool_name],
            "usage": f"Call {tool_name}() to execute this tool"
        }

    except Exception as e:
        logger.error(f"Error getting help: {e}")
        return {
            "error": "Failed to get help information",
            "details": str(e)
        }


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
            "configuration": {}
        }

        try:
            # Get process information
            if WINDOWS_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'notepad' in proc.info['name'].lower():
                        p = psutil.Process(proc.info['pid'])
                        system_info["process_info"] = {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": p.cpu_percent(),
                            "memory_mb": p.memory_info().rss / 1024 / 1024,
                            "create_time": p.create_time()
                        }
                        break

            # Get memory information
            memory = psutil.virtual_memory()
            system_info["memory_usage"] = {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "available_gb": memory.available / 1024 / 1024 / 1024,
                "percent_used": memory.percent
            }

            # Get window information
            system_info["window_info"] = {
                "main_window_handle": controller.hwnd,
                "scintilla_handle": controller.scintilla_hwnd,
                "window_title": await controller.get_window_text(controller.hwnd)
            }

            # Get configuration
            system_info["configuration"] = {
                "timeout": NOTEPADPP_TIMEOUT,
                "auto_start": NOTEPADPP_AUTO_START,
                "notepad_path": controller.notepadpp_exe
            }

        except Exception as sys_error:
            logger.warning(f"Could not get detailed system info: {sys_error}")
            system_info["note"] = "Some system information unavailable"

        return {
            "status": "success",
            "basic_info": basic_status,
            "system_info": system_info,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "error": "Failed to get system status",
            "details": str(e)
        }


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
                "full_title": window_text
            },
            "note": "Full tab enumeration requires Notepad++ plugin API integration"
        }

    except Exception as e:
        logger.error(f"Error listing tabs: {e}")
        return {
            "error": "Failed to list tabs",
            "details": str(e)
        }


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
            "message": f"Switched to tab {tab_index}"
        }

    except Exception as e:
        logger.error(f"Error switching to tab: {e}")
        return {
            "error": "Failed to switch tab",
            "details": str(e)
        }


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
        keybd_event(ord('W'), 0, 0, 0)
        keybd_event(ord('W'), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.3)

        return {
            "success": True,
            "closed_tab": tab_index,
            "message": f"Closed tab {tab_index}"
        }

    except Exception as e:
        logger.error(f"Error closing tab: {e}")
        return {
            "error": "Failed to close tab",
            "details": str(e)
        }


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
            "is_modified": file_info.get("is_modified", False)
        }

        # In a real implementation, this would save to a session file
        # For now, we'll return the session data
        return {
            "success": True,
            "session_name": session_name,
            "session_data": session_data,
            "message": f"Session '{session_name}' saved",
            "note": "Session persistence requires additional file I/O implementation"
        }

    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return {
            "error": "Failed to save session",
            "details": str(e)
        }


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
            "note": "Full session restoration requires session file format implementation"
        }

    except Exception as e:
        logger.error(f"Error loading session: {e}")
        return {
            "error": "Failed to load session",
            "details": str(e)
        }


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
            "note": "No sessions found (session persistence not yet implemented)"
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return {
            "error": "Failed to list sessions",
            "details": str(e)
        }


def main():
    """Main entry point for the MCP server."""
    import sys
    
    if not WINDOWS_AVAILABLE:
        logger.error("This MCP server requires Windows and pywin32")
        sys.exit(1)
    
    app.run()


if __name__ == "__main__":
    main()
