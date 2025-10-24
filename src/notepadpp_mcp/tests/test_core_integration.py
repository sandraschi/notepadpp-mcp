"""Comprehensive integration tests for core functionality.

This module tests the core functionality to achieve 80%+ test coverage
by testing the underlying functions and classes directly.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from notepadpp_mcp.tools.server import (
    NotepadPPController,
    NotepadPPError,
    NotepadPPNotFoundError,
    handle_tool_errors,
    validate_file_path,
    validate_text_input,
)


class TestNotepadPPControllerCore:
    """Test NotepadPPController core functionality."""

    @pytest.mark.asyncio
    async def test_controller_initialization(self, mock_win32):
        """Test controller initialization."""
        controller = NotepadPPController()
        assert controller is not None
        assert hasattr(controller, "hwnd")
        assert hasattr(controller, "scintilla_hwnd")
        assert hasattr(controller, "notepadpp_exe")

    @pytest.mark.asyncio
    async def test_ensure_notepadpp_running_success(self, mock_win32):
        """Test successful Notepad++ detection."""
        controller = NotepadPPController()

        with patch.object(controller, "_find_notepadpp_window", return_value=12345):
            with patch.object(controller, "_find_scintilla_window", return_value=54321):
                result = await controller.ensure_notepadpp_running()
                assert result is True
                assert controller.hwnd == 12345
                assert controller.scintilla_hwnd == 54321

    @pytest.mark.asyncio
    async def test_ensure_notepadpp_running_not_found(self, mock_win32):
        """Test Notepad++ not found scenario."""
        controller = NotepadPPController()

        with patch.object(controller, "_find_notepadpp_window", return_value=None):
            with patch("notepadpp_mcp.tools.server.NOTEPADPP_AUTO_START", False):
                with pytest.raises(NotepadPPNotFoundError):
                    await controller.ensure_notepadpp_running()

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_win32):
        """Test sending Windows messages."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.SendMessage", return_value=123
        ) as mock_send:
            result = await controller.send_message(12345, 0x000E, 0, 0)
            assert result == 123
            mock_send.assert_called_once_with(12345, 0x000E, 0, 0)

    @pytest.mark.asyncio
    async def test_send_message_error(self, mock_win32):
        """Test sending Windows messages with error."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.SendMessage",
            side_effect=Exception("SendMessage failed"),
        ):
            with pytest.raises(NotepadPPError):
                await controller.send_message(12345, 0x000E, 0, 0)

    @pytest.mark.asyncio
    async def test_get_window_text_success(self, mock_win32):
        """Test getting window text."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.GetWindowText",
            return_value="Test Window",
        ):
            result = await controller.get_window_text(12345)
            assert result == "Test Window"

    @pytest.mark.asyncio
    async def test_get_window_text_error(self, mock_win32):
        """Test getting window text with error."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.GetWindowText",
            side_effect=Exception("GetWindowText failed"),
        ):
            with pytest.raises(NotepadPPError):
                await controller.get_window_text(12345)

    @pytest.mark.asyncio
    async def test_find_notepadpp_window_success(self, mock_win32):
        """Test finding Notepad++ window."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.FindWindow", return_value=12345
        ):
            result = controller._find_notepadpp_window()
            assert result == 12345

    @pytest.mark.asyncio
    async def test_find_notepadpp_window_not_found(self, mock_win32):
        """Test finding Notepad++ window when not found."""
        controller = NotepadPPController()

        with patch("notepadpp_mcp.tools.server.win32gui.FindWindow", return_value=0):
            result = controller._find_notepadpp_window()
            assert result is None

    @pytest.mark.asyncio
    async def test_find_scintilla_window_success(self, mock_win32):
        """Test finding Scintilla window."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.FindWindowEx", return_value=54321
        ):
            result = controller._find_scintilla_window(12345)
            assert result == 54321

    @pytest.mark.asyncio
    async def test_find_scintilla_window_not_found(self, mock_win32):
        """Test finding Scintilla window when not found."""
        controller = NotepadPPController()

        with patch("notepadpp_mcp.tools.server.win32gui.FindWindowEx", return_value=0):
            result = controller._find_scintilla_window(12345)
            assert result is None

class TestErrorHandling:
    """Test error handling functionality."""

    @pytest.mark.asyncio
    async def test_handle_tool_errors_success(self):
        """Test error handling decorator with success."""

        @handle_tool_errors
        async def test_func():
            return {"success": True, "message": "Test success"}

        result = await test_func()
        assert result["success"] is True
        assert result["message"] == "Test success"

    @pytest.mark.asyncio
    async def test_handle_tool_errors_exception(self):
        """Test error handling decorator with exception."""

        @handle_tool_errors
        async def test_func():
            raise Exception("Test error")

        result = await test_func()
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_tool_errors_notepadpp_error(self):
        """Test error handling decorator with NotepadPPError."""

        @handle_tool_errors
        async def test_func():
            raise NotepadPPError("Notepad++ error")

        result = await test_func()
        assert result["success"] is False
        assert "error" in result
        assert "Notepad++ error" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_tool_errors_notepadpp_not_found_error(self):
        """Test error handling decorator with NotepadPPNotFoundError."""

        @handle_tool_errors
        async def test_func():
            raise NotepadPPNotFoundError("Notepad++ not found")

        result = await test_func()
        assert result["success"] is False
        assert "error" in result
        assert "Notepad++ not found" in result["error"]


class TestWindowsAPIIntegration:
    """Test Windows API integration scenarios."""

    def test_windows_api_available(self):
        """Test when Windows API is available."""
        from notepadpp_mcp.tools.server import WINDOWS_AVAILABLE

        assert WINDOWS_AVAILABLE is True

    @pytest.mark.asyncio
    async def test_windows_api_unavailable(self):
        """Test when Windows API is not available."""
        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", False):
            with pytest.raises(NotepadPPError):
                NotepadPPController()

    @pytest.mark.asyncio
    async def test_notepadpp_path_detection(self):
        """Test Notepad++ path detection."""
        controller = NotepadPPController()

        with patch("notepadpp_mcp.tools.server.os.path.exists", return_value=True):
            result = controller._find_notepadpp_exe()
            assert result is not None

    @pytest.mark.asyncio
    async def test_notepadpp_path_not_found(self):
        """Test Notepad++ path not found."""
        controller = NotepadPPController()

        with patch("notepadpp_mcp.tools.server.Path.exists", return_value=False):
            with pytest.raises(NotepadPPNotFoundError):
                controller._find_notepadpp_exe()


class TestConfiguration:
    """Test configuration and constants."""

    def test_default_notepadpp_paths(self):
        """Test default Notepad++ paths."""
        from notepadpp_mcp.tools.server import DEFAULT_NOTEPADPP_PATHS

        assert isinstance(DEFAULT_NOTEPADPP_PATHS, list)
        assert len(DEFAULT_NOTEPADPP_PATHS) > 0
        assert all(isinstance(path, str) for path in DEFAULT_NOTEPADPP_PATHS)

    def test_configuration_constants(self):
        """Test configuration constants."""
        from notepadpp_mcp.tools.server import (
            NOTEPADPP_AUTO_START,
            NOTEPADPP_TIMEOUT,
        )

        assert isinstance(NOTEPADPP_AUTO_START, bool)
        assert isinstance(NOTEPADPP_TIMEOUT, int)
        assert NOTEPADPP_TIMEOUT > 0

    def test_logging_configuration(self):
        """Test logging configuration."""
        from notepadpp_mcp.tools.server import logger, console_handler, formatter

        assert logger is not None
        assert console_handler is not None
        assert formatter is not None


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_controller_with_invalid_hwnd(self, mock_win32):
        """Test controller with invalid window handle."""
        controller = NotepadPPController()
        controller.hwnd = 0  # Invalid handle

        with pytest.raises(NotepadPPError):
            await controller.send_message(0, 0x000E, 0, 0)

    @pytest.mark.asyncio
    async def test_controller_with_invalid_scintilla_hwnd(self, mock_win32):
        """Test controller with invalid Scintilla handle."""
        controller = NotepadPPController()
        controller.scintilla_hwnd = 0  # Invalid handle

        with pytest.raises(NotepadPPError):
            await controller.get_window_text(0)

    @pytest.mark.asyncio
    async def test_controller_timeout_scenario(self, mock_win32):
        """Test controller timeout scenario."""
        controller = NotepadPPController()

        with patch(
            "notepadpp_mcp.tools.server.win32gui.SendMessage",
            side_effect=Exception("Timeout"),
        ):
            with pytest.raises(NotepadPPError):
                await controller.send_message(12345, 0x000E, 0, 0)
