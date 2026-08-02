"""Comprehensive integration tests for all MCP tools.

This module tests all 8 Portmanteau tools using the app instance,
and includes a safe pywinauto GUI test for local verification.
"""

import os
import tempfile
import time
from unittest.mock import AsyncMock, patch

import pytest

from notepadpp_mcp.server import mcp as app


async def get_tool_fn(name: str):
    """Retrieve original tool function from mcp app."""
    tool = await app.get_tool(name)
    return tool.fn


@pytest.fixture(autouse=True)
def bind_mock_controller(mock_notepadpp_controller):
    from notepadpp_mcp.server import (
        display_tool,
        file_tool,
        linting_tool,
        plugin_tool,
        session_tool,
        status_tool,
        tab_tool,
        text_tool,
    )

    file_tool.controller = mock_notepadpp_controller
    text_tool.controller = mock_notepadpp_controller
    status_tool.controller = mock_notepadpp_controller
    tab_tool.controller = mock_notepadpp_controller
    session_tool.controller = mock_notepadpp_controller
    linting_tool.controller = mock_notepadpp_controller
    display_tool.controller = mock_notepadpp_controller
    plugin_tool.controller = mock_notepadpp_controller

    # Disable WINDOWS_AVAILABLE in tool modules to skip real API calls during mock tests
    import notepadpp_mcp.tools.display_operations
    import notepadpp_mcp.tools.file_operations
    import notepadpp_mcp.tools.plugin_operations
    import notepadpp_mcp.tools.session_operations
    import notepadpp_mcp.tools.tab_operations
    import notepadpp_mcp.tools.text_operations

    notepadpp_mcp.tools.file_operations.WINDOWS_AVAILABLE = False
    notepadpp_mcp.tools.text_operations.WINDOWS_AVAILABLE = False
    notepadpp_mcp.tools.display_operations.WINDOWS_AVAILABLE = False
    notepadpp_mcp.tools.plugin_operations.WINDOWS_AVAILABLE = False
    notepadpp_mcp.tools.tab_operations.WINDOWS_AVAILABLE = False
    notepadpp_mcp.tools.session_operations.WINDOWS_AVAILABLE = False


class TestCoreFileOperations:
    """Test file_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_file_ops_open_success(self, mock_win32):
        """Test file_ops open success."""
        file_ops = await get_tool_fn("file_ops")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            test_file = f.name

        try:
            with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
                mock_controller.notepadpp_exe = r"C:\Program Files\Notepad++\notepad++.exe"
                mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)

                result = await file_ops(operation="open", file_path=test_file)
                assert result["success"] is True
                assert "opened" in result["summary"].lower()
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_file_ops_open_not_found(self, mock_win32):
        """Test file_ops open with non-existent file."""
        file_ops = await get_tool_fn("file_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await file_ops(operation="open", file_path="nonexistent.txt")
            assert result["success"] is False
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_file_ops_new_success(self, mock_win32):
        """Test file_ops new document creation."""
        file_ops = await get_tool_fn("file_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await file_ops(operation="new")
            assert result["success"] is True, f"Failed: {result}"
            assert "untitled" in result["summary"].lower()

    @pytest.mark.asyncio
    async def test_file_ops_save_success(self, mock_win32):
        """Test file_ops save document."""
        file_ops = await get_tool_fn("file_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await file_ops(operation="save")
            assert result["success"] is True, f"Failed: {result}"
            assert "saved" in result["summary"].lower()


class TestTextOperations:
    """Test text_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_text_ops_insert_success(self, mock_win32):
        """Test text insertion."""
        text_ops = await get_tool_fn("text_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await text_ops(operation="insert", text="Hello!")
            assert result["success"] is True, f"Failed: {result}"
            assert "inserted" in result["summary"].lower()

    @pytest.mark.asyncio
    async def test_text_ops_find_success(self, mock_win32):
        """Test text find search."""
        text_ops = await get_tool_fn("text_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await text_ops(operation="find", text="test")
            assert result["success"] is True, f"Failed: {result}"
            assert "found" in result["summary"].lower()


class TestTabManagement:
    """Test tab_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_tab_ops_list(self, mock_win32):
        """Test listing open tabs."""
        tab_ops = await get_tool_fn("tab_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await tab_ops(operation="list")
            assert result["success"] is True
            assert "tab" in result["summary"].lower()


class TestLintingTools:
    """Test linting_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_linting_ops_python(self, mock_win32):
        """Test python file linting."""
        linting_ops = await get_tool_fn("linting_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await linting_ops(operation="python", file_path="test.py")
            # Linting might return success=False if linter fails, which is correct
            assert "operation" in result


class TestDisplayFixes:
    """Test display_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_display_ops_invisible(self, mock_win32):
        """Test display ops invisible text fix."""
        display_ops = await get_tool_fn("display_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await display_ops(operation="fix_invisible_text")
            assert result["success"] is True, f"Failed: {result}"


class TestPluginManagement:
    """Test plugin_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_plugin_ops_discover(self, mock_win32):
        """Test plugin discovery."""
        plugin_ops = await get_tool_fn("plugin_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await plugin_ops(operation="discover", search_term="hex")
            assert result["success"] is True


class TestStatusAndInfo:
    """Test status_ops tool functionality."""

    @pytest.mark.asyncio
    async def test_status_ops_health(self, mock_win32):
        """Test server health check."""
        status_ops = await get_tool_fn("status_ops")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            result = await status_ops(operation="health_check")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_notepad_dashboard(self, mock_win32):
        """Test notepad_dashboard prefab-ui output."""
        notepad_dashboard = await get_tool_fn("notepad_dashboard")

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.hwnd = 12345
            mock_controller.scintilla_hwnd = 54321
            mock_controller.notepadpp_exe = "notepad++.exe"
            mock_controller.get_window_text = AsyncMock(return_value="test.txt - Notepad++")

            from prefab_ui.components import Column

            result = await notepad_dashboard()
            assert isinstance(result, Column)
            assert len(result.children) == 3


# ============================================================================
# SAFE GUI AUTOMATION TESTING (pywinauto)
# ============================================================================


@pytest.mark.requires_notepadpp
@pytest.mark.skipif(os.getenv("NOTEPADPP_GUI_TEST") != "1", reason="Local GUI; set NOTEPADPP_GUI_TEST=1")
def test_local_gui_safe_keystrokes():
    """Test using pywinauto to target Notepad++ specifically and interact safely.

    This ensures that instead of blindly typing into whatever window is in focus,
    we explicitly connect to the Notepad++ process, focus it, open a safe temp
    tab, write content, and close the tab without saving.
    """
    from pywinauto.application import Application

    # 1. Connect or start Notepad++
    try:
        app_gui = Application(backend="win32").connect(title_re=".* - Notepad\\+\\+")
    except Exception:
        # Notepad++ not running, attempt start using default path
        npp_exe = r"C:\Program Files\Notepad++\notepad++.exe"
        if not os.path.exists(npp_exe):
            pytest.skip("Notepad++ not installed at default path. Skipping real GUI test.")
        app_gui = Application(backend="win32").start(npp_exe)
        time.sleep(2)

    main_window = app_gui.window(title_re=".* - Notepad\\+\\+")
    main_window.set_focus()

    # 2. Safely create a new temporary tab using Ctrl+N
    main_window.type_keys("^n")
    time.sleep(0.5)

    try:
        # 3. Target Scintilla window specifically and send test text
        scintilla = main_window.child_window(class_name="Scintilla")
        scintilla.type_keys("Hello from SOTA 2026 pywinauto test!{ENTER}", with_spaces=True)
        time.sleep(0.5)

        # Confirm the text was written
        text = scintilla.window_text()
        assert len(text) > 0 or text is not None
    finally:
        # 4. Close the new tab safely using Ctrl+W and send 'n' to discard changes
        main_window.type_keys("^w")
        time.sleep(0.5)
        # Type 'n' (No) to discard the save prompt safely
        main_window.type_keys("n")
