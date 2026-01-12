"""Test configuration and fixtures for notepadpp-mcp tests."""

import os
import sys
from typing import Any
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_win32() -> Any:
    """Mock Windows API modules."""
    with patch.dict(
        "sys.modules",
        {
            "win32gui": Mock(),
            "win32con": Mock(),
            "win32api": Mock(),
            "win32process": Mock(),
            "win32clipboard": Mock(),
        },
    ) as mocked_modules:
        # Set up common constants
        mocked_modules["win32con"].WM_GETTEXTLENGTH = 0x000E
        mocked_modules["win32con"].WM_GETTEXT = 0x000D
        mocked_modules["win32con"].VK_CONTROL = 0x11
        mocked_modules["win32con"].VK_RETURN = 0x0D
        mocked_modules["win32con"].VK_ESCAPE = 0x1B
        mocked_modules["win32con"].KEYEVENTF_KEYUP = 0x0002

        yield mocked_modules


@pytest.fixture
def mock_notepadpp_controller(mock_win32: Any) -> Any:
    """Create a mocked NotepadPPController."""
    from notepadpp_mcp.tools.server import NotepadPPController

    with patch.object(NotepadPPController, "_find_notepadpp_exe") as mock_find_exe:
        mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"
        controller = NotepadPPController()
        controller.hwnd = 12345  # Mock window handle
        controller.scintilla_hwnd = 54321  # Mock Scintilla handle
        yield controller
