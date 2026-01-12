"""
Level 1: Smoke Test
===================
Quick validation that Notepad++ MCP server starts and basic tools work.

Time: 2-3 minutes
Coverage: Critical tools only (20%)
"""

import pytest
from pathlib import Path


@pytest.mark.megatest_smoke
async def test_server_initializes(isolated_test_env, assert_production_safe):
    """Test: MCP server can initialize."""
    test_dir = isolated_test_env["test_dir"]
    assert_production_safe(test_dir)

    # Import and initialize server
    from notepadpp_mcp.tools.server import app

    assert app is not None
    assert hasattr(app, "run_stdio_async")


@pytest.mark.megatest_smoke
async def test_file_operations_available(isolated_test_env):
    """Test: File operations tool is available."""
    from notepadpp_mcp.tools.file_operations import FileOperationsTool

    # Test tool can be instantiated
    tool = FileOperationsTool(None, None)  # No controller needed for instantiation test
    assert tool is not None
    assert hasattr(tool, "register_tools")


@pytest.mark.megatest_smoke
async def test_text_operations_available(isolated_test_env):
    """Test: Text operations tool is available."""
    from notepadpp_mcp.tools.text_operations import TextOperationsTool

    tool = TextOperationsTool(None, None)
    assert tool is not None
    assert hasattr(tool, "register_tools")


@pytest.mark.megatest_smoke
async def test_status_operations_available(isolated_test_env):
    """Test: Status operations tool is available."""
    from notepadpp_mcp.tools.status_operations import StatusOperationsTool

    tool = StatusOperationsTool(None, None)
    assert tool is not None
    assert hasattr(tool, "register_tools")


@pytest.mark.megatest_smoke
async def test_controller_initialization(mock_windows_api):
    """Test: Controller can initialize (with mocks)."""
    from notepadpp_mcp.tools.controller import NotepadPPController

    # Should not raise exception with mocked Windows API
    try:
        controller = NotepadPPController()
        assert controller is not None
    except Exception as e:
        # In mock environment, this is expected to fail gracefully
        assert "Windows API not available" in str(e)


@pytest.mark.megatest_smoke
async def test_basic_file_creation(isolated_test_env, assert_production_safe):
    """Test: Can create test files safely."""
    test_dir = isolated_test_env["test_dir"]
    assert_production_safe(test_dir)

    # Create a test file
    test_file = test_dir / "smoke_test.txt"
    test_content = "This is a smoke test file."
    test_file.write_text(test_content)

    # Verify it was created
    assert test_file.exists()
    assert test_file.read_text() == test_content

    # Verify it's in safe location
    assert_production_safe(test_file)


@pytest.mark.megatest_smoke
async def test_temp_directory_isolation(isolated_test_env):
    """Test: Test directories are properly isolated."""
    test_dir = isolated_test_env["test_dir"]

    # Should contain our test files
    assert (test_dir / "test_files").exists()
    test_files = list((test_dir / "test_files").glob("*.txt"))
    assert len(test_files) == 3  # Created in conftest.py

    # Should not contain any production files
    for file_path in test_dir.rglob("*"):
        assert not str(file_path).startswith("C:\\Program Files")
        assert not str(file_path).startswith("C:\\Windows")


@pytest.mark.megatest_smoke
async def test_import_all_tools():
    """Test: All tool modules can be imported."""
    try:
        from notepadpp_mcp.tools import (
            controller,
            file_operations,
            text_operations,
            status_operations,
            tab_operations,
            session_operations,
            linting_operations,
            display_operations,
            plugin_operations,
        )

        # Verify imports are not None to satisfy linter
        assert controller is not None
        assert file_operations is not None
        assert text_operations is not None
        assert status_operations is not None
        assert tab_operations is not None
        assert session_operations is not None
        assert linting_operations is not None
        assert display_operations is not None
        assert plugin_operations is not None
    except ImportError as e:
        pytest.fail(f"Failed to import tool modules: {e}")


@pytest.mark.megatest_smoke
async def test_mock_windows_api(mock_windows_api):
    """Test: Mock Windows API fixtures work."""
    mocks = mock_windows_api

    assert "win32api" in mocks
    assert "win32con" in mocks
    assert "win32gui" in mocks

    # Test mock functions
    mocks["win32api"].keybd_event.assert_not_called()
    mocks["win32gui"].SetForegroundWindow.assert_not_called()


@pytest.mark.megatest_smoke
async def test_path_safety_functions():
    """Test: Path safety detection works."""
    import tempfile

    # Import functions directly since relative imports don't work in test discovery
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from conftest import is_production_path, is_safe_test_path

    # Test production paths
    assert is_production_path(Path("C:\\Program Files\\Notepad++"))
    assert is_production_path(Path("C:\\Windows\\System32"))

    # Test safe paths
    assert is_safe_test_path(Path(tempfile.gettempdir()) / "test")
    assert is_safe_test_path(Path("tests/megatest"))

    # Test unsafe paths
    assert not is_safe_test_path(Path("C:\\Windows"))
    assert not is_safe_test_path(Path("C:\\Program Files"))


@pytest.mark.megatest_smoke
async def test_checksum_computation(checksum_validator, isolated_test_env):
    """Test: Checksum computation works."""
    test_file = isolated_test_env["test_files"][0]

    checksum1 = checksum_validator(test_file)
    assert checksum1  # Should not be empty
    assert len(checksum1) == 32  # MD5 hex length

    # Same content should give same checksum
    checksum2 = checksum_validator(test_file)
    assert checksum1 == checksum2

    # Different content should give different checksum
    test_file.write_text("different content")
    checksum3 = checksum_validator(test_file)
    assert checksum3 != checksum1
