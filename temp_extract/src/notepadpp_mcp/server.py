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
from pathlib import Path
from typing import Any, Dict, Optional

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

    except Exception as e:
        return {"success": False, "error": f"Failed to open file: {e}"}


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
        keybd_event(ord("V"), 0, 0, 0)
        keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
        keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.2)

        return {"success": True, "message": f"Inserted {len(text)} characters"}

    except Exception as e:
        return {"success": False, "error": f"Failed to insert text: {e}"}


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


@app.tool()
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


def main() -> None:
    """Main entry point for the MCP server."""
    if not WINDOWS_AVAILABLE:
        logger.error("This MCP server requires Windows and pywin32")
        sys.exit(1)

    app.run()


if __name__ == "__main__":
    main()
