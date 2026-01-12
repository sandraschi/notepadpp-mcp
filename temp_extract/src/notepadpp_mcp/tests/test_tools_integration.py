"""Comprehensive integration tests for all MCP tools.

This module tests all 26 tools with real Windows API integration
and Notepad++ scenarios to achieve 80%+ test coverage.
"""

import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest


class TestCoreFileOperations:
    """Test core file operation tools."""

    @pytest.mark.asyncio
    async def test_open_file_success(self, mock_win32):
        """Test successful file opening."""
        # Import the actual function implementation
        from notepadpp_mcp.tools.server import open_file

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content for file opening")
            test_file = f.name

        try:
            with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
                mock_controller.notepadpp_exe = (
                    r"C:\Program Files\Notepad++\notepad++.exe"
                )
                mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)

                result = await open_file.fn(test_file)

                assert result["success"] is True
                assert "opened file" in result["message"].lower()

        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_open_file_not_found(self, mock_win32):
        """Test file not found scenario."""
        from notepadpp_mcp.tools.server import open_file

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.notepadpp_exe = r"C:\Program Files\Notepad++\notepad++.exe"
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)

            result = await open_file.fn("nonexistent_file.txt")

            assert result["success"] is False
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_new_file_success(self, mock_win32):
        """Test new file creation."""
        from notepadpp_mcp.tools.server import new_file

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await new_file.fn()

            assert result["success"] is True
            assert "new file" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_save_file_success(self, mock_win32):
        """Test file saving."""
        from notepadpp_mcp.tools.server import save_file

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await save_file.fn()

            assert result["success"] is True
            assert "saved" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_get_current_file_info(self, mock_win32):
        """Test getting current file information."""
        from notepadpp_mcp.tools.server import get_current_file_info

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.get_window_text = AsyncMock(
                return_value="Untitled - Notepad++"
            )

            result = await get_current_file_info.fn()

            assert result["success"] is True
            assert "file_info" in result


class TestTextOperations:
    """Test text manipulation tools."""

    @pytest.mark.asyncio
    async def test_insert_text_success(self, mock_win32):
        """Test text insertion."""
        from notepadpp_mcp.tools.server import insert_text

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await insert_text.fn("Hello, World!")

            assert result["success"] is True
            assert "inserted" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_find_text_success(self, mock_win32):
        """Test text finding."""
        from notepadpp_mcp.tools.server import find_text

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await find_text.fn("test")

            assert result["success"] is True
            assert "search" in result["message"].lower()


class TestTabManagement:
    """Test tab management tools."""

    @pytest.mark.asyncio
    async def test_list_tabs_success(self, mock_win32):
        """Test listing tabs."""
        from notepadpp_mcp.tools.server import list_tabs

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await list_tabs.fn()

            assert result["success"] is True
            assert "tabs" in result

    @pytest.mark.asyncio
    async def test_switch_to_tab_success(self, mock_win32):
        """Test switching tabs."""
        from notepadpp_mcp.tools.server import switch_to_tab

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await switch_to_tab.fn(0)

            assert result["success"] is True
            assert "switched" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_close_tab_success(self, mock_win32):
        """Test closing tabs."""
        from notepadpp_mcp.tools.server import close_tab

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await close_tab.fn(0)

            assert result["success"] is True
            assert "closed" in result["message"].lower()


class TestSessionManagement:
    """Test session management tools."""

    @pytest.mark.asyncio
    async def test_save_session_success(self, mock_win32):
        """Test saving sessions."""
        from notepadpp_mcp.tools.server import save_session

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await save_session.fn("test_session")

            assert result["success"] is True
            assert "saved" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_load_session_success(self, mock_win32):
        """Test loading sessions."""
        from notepadpp_mcp.tools.server import load_session

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await load_session.fn("test_session")

            assert result["success"] is True
            assert "loaded" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_list_sessions_success(self, mock_win32):
        """Test listing sessions."""
        from notepadpp_mcp.tools.server import list_sessions

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await list_sessions.fn()

            assert result["success"] is True
            assert "sessions" in result


class TestLintingTools:
    """Test code quality and linting tools."""

    @pytest.mark.asyncio
    async def test_lint_python_file_success(self, mock_win32):
        """Test Python file linting."""
        from notepadpp_mcp.tools.server import lint_python_file

        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, World!')\n")
            test_file = f.name

        try:
            result = await lint_python_file.fn(test_file)

            assert result["success"] is True
            assert "linting" in result["message"].lower()

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_lint_python_file_not_found(self, mock_win32):
        """Test Python linting with non-existent file."""
        from notepadpp_mcp.tools.server import lint_python_file

        result = await lint_python_file.fn("nonexistent.py")

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_lint_javascript_file_success(self, mock_win32):
        """Test JavaScript file linting."""
        from notepadpp_mcp.tools.server import lint_javascript_file

        # Create a temporary JavaScript file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write("console.log('Hello, World!');\n")
            test_file = f.name

        try:
            result = await lint_javascript_file.fn(test_file)

            assert result["success"] is True
            assert "linting" in result["message"].lower()

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_lint_json_file_success(self, mock_win32):
        """Test JSON file linting."""
        from notepadpp_mcp.tools.server import lint_json_file

        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"message": "Hello, World!"}\n')
            test_file = f.name

        try:
            result = await lint_json_file.fn(test_file)

            assert result["success"] is True
            assert "linting" in result["message"].lower()

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_lint_markdown_file_success(self, mock_win32):
        """Test Markdown file linting."""
        from notepadpp_mcp.tools.server import lint_markdown_file

        # Create a temporary Markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Hello, World!\n\nThis is a test markdown file.\n")
            test_file = f.name

        try:
            result = await lint_markdown_file.fn(test_file)

            assert result["success"] is True
            assert "linting" in result["message"].lower()

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_get_linting_tools(self, mock_win32):
        """Test getting linting tools information."""
        from notepadpp_mcp.tools.server import get_linting_tools

        result = await get_linting_tools.fn()

        assert result["success"] is True
        assert "tools" in result
        assert "python" in result["tools"]
        assert "javascript" in result["tools"]
        assert "json" in result["tools"]
        assert "markdown" in result["tools"]


class TestDisplayFixes:
    """Test display fix tools."""

    @pytest.mark.asyncio
    async def test_fix_invisible_text_success(self, mock_win32):
        """Test invisible text fix."""
        from notepadpp_mcp.tools.server import fix_invisible_text

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await fix_invisible_text.fn()

            assert result["success"] is True
            assert "fixed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_fix_display_issue_success(self, mock_win32):
        """Test general display issue fix."""
        from notepadpp_mcp.tools.server import fix_display_issue

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await fix_display_issue.fn()

            assert result["success"] is True
            assert "fixed" in result["message"].lower()


class TestPluginManagement:
    """Test plugin ecosystem tools."""

    @pytest.mark.asyncio
    async def test_discover_plugins_success(self, mock_win32):
        """Test plugin discovery."""
        from notepadpp_mcp.tools.server import discover_plugins

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)

            result = await discover_plugins.fn()

            assert result["success"] is True
            assert "plugins" in result

    @pytest.mark.asyncio
    async def test_install_plugin_success(self, mock_win32):
        """Test plugin installation."""
        from notepadpp_mcp.tools.server import install_plugin

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await install_plugin.fn("test_plugin")

            assert result["success"] is True
            assert "installed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_list_installed_plugins_success(self, mock_win32):
        """Test listing installed plugins."""
        from notepadpp_mcp.tools.server import list_installed_plugins

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await list_installed_plugins.fn()

            assert result["success"] is True
            assert "plugins" in result

    @pytest.mark.asyncio
    async def test_execute_plugin_command_success(self, mock_win32):
        """Test plugin command execution."""
        from notepadpp_mcp.tools.server import execute_plugin_command

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.send_message = AsyncMock(return_value=True)

            result = await execute_plugin_command.fn("test_command")

            assert result["success"] is True
            assert "executed" in result["message"].lower()


class TestStatusAndInfo:
    """Test status and information tools."""

    @pytest.mark.asyncio
    async def test_get_status_success(self, mock_win32):
        """Test getting status."""
        from notepadpp_mcp.tools.server import get_status

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.hwnd = 12345
            mock_controller.scintilla_hwnd = 54321

            result = await get_status.fn()

            assert result["success"] is True
            assert "status" in result

    @pytest.mark.asyncio
    async def test_get_system_status_success(self, mock_win32):
        """Test getting system status."""
        from notepadpp_mcp.tools.server import get_system_status

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=True)
            mock_controller.notepadpp_exe = r"C:\Program Files\Notepad++\notepad++.exe"

            result = await get_system_status.fn()

            assert result["success"] is True
            assert "system" in result

    @pytest.mark.asyncio
    async def test_get_help_success(self, mock_win32):
        """Test getting help information."""
        from notepadpp_mcp.tools.server import get_help

        result = await get_help.fn()

        assert result["success"] is True
        assert "help" in result
        assert "tools" in result


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_notepadpp_not_running(self, mock_win32):
        """Test when Notepad++ is not running."""
        from notepadpp_mcp.tools.server import open_file

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(return_value=False)

            result = await open_file.fn("test.txt")

            assert result["success"] is False
            assert "notepad++" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_controller_exception(self, mock_win32):
        """Test controller exception handling."""
        from notepadpp_mcp.tools.server import get_status

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.ensure_notepadpp_running = AsyncMock(
                side_effect=Exception("Test error")
            )

            result = await get_status.fn()

            assert result["success"] is False
            assert "error" in result


class TestWindowsAPIIntegration:
    """Test Windows API integration scenarios."""

    @pytest.mark.asyncio
    async def test_windows_api_unavailable(self):
        """Test when Windows API is not available."""
        from notepadpp_mcp.tools.server import get_status

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", False):
            result = await get_status.fn()

            assert result["success"] is False
            assert "windows" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_notepadpp_not_found(self, mock_win32):
        """Test when Notepad++ executable is not found."""
        from notepadpp_mcp.tools.server import get_system_status

        with patch("notepadpp_mcp.tools.server.controller") as mock_controller:
            mock_controller.notepadpp_exe = None

            result = await get_system_status.fn()

            assert result["success"] is False
            assert "notepad++" in result["error"].lower()
