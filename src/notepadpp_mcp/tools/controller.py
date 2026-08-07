"""
Notepad++ Controller Module

Handles Windows API interactions and Notepad++ automation.

TRANSPORT NOTE (empirical, Notepad++ 8.x):
- Scintilla *int-only* messages work from external processes: GETLENGTH,
  GETLINECOUNT, GETCURRENTPOS/ANCHOR, GETSELECTIONSTART/END, GETCOLUMN,
  LINEFROMPOSITION, GOTOPOS, GOTOLINE.
- Scintilla *pointer* messages (SCI_GETTEXT/SETTEXT/REPLACESEL/SETSEL/GETLINE)
  and NPPM_* menu-command messages are NOT serviced by this NPP build.
- Therefore text transport uses the clipboard + keystrokes (needs the editor
  foreground) with verify-after, and named files are read from disk.
"""

import asyncio
import ctypes
import os
import subprocess
import time
from pathlib import Path
from typing import Any

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

# Scintilla message codes that work externally (int-only, verified)
SCI_GETCURRENTPOS = 2008
SCI_GETANCHOR = 2009
SCI_GETCOLUMN = 2129
SCI_GETSELECTIONSTART = 2143
SCI_GETSELECTIONEND = 2144
SCI_GETLINECOUNT = 2154
SCI_LINEFROMPOSITION = 2166
SCI_GETLENGTH = 2183
SCI_GOTOLINE = 2024
SCI_GOTOPOS = 2025

# Scintilla pointer/menu messages - NOT serviced by NPP 8.x (kept for docs/fallback)
SCI_GETTEXT = 2182
SCI_SETTEXT = 2181
SCI_SETSEL = 2013
SCI_REPLACESEL = 2170

# Notepad++ main-window message (attempted first for full paths; often unsupported)
NPPM_GETFULLCURRENTPATH = 1024 + 213

# 64-bit-safe SendMessageW signature (default ctypes marshalling truncates pointers)
_User32SendMessageW = None


def _send_message_w(hwnd: int, msg: int, wparam: int, lparam) -> int:
    """SendMessageW with explicit 64-bit argtypes (pointer-safe)."""
    global _User32SendMessageW
    if _User32SendMessageW is None:
        _User32SendMessageW = ctypes.windll.user32.SendMessageW
        _User32SendMessageW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]
        _User32SendMessageW.restype = ctypes.c_ssize_t
    if lparam is None:
        lparam = 0
    return int(_User32SendMessageW(hwnd, msg, wparam, lparam))


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

    def _find_notepadpp_window(self) -> int | None:
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

    def _find_scintilla_window(self, main_hwnd: int) -> int | None:
        """Find the editor Scintilla window within Notepad++ (first non-empty buffer)."""
        candidates: list[int] = []

        def enum_child_windows(hwnd: int, scintilla_windows: list[int]) -> bool:
            if win32gui.GetClassName(hwnd) == "Scintilla":
                scintilla_windows.append(hwnd)
            return True

        win32gui.EnumChildWindows(main_hwnd, enum_child_windows, candidates)
        if not candidates:
            return None
        # Prefer the Scintilla with content (editor) over dialog-internal ones.
        best = candidates[0]
        best_len = -1
        for hwnd in candidates:
            try:
                length = _send_message_w(hwnd, SCI_GETLENGTH, 0, 0)
            except Exception:
                length = 0
            if length > best_len:
                best_len = length
                best = hwnd
        return best

    async def ensure_notepadpp_running(self) -> bool:
        """Ensure Notepad++ is running, start if needed."""
        self.hwnd = self._find_notepadpp_window()

        if not self.hwnd and NOTEPADPP_AUTO_START:
            subprocess.Popen([self.notepadpp_exe], shell=False)
            for _ in range(50):  # 5 seconds max
                await asyncio.sleep(0.1)
                self.hwnd = self._find_notepadpp_window()
                if self.hwnd:
                    break

        if not self.hwnd:
            raise NotepadPPNotFoundError("Notepad++ is not running and auto-start failed")

        self.scintilla_hwnd = self._find_scintilla_window(self.hwnd)
        if not self.scintilla_hwnd:
            raise NotepadPPError("Could not find Scintilla editor window")

        return True

    async def send_message(self, hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> int:
        """Send Windows message to window."""
        try:
            return _send_message_w(hwnd, msg, wparam, lparam)
        except Exception as e:
            raise NotepadPPError(f"Failed to send message: {e}") from e

    def get_window_text(self, hwnd: int) -> str:
        """Get caption text for a window (title bar)."""
        try:
            return win32gui.GetWindowText(hwnd) or ""
        except Exception as e:
            raise NotepadPPError(f"Failed to get window text: {e}") from e

    # ------------------------------------------------------------------
    # Scintilla int-only primitives (verified working on NPP 8.x)
    # ------------------------------------------------------------------

    def _sci(self, msg: int, wparam: int = 0, lparam: int = 0) -> int:
        """Send an int-only Scintilla message to the editor window."""
        if not self.scintilla_hwnd:
            raise NotepadPPError("Scintilla window not found - call ensure_notepadpp_running() first")
        return _send_message_w(self.scintilla_hwnd, msg, wparam, lparam)

    def get_buffer_length(self) -> int:
        """Length of the active buffer in characters."""
        return self._sci(SCI_GETLENGTH)

    def get_line_count(self) -> int:
        """Number of lines in the active buffer."""
        return self._sci(SCI_GETLINECOUNT)

    def get_caret(self) -> int:
        """Current caret position."""
        return self._sci(SCI_GETCURRENTPOS)

    def get_selection(self) -> tuple[int, int]:
        """Return (start, end) of the current selection."""
        start = self._sci(SCI_GETSELECTIONSTART)
        end = self._sci(SCI_GETSELECTIONEND)
        return start, end

    def goto_pos(self, pos: int) -> None:
        """Move the caret to a character position."""
        self._sci(SCI_GOTOPOS, max(0, pos), 0)

    def goto_line(self, line: int) -> None:
        """Move the caret to the start of a 1-based line (clamped)."""
        self._sci(SCI_GOTOLINE, max(1, line) - 1, 0)

    # ------------------------------------------------------------------
    # Modal dialog handling (Notepad++ Save/Confirm dialogs)
    # ------------------------------------------------------------------

    def _find_modal_dialog(self) -> int | None:
        """Find a modal #32770 dialog owned by the Notepad++ process."""
        if not self.hwnd:
            return None
        try:
            import win32process

            _, npp_pid = win32process.GetWindowThreadProcessId(self.hwnd)
        except Exception:
            return None
        found: list[int] = []

        def cb(hwnd: int, _lparam) -> bool:
            try:
                if win32gui.GetClassName(hwnd) == "#32770":
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == npp_pid:
                        found.append(hwnd)
            except Exception:
                pass
            return True

        win32gui.EnumWindows(cb, None)
        return found[0] if found else None

    def has_modal_dialog(self) -> bool:
        """True when a Notepad++ modal dialog (e.g. Save file?) is open."""
        return self._find_modal_dialog() is not None

    def dismiss_save_dialog(self, choice: str = "no") -> bool:
        """Click a button on the NPP modal dialog (No/Cancel/Yes) via BM_CLICK.

        Deterministic - no foreground required. Returns True when a button
        was clicked. 'no' = close without saving (discard), 'yes' = save.
        """
        dlg = self._find_modal_dialog()
        if not dlg:
            return False
        buttons: list[tuple[int, str]] = []

        def cb(hwnd: int, _lparam) -> bool:
            try:
                if win32gui.GetClassName(hwnd) == "Button":
                    buttons.append((hwnd, win32gui.GetWindowText(hwnd)))
            except Exception:
                pass
            return True

        win32gui.EnumChildWindows(dlg, cb, None)
        for hwnd, text in buttons:
            # Buttons carry accelerator prefixes: "&No" -> "No"
            if text.replace("&", "").strip().lower() == choice.lower():
                _send_message_w(hwnd, 0x00F5, 0, 0)  # BM_CLICK
                return True
        # Fallback: Cancel (safe default - aborts the dialog)
        for hwnd, text in buttons:
            if text.replace("&", "").strip().lower() == "cancel":
                _send_message_w(hwnd, 0x00F5, 0, 0)
                return True
        return False

    def _bring_to_foreground(self) -> bool:
        """Bring Notepad++ to the foreground (with thread-attach fallback)."""
        if not self.hwnd:
            return False
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            return True
        except Exception:
            pass
        try:
            import win32process

            cur = win32gui.GetForegroundWindow()
            if cur:
                cur_tid = win32process.GetWindowThreadProcessId(cur)[0]
            else:
                cur_tid = None
            my_tid = win32api.GetCurrentThreadId()
            if cur_tid and cur_tid != my_tid:
                win32process.AttachThreadInput(my_tid, cur_tid, True)
            win32gui.BringWindowToTop(self.hwnd)
            try:
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception:
                pass
            if cur_tid and cur_tid != my_tid:
                win32process.AttachThreadInput(my_tid, cur_tid, False)
            return True
        except Exception:
            return False

    def _key_chord(self, keys: list[str]) -> None:
        """Simulate a key chord (e.g. ['ctrl', 'v']) on the foreground window."""
        mods = {
            "ctrl": win32con.VK_CONTROL,
            "shift": win32con.VK_SHIFT,
            "alt": win32con.VK_MENU,
        }
        down: list[int] = []
        try:
            for key in keys:
                code = mods.get(key)
                if code is not None:
                    win32api.keybd_event(code, 0, 0, 0)
                    down.append(code)
                else:
                    vk = ord(key.upper()) if len(key) == 1 else getattr(win32con, f"VK_{key.upper()}", 0)
                    if vk:
                        win32api.keybd_event(vk, 0, 0, 0)
                        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
        finally:
            for code in reversed(down):
                win32api.keybd_event(code, 0, win32con.KEYEVENTF_KEYUP, 0)

    def _clipboard_set(self, text: str) -> None:
        import win32clipboard

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()

    def _clipboard_get(self) -> str:
        import win32clipboard

        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT) or ""
            return ""
        finally:
            win32clipboard.CloseClipboard()

    def paste_text(self, text: str) -> bool:
        """Set the clipboard and paste into the editor (needs foreground). Returns success."""
        if not self._bring_to_foreground():
            return False
        time.sleep(0.15)
        self._clipboard_set(text)
        time.sleep(0.15)
        self._key_chord(["ctrl", "v"])
        time.sleep(0.3)
        return True

    def select_all(self) -> bool:
        """Ctrl+A in the editor (needs foreground). Returns success."""
        if not self._bring_to_foreground():
            return False
        time.sleep(0.15)
        self._key_chord(["ctrl", "a"])
        time.sleep(0.15)
        return True

    def copy_selection_to_clipboard(self) -> bool:
        """Ctrl+C in the editor (needs foreground). Returns success."""
        if not self._bring_to_foreground():
            return False
        time.sleep(0.15)
        self._key_chord(["ctrl", "c"])
        time.sleep(0.2)
        return True

    def new_document(self) -> bool:
        """File > New via keystroke (needs foreground). Returns success."""
        if not self._bring_to_foreground():
            return False
        time.sleep(0.15)
        self._key_chord(["ctrl", "n"])
        time.sleep(0.3)
        return True

    def save_current(self) -> bool:
        """File > Save via keystroke (needs foreground). Returns success."""
        if not self._bring_to_foreground():
            return False
        time.sleep(0.15)
        self._key_chord(["ctrl", "s"])
        time.sleep(0.3)
        return True

    # ------------------------------------------------------------------
    # Text read/write with verify-after (honest - never fake success)
    # ------------------------------------------------------------------

    def get_current_file_path(self) -> str:
        """Full path of the active buffer: NPPM message first, then the window title."""
        try:
            size = 512
            buf = ctypes.create_string_buffer(size)
            result = _send_message_w(self.hwnd or 0, NPPM_GETFULLCURRENTPATH, size, ctypes.cast(buf, ctypes.c_char_p))
            if result and result < size:
                path = buf.value.decode("utf-8", errors="replace")
                if path and os.path.exists(path):
                    return path
        except Exception:
            pass
        # Title fallback: Notepad++ often shows the full path in the title.
        try:
            title = win32gui.GetWindowText(self.hwnd) or ""
            marker = " - Notepad++"
            if marker in title:
                title = title.split(marker)[0]
            name = title[1:] if title.startswith("*") else title
            if name.endswith("*"):
                name = name[:-1]
            name = name.strip()
        except Exception:
            name = ""
        if name and os.path.isabs(name) and os.path.exists(name):
            return name
        return ""

    def get_active_tab_state(self) -> dict:
        """Parse the window title into tab state: filename, dirty, untitled."""
        try:
            title = win32gui.GetWindowText(self.hwnd) or ""
        except Exception:
            title = ""
        rest = title
        marker = " - Notepad++"
        if marker in title:
            rest = title.split(marker)[0]
        dirty = rest.startswith("*") or rest.endswith("*")
        filename = rest[1:] if rest.startswith("*") else rest
        if filename.endswith("*"):
            filename = filename[:-1]
        filename = filename.strip()
        untitled = not filename or filename.lower().startswith("new ") or filename.lower() == "untitled"
        return {
            "title": title,
            "filename": filename,
            "path": self.get_current_file_path(),
            "dirty": dirty,
            "untitled": untitled,
        }

    def get_buffer_text(self) -> tuple[str, str]:
        """Read the active buffer.

        Returns (text, source) where source is 'disk' (clean named file),
        'clipboard' (live buffer - dirty tab or untitled) or '' on failure.

        A dirty tab (unsaved changes) MUST be read from the live buffer -
        reading disk would return stale content and overwrite edits.
        """
        state = self.get_active_tab_state()
        if state["dirty"] or state["untitled"]:
            text = self.get_live_buffer_text()
            if text or self.get_buffer_length() == 0:
                return text, "clipboard"
        path = self.get_current_file_path()
        if path and os.path.exists(path):
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    return f.read(), "disk"
            except OSError:
                return "", ""
        return "", ""

    def set_buffer_text(self, text: str) -> bool:
        """Replace the whole buffer. Clipboard is set FIRST so the paste cannot
        race with a stale clipboard left by a previous verify/copy step."""
        if not self._bring_to_foreground():
            return False
        self._clipboard_set(text)
        time.sleep(0.15)
        self._key_chord(["ctrl", "a"])
        time.sleep(0.2)
        self._key_chord(["ctrl", "v"])
        time.sleep(0.5)  # let the paste land before verification
        return True

    def insert_at_caret(self, text: str) -> bool:
        """Paste text at the caret (replaces any selection). Returns success."""
        return self.paste_text(text)

    def get_live_buffer_text(self) -> str:
        """Read the LIVE buffer (clipboard round-trip) - sees unsaved changes.

        Use for post-edit verification; get_buffer_text() reads disk for named files.
        """
        if self.select_all() and self.copy_selection_to_clipboard():
            return self._clipboard_get()
        return ""

    def verify_buffer(self, expected: str) -> bool:
        """Verify the buffer now holds `expected` (clipboard round-trip: select-all + copy).

        Line endings are normalized (Notepad++ stores CRLF; expected text may use LF).
        Retries twice to absorb editor/foreground timing jitter.
        """

        def _norm(s: str) -> str:
            return s.replace("\r\n", "\n").replace("\r", "\n")

        for _ in range(3):
            if self.select_all() and self.copy_selection_to_clipboard():
                if _norm(self._clipboard_get()) == _norm(expected):
                    return True
            time.sleep(0.3)
        return False


def handle_tool_errors(func):
    """Decorator to handle Notepad++ errors in tools and return standard MCP response."""
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NotepadPPNotFoundError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "NOTEPADPP_NOT_FOUND",
                "message": f"Notepad++ is not running or could not be found: {e}",
            }
        except NotepadPPError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "NOTEPADPP_ERROR",
                "message": f"An error occurred during Notepad++ automation: {e}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "UNKNOWN_ERROR",
                "message": f"An unexpected error occurred: {e}",
            }

    return wrapper
