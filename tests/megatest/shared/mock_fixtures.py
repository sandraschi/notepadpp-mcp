"""
Shared mock fixtures for Notepad++ MCP testing.

These fixtures provide comprehensive mocks for:
- Windows API calls
- Notepad++ process simulation
- File system operations
- HTTP requests for plugin discovery
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile


@pytest.fixture
def mock_notepadpp_window():
    """Mock a Notepad++ window handle and operations."""
    return {
        "hwnd": 12345,
        "scintilla_hwnd": 67890,
        "title": "test.txt - Notepad++",
        "class_name": "Notepad++",
        "is_visible": True,
    }


@pytest.fixture
def mock_notepadpp_process():
    """Mock Notepad++ process information."""
    process = Mock()
    process.pid = 1234
    process.name = "notepad++.exe"
    process.is_running = Mock(return_value=True)
    process.terminate = Mock()
    process.wait = Mock()
    return process


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with (
        patch("builtins.open") as mock_open,
        patch("os.path.exists") as mock_exists,
        patch("os.path.abspath") as mock_abspath,
    ):
        # Mock file existence
        mock_exists.return_value = True
        mock_abspath.return_value = "/mock/path/test.txt"

        # Mock file reading
        mock_file = Mock()
        mock_file.read.return_value = "mock file content"
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_open.return_value = mock_file

        yield {"open": mock_open, "exists": mock_exists, "abspath": mock_abspath}


@pytest.fixture
def mock_plugin_api_response():
    """Mock response from Notepad++ Plugin List API."""
    return {
        "plugins": [
            {
                "display-name": "Test Plugin",
                "description": "A test plugin for Notepad++",
                "category": "test",
                "version": "1.0.0",
                "author": "Test Author",
                "homepage": "https://example.com",
            },
            {
                "display-name": "Another Plugin",
                "description": "Another test plugin",
                "category": "utility",
                "version": "2.1.0",
                "author": "Another Author",
                "homepage": "https://another.com",
            },
        ]
    }


@pytest.fixture
def mock_linting_commands():
    """Mock external linting command results."""
    results = {
        "ruff_success": Mock(returncode=0, stdout="[]", stderr=""),
        "ruff_with_issues": Mock(
            returncode=2,
            stdout='[{"type": "error", "message": "test error"}]',
            stderr="",
        ),
        "ruff_not_found": Exception("FileNotFoundError"),
        "eslint_success": Mock(returncode=0, stdout="[]", stderr=""),
        "eslint_not_found": Exception("FileNotFoundError"),
    }
    return results


@pytest.fixture
def mock_system_info():
    """Mock system information for testing."""
    return {
        "os": "Windows",
        "architecture": "64bit",
        "python_version": "3.10.0",
        "memory_percent": 45.0,
        "cpu_count": 8,
        "disk_free": 1000000000,  # 1GB
        "processes": [
            {"name": "notepad++.exe", "pid": 1234},
            {"name": "python.exe", "pid": 5678},
        ],
    }


@pytest.fixture
def mock_temp_directory():
    """Create a mock temporary directory structure."""
    temp_dir = Path(tempfile.mkdtemp(prefix="mock_notepadpp_"))

    # Create mock Notepad++ structure
    notepadpp_dir = temp_dir / "notepadpp"
    notepadpp_dir.mkdir()

    config_dir = notepadpp_dir / "config"
    config_dir.mkdir()

    plugins_dir = notepadpp_dir / "plugins"
    plugins_dir.mkdir()

    # Create mock config files
    (config_dir / "config.xml").write_text("<NotepadPlus><GUIConfigs/></NotepadPlus>")
    (plugins_dir / "test_plugin.dll").write_text("mock dll content")

    yield temp_dir

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_notepadpp_installation(mock_temp_directory):
    """Mock a complete Notepad++ installation."""
    notepadpp_exe = mock_temp_directory / "notepadpp" / "notepad++.exe"
    notepadpp_exe.write_text("mock exe")

    return {
        "exe_path": str(notepadpp_exe),
        "config_dir": str(mock_temp_directory / "notepadpp" / "config"),
        "plugins_dir": str(mock_temp_directory / "notepadpp" / "plugins"),
        "version": "8.5.0",
    }


@pytest.fixture
def mock_session_data():
    """Mock session data for testing."""
    return {
        "name": "test_session",
        "timestamp": 1640995200.0,  # 2022-01-01 00:00:00
        "files": ["test1.txt", "test2.py"],
        "active_file": "test1.txt",
        "is_modified": False,
    }


@pytest.fixture
def mock_tab_info():
    """Mock tab information."""
    return {
        "tabs": [
            {"filename": "test1.txt", "is_modified": False, "index": 0},
            {"filename": "test2.py", "is_modified": True, "index": 1},
        ],
        "active_tab": 0,
        "total_tabs": 2,
    }


@pytest.fixture
def mock_lint_results():
    """Mock linting results for different file types."""
    return {
        "python": {
            "success": True,
            "linter": "ruff",
            "issues": [
                {"type": "warning", "message": "unused import", "line": 1},
                {"type": "error", "message": "syntax error", "line": 10},
            ],
        },
        "javascript": {
            "success": True,
            "linter": "eslint",
            "issues": [{"type": "warning", "message": "missing semicolon", "line": 5}],
        },
        "json": {
            "success": True,
            "linter": "json_validator",
            "valid": True,
            "issues": [],
        },
        "markdown": {
            "success": True,
            "linter": "markdown_validator",
            "issues": [{"type": "warning", "message": "header hierarchy", "line": 3}],
        },
    }


@pytest.fixture
def mock_display_state():
    """Mock display state information."""
    return {
        "window_visible": True,
        "window_minimized": False,
        "theme": "default",
        "font_size": 10,
        "zoom_level": 100,
    }


@pytest.fixture
def comprehensive_mock_setup(
    mock_windows_api,
    mock_notepadpp_controller,
    mock_subprocess,
    mock_requests,
    mock_file_operations,
    mock_temp_directory,
):
    """Comprehensive mock setup for full integration testing."""
    return {
        "windows_api": mock_windows_api,
        "controller": mock_notepadpp_controller,
        "subprocess": mock_subprocess,
        "requests": mock_requests,
        "file_ops": mock_file_operations,
        "temp_dir": mock_temp_directory,
        "ready": True,
    }
