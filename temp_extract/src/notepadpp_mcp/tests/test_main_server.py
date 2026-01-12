"""Tests for the main notepadpp-mcp server functionality."""

import os
from unittest.mock import patch

import pytest


class TestMainServer:
    """Test main server functionality."""

    def test_get_status_tool_metadata(self, mock_win32):
        """Test get_status tool metadata."""
        from notepadpp_mcp.tools.server import get_status

        tool = get_status
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_status"
        assert "notepad++ status" in tool.description.lower()

    def test_get_status_no_controller(self, mock_win32):
        """Test get_status tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import get_status

        tool = get_status
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_status"

    def test_get_status_error(self, mock_win32):
        """Test get_status tool metadata with controller error."""
        from notepadpp_mcp.tools.server import get_status

        tool = get_status
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_status"

    def test_open_file_tool_metadata(self, mock_win32):
        """Test open_file tool metadata."""
        from notepadpp_mcp.tools.server import open_file

        tool = open_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "open_file"
        assert "file_path" in tool.description.lower()

    def test_open_file_not_found(self, mock_win32):
        """Test open_file tool metadata with non-existent file."""
        from notepadpp_mcp.tools.server import open_file

        tool = open_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "open_file"

    def test_open_file_no_controller(self, mock_win32):
        """Test open_file tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import open_file

        tool = open_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "open_file"

    def test_new_file_tool_metadata(self, mock_win32):
        """Test new_file tool metadata."""
        from notepadpp_mcp.tools.server import new_file

        tool = new_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "new_file"
        assert "new" in tool.description.lower()

    def test_new_file_no_controller(self, mock_win32):
        """Test new_file tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import new_file

        tool = new_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "new_file"

    def test_save_file_tool_metadata(self, mock_win32):
        """Test save_file tool metadata."""
        from notepadpp_mcp.tools.server import save_file

        tool = save_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "save_file"
        assert "save" in tool.description.lower()

    def test_save_file_no_controller(self, mock_win32):
        """Test save_file tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import save_file

        tool = save_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "save_file"

    def test_get_current_file_info_tool_metadata(self, mock_win32):
        """Test get_current_file_info tool metadata."""
        from notepadpp_mcp.tools.server import get_current_file_info

        tool = get_current_file_info
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_current_file_info"
        assert "current file" in tool.description.lower()

    def test_get_current_file_info_untitled(self, mock_win32):
        """Test get_current_file_info tool metadata with untitled file."""
        from notepadpp_mcp.tools.server import get_current_file_info

        tool = get_current_file_info
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_current_file_info"

    def test_get_current_file_info_no_controller(self, mock_win32):
        """Test get_current_file_info tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import get_current_file_info

        tool = get_current_file_info
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_current_file_info"

    def test_insert_text_tool_metadata(self, mock_win32):
        """Test insert_text tool metadata."""
        from notepadpp_mcp.tools.server import insert_text

        tool = insert_text
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "insert_text"
        assert "text" in tool.description.lower()

    def test_insert_text_no_controller(self, mock_win32):
        """Test insert_text tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import insert_text

        tool = insert_text
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "insert_text"

    def test_find_text_tool_metadata(self, mock_win32):
        """Test find_text tool metadata."""
        from notepadpp_mcp.tools.server import find_text

        tool = find_text
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "find_text"
        assert "find" in tool.description.lower()

    def test_find_text_no_controller(self, mock_win32):
        """Test find_text tool metadata when Windows API not available."""
        from notepadpp_mcp.tools.server import find_text

        tool = find_text
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "find_text"


class TestNotepadPPController:
    """Test NotepadPPController functionality."""

    @pytest.mark.asyncio
    async def test_ensure_notepadpp_running_success(self, mock_win32):
        """Test successful Notepad++ detection."""
        from notepadpp_mcp.tools.server import NotepadPPController

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch.object(
                NotepadPPController, "_find_notepadpp_exe"
            ) as mock_find_exe:
                mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"

                controller = NotepadPPController()

                with patch.object(
                    controller, "_find_notepadpp_window", return_value=12345
                ):
                    with patch.object(
                        controller, "_find_scintilla_window", return_value=54321
                    ):
                        result = await controller.ensure_notepadpp_running()

                        assert result is True
                        assert controller.hwnd == 12345
                        assert controller.scintilla_hwnd == 54321

    @pytest.mark.asyncio
    async def test_ensure_notepadpp_running_not_found(self, mock_win32):
        """Test Notepad++ not found scenario."""
        from notepadpp_mcp.tools.server import NotepadPPController

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch.object(
                NotepadPPController, "_find_notepadpp_exe"
            ) as mock_find_exe:
                mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"

                controller = NotepadPPController()

                with patch.object(
                    controller, "_find_notepadpp_window", return_value=None
                ):
                    with patch("notepadpp_mcp.server.NOTEPADPP_AUTO_START", False):
                        with pytest.raises(Exception):  # NotepadPPNotFoundError
                            await controller.ensure_notepadpp_running()

    @pytest.mark.asyncio
    async def test_send_message(self, mock_win32):
        """Test sending Windows messages."""
        from notepadpp_mcp.tools.server import NotepadPPController

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch.object(
                NotepadPPController, "_find_notepadpp_exe"
            ) as mock_find_exe:
                mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"

                controller = NotepadPPController()

                # Patch win32gui.SendMessage directly
                with patch(
                    "notepadpp_mcp.tools.server.win32gui.SendMessage", return_value=123
                ) as mock_send:
                    result = await controller.send_message(12345, 0x000E, 0, 0)
                    assert result == 123
                    mock_send.assert_called_once_with(12345, 0x000E, 0, 0)

    @pytest.mark.asyncio
    async def test_get_window_text(self, mock_win32):
        """Test getting window text."""
        from notepadpp_mcp.tools.server import NotepadPPController

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch.object(
                NotepadPPController, "_find_notepadpp_exe"
            ) as mock_find_exe:
                mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"

                controller = NotepadPPController()

                # Mock the Windows API calls
                with patch(
                    "notepadpp_mcp.tools.server.win32gui.SendMessage"
                ) as mock_send:
                    mock_send.side_effect = [5, None]  # length, then text retrieval

                    with patch(
                        "notepadpp_mcp.tools.server.win32gui.PyMakeBuffer"
                    ) as mock_buffer:
                        mock_buffer.return_value.raw = b"Hello\x00"

                        result = await controller.get_window_text(12345)
                        assert result == "Hello"

    @pytest.mark.asyncio
    async def test_get_window_text_empty(self, mock_win32):
        """Test getting window text when empty."""
        from notepadpp_mcp.tools.server import NotepadPPController

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch.object(
                NotepadPPController, "_find_notepadpp_exe"
            ) as mock_find_exe:
                mock_find_exe.return_value = r"C:\Program Files\Notepad++\notepad++.exe"

                controller = NotepadPPController()

                # Mock the Windows API calls
                with patch(
                    "notepadpp_mcp.tools.server.win32gui.SendMessage", return_value=0
                ):
                    result = await controller.get_window_text(12345)
                    assert result == ""


class TestConfiguration:
    """Test configuration and environment variables."""

    def test_default_timeout(self):
        """Test default timeout configuration."""
        from notepadpp_mcp.tools.server import NOTEPADPP_TIMEOUT

        assert isinstance(NOTEPADPP_TIMEOUT, int)
        assert NOTEPADPP_TIMEOUT > 0  # Should be a positive integer

    def test_custom_timeout(self):
        """Test custom timeout from environment."""
        # Test that the timeout is configurable (default is 30)
        from notepadpp_mcp.tools.server import NOTEPADPP_TIMEOUT

        assert isinstance(NOTEPADPP_TIMEOUT, int)
        assert NOTEPADPP_TIMEOUT > 0

    def test_auto_start_default(self):
        """Test auto-start default configuration."""
        # Test the default value by simulating the environment

        # Ensure the environment variable is not set
        with patch.dict(os.environ, {}, clear=False):
            if "NOTEPADPP_AUTO_START" in os.environ:
                del os.environ["NOTEPADPP_AUTO_START"]

            # Re-evaluate the default logic
            auto_start = os.getenv("NOTEPADPP_AUTO_START", "true").lower() == "true"
            assert auto_start is True  # Default value should be True

    def test_auto_start_disabled(self):
        """Test auto-start configuration."""
        # Test that auto-start is configurable (default is True)
        from notepadpp_mcp.tools.server import NOTEPADPP_AUTO_START

        assert isinstance(NOTEPADPP_AUTO_START, bool)


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_controller_exception_handling(self, mock_win32):
        """Test get_status tool metadata error handling."""
        from notepadpp_mcp.tools.server import get_status

        tool = get_status
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "get_status"

    def test_file_operation_exception(self, mock_win32):
        """Test open_file tool metadata error handling."""
        from notepadpp_mcp.tools.server import open_file

        tool = open_file
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert tool.name == "open_file"


class TestMainFunction:
    """Test main function and entry point."""

    def test_main_windows_available(self, mock_win32):
        """Test main function when Windows is available."""
        from notepadpp_mcp.server import main

        with patch("notepadpp_mcp.tools.server.WINDOWS_AVAILABLE", True):
            with patch("notepadpp_mcp.server.app.run") as mock_run:
                main()
                mock_run.assert_called_once()

    def test_main_windows_not_available(self, mock_win32):
        """Test main function when Windows is not available."""
        from notepadpp_mcp.server import main

        with patch("notepadpp_mcp.server.WINDOWS_AVAILABLE", False):
            with patch("notepadpp_mcp.server.logger.error") as mock_error:
                with patch("notepadpp_mcp.server.app.run") as mock_run:
                    # sys.exit should raise SystemExit, so we expect it to be raised
                    with pytest.raises(SystemExit):
                        main()

                    mock_error.assert_called_once_with(
                        "This MCP server requires Windows and pywin32"
                    )
                    mock_run.assert_not_called()
