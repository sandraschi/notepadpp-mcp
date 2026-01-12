"""
Notepad++ Controller Module

Handles Windows API interactions and Notepad++ automation.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional

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


class NotepadPPError(Exception):
    """Base exception for Notepad++ operations."""

    pass


class NotepadPPNotFoundError(NotepadPPError):
    """Exception raised when Notepad++ is not found."""

    pass


# Configuration
NOTEPADPP_TIMEOUT = int(os.getenv("NOTEPADPP_TIMEOUT", "30"))
NOTEPADPP_AUTO_START = os.getenv("NOTEPADPP_AUTO_START", "true").lower() == "true"
NOTEPADPP_PATH = os.getenv("NOTEPADPP_PATH", None)

# Default Notepad++ installation paths
DEFAULT_NOTEPADPP_PATHS = [
    r"C:\Program Files\Notepad++\notepad++.exe",
    r"C:\Program Files (x86)\Notepad++\notepad++.exe",
    rf"C:\Users\{os.getenv('USERNAME', '')}\AppData\Local\Notepad++\notepad++.exe",
]


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
