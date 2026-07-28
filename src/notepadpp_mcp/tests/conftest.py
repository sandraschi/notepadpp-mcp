"""Test configuration and fixtures for notepadpp-mcp tests.

This file sets up global mocks and module-level patches to guarantee
complete isolation from the Win32 API during tests.
"""

import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(autouse=True)
def patch_win32_in_modules():
    """Session-wide autouse fixture to patch win32* modules in all project files."""
    mock_gui = MagicMock()
    mock_api = MagicMock()
    mock_clip = MagicMock()

    # Configure mock_gui defaults
    mock_gui.IsWindowVisible = MagicMock(return_value=True)
    mock_gui.GetWindowText = MagicMock(return_value="test.txt - Notepad++")
    mock_gui.GetClassName = MagicMock(return_value="Notepad++")

    modules_to_patch = [
        "notepadpp_mcp.tools.file_operations",
        "notepadpp_mcp.tools.text_operations",
        "notepadpp_mcp.tools.display_operations",
        "notepadpp_mcp.tools.plugin_operations",
        "notepadpp_mcp.tools.tab_operations",
        "notepadpp_mcp.tools.session_operations",
        "notepadpp_mcp.tools.controller",
    ]

    patches = []
    for mod in modules_to_patch:
        patches.append(patch(f"{mod}.win32gui", mock_gui, create=True))
        patches.append(patch(f"{mod}.win32api", mock_api, create=True))
        patches.append(patch(f"{mod}.win32clipboard", mock_clip, create=True))

    for p in patches:
        p.start()

    yield {
        "win32gui": mock_gui,
        "win32api": mock_api,
        "win32clipboard": mock_clip,
    }

    for p in patches:
        p.stop()


@pytest.fixture
def mock_win32() -> MagicMock:
    """Fixture returning a mocked win32 gui module."""
    return MagicMock()


@pytest.fixture
def mock_notepadpp_controller(mock_win32: Any) -> Any:
    """Create a mocked NotepadPPController."""
    from notepadpp_mcp.tools.controller import NotepadPPController

    with patch.object(
        NotepadPPController, "_find_notepadpp_exe", return_value=r"C:\Program Files\Notepad++\notepad++.exe"
    ):
        with patch.object(NotepadPPController, "_find_notepadpp_window", return_value=12345):
            with patch.object(NotepadPPController, "_find_scintilla_window", return_value=54321):
                controller = NotepadPPController()
                controller.hwnd = 12345
                controller.scintilla_hwnd = 54321
                yield controller
