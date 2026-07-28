"""Tests for the main notepadpp-mcp server functionality and tool metadata."""

from unittest.mock import patch

import pytest

from notepadpp_mcp.server import mcp as app


async def get_tool(name: str):
    """Retrieve tool wrapper from mcp app."""
    return await app.get_tool(name)


class TestMainServerMetadata:
    """Test metadata of all registered FastMCP tools."""

    @pytest.mark.asyncio
    async def test_file_ops_metadata(self, mock_win32):
        """Test file_ops metadata."""
        tool = await get_tool("file_ops")
        assert tool.name == "file_ops"
        assert tool.description is not None
        assert "file" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_text_ops_metadata(self, mock_win32):
        """Test text_ops metadata."""
        tool = await get_tool("text_ops")
        assert tool.name == "text_ops"
        assert "text" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_tab_ops_metadata(self, mock_win32):
        """Test tab_ops metadata."""
        tool = await get_tool("tab_ops")
        assert tool.name == "tab_ops"
        assert "tab" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_status_ops_metadata(self, mock_win32):
        """Test status_ops metadata."""
        tool = await get_tool("status_ops")
        assert tool.name == "status_ops"
        assert "status" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_session_ops_metadata(self, mock_win32):
        """Test session_ops metadata."""
        tool = await get_tool("session_ops")
        assert tool.name == "session_ops"
        assert "session" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_linting_ops_metadata(self, mock_win32):
        """Test linting_ops metadata."""
        tool = await get_tool("linting_ops")
        assert tool.name == "linting_ops"
        assert "lint" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_display_ops_metadata(self, mock_win32):
        """Test display_ops metadata."""
        tool = await get_tool("display_ops")
        assert tool.name == "display_ops"
        assert "display" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_plugin_ops_metadata(self, mock_win32):
        """Test plugin_ops metadata."""
        tool = await get_tool("plugin_ops")
        assert tool.name == "plugin_ops"
        assert "plugin" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_suggest_notepad_plan_metadata(self, mock_win32):
        """Test suggest_notepad_plan metadata."""
        tool = await get_tool("suggest_notepad_plan")
        assert tool.name == "suggest_notepad_plan"
        assert "plan" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_agentic_notepad_workflow_metadata(self, mock_win32):
        """Test agentic_notepad_workflow metadata."""
        tool = await get_tool("agentic_notepad_workflow")
        assert tool.name == "agentic_notepad_workflow"
        assert "workflow" in tool.description.lower()

    @pytest.mark.asyncio
    async def test_notepad_dashboard_metadata(self, mock_win32):
        """Test notepad_dashboard metadata."""
        tool = await get_tool("notepad_dashboard")
        assert tool.name == "notepad_dashboard"
        assert "dashboard" in tool.description.lower()


class TestMainFunction:
    """Test main function and entry point."""

    def test_main_windows_available(self, mock_win32):
        """Test main function when Windows is available."""
        from notepadpp_mcp.server import main

        with patch("notepadpp_mcp.server.WINDOWS_AVAILABLE", True):
            with patch("notepadpp_mcp.server.asyncio.run") as mock_arun:
                main()
                mock_arun.assert_called_once()

    def test_main_windows_not_available(self, mock_win32):
        """Test main function when Windows is not available."""
        from notepadpp_mcp.server import main

        with patch("notepadpp_mcp.server.WINDOWS_AVAILABLE", False):
            with patch("notepadpp_mcp.server.logger.error") as mock_error:
                # sys.exit should raise SystemExit, so we expect it to be raised
                with pytest.raises(SystemExit):
                    main()

                mock_error.assert_called_once_with("This MCP server requires Windows and pywin32")
