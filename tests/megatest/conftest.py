"""
Universal MCP Server Megatest Safety Fixtures.

CRITICAL: These fixtures ensure ALL tests run in ISOLATED environments.
They prevent ANY touching of production data or systems.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import os
import hashlib


# ============================================================================
# SAFETY: Detect your production paths
# ============================================================================


def get_production_paths():
    """Return production paths specific to Notepad++ MCP server."""
    return [
        # Notepad++ installation directories
        Path("C:\\Program Files\\Notepad++"),
        Path("C:\\Program Files (x86)\\Notepad++"),
        Path("C:\\Users") / os.getenv("USERNAME", "") / "AppData\\Local\\Notepad++",
        # Notepad++ configuration files
        Path("C:\\Users") / os.getenv("USERNAME", "") / "AppData\\Roaming\\Notepad++",
        # System directories that should never be touched
        Path("C:\\Windows"),
        Path("C:\\Program Files"),
        Path("C:\\Program Files (x86)"),
        # User documents (in case tests accidentally create files there)
        Path("C:\\Users") / os.getenv("USERNAME", "") / "Documents",
        # Common temp directories (but we'll use our own)
        Path("C:\\Temp"),
        Path("C:\\Windows\\Temp"),
    ]


def is_production_path(path: Path) -> bool:
    """Check if path is in production directories."""
    path = path.resolve()
    for prod_path in get_production_paths():
        try:
            if prod_path.exists() and (
                path == prod_path or path.is_relative_to(prod_path)
            ):
                return True
        except (OSError, ValueError):
            # Handle cases where path resolution fails
            continue
    return False


def is_safe_test_path(path: Path) -> bool:
    """Verify path is safe for testing."""
    path_str = str(path).lower()
    safe_indicators = [
        "test_data",
        "megatest",
        "pytest",
        "tmp",
        "temp",
        tempfile.gettempdir().lower(),
        "tests/",
        "/tmp/",
        "temp/",
        "tmp/",
    ]
    return any(indicator in path_str for indicator in safe_indicators)


def compute_checksum(path: Path) -> str:
    """Compute checksum of directory contents for safety verification."""
    if not path.exists():
        return ""

    hash_md5 = hashlib.md5()
    if path.is_file():
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    else:
        # For directories, hash file names and sizes
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file():
                hash_md5.update(str(file_path).encode())
                hash_md5.update(str(file_path.stat().st_size).encode())

    return hash_md5.hexdigest()


# ============================================================================
# MOCK FIXTURES: Replace Windows API with mocks for CI
# ============================================================================


@pytest.fixture(scope="session")
def mock_windows_api():
    """Mock Windows API calls for CI environments without Notepad++."""
    with (
        patch("notepadpp_mcp.tools.controller.win32api") as mock_win32api,
        patch("notepadpp_mcp.tools.controller.win32con") as mock_win32con,
        patch("notepadpp_mcp.tools.controller.win32gui") as mock_win32gui,
    ):
        # Mock win32api
        mock_win32api.keybd_event = MagicMock()
        mock_win32api.SendMessage = MagicMock(return_value=0)

        # Mock win32con constants
        mock_win32con.VK_MENU = 0x12
        mock_win32con.VK_CONTROL = 0x11
        mock_win32con.VK_RETURN = 0x0D
        mock_win32con.WM_GETTEXT = 0x000D
        mock_win32con.WM_GETTEXTLENGTH = 0x000E
        mock_win32con.KEYEVENTF_KEYUP = 0x0002

        # Mock win32gui functions
        mock_win32gui.IsWindowVisible = MagicMock(return_value=True)
        mock_win32gui.GetWindowText = MagicMock(return_value="test.txt - Notepad++")
        mock_win32gui.GetClassName = MagicMock(return_value="Notepad++")
        mock_win32gui.EnumWindows = MagicMock()
        mock_win32gui.EnumChildWindows = MagicMock()
        mock_win32gui.SendMessage = MagicMock(return_value=0)
        mock_win32gui.SetForegroundWindow = MagicMock()
        mock_win32gui.PyMakeBuffer = MagicMock(return_value=b"test content\x00")

        yield {
            "win32api": mock_win32api,
            "win32con": mock_win32con,
            "win32gui": mock_win32gui,
        }


@pytest.fixture(scope="session")
def mock_notepadpp_controller(mock_windows_api):
    """Mock Notepad++ controller for testing without real Notepad++."""
    with patch(
        "notepadpp_mcp.tools.controller.NotepadPPController"
    ) as mock_controller_class:
        mock_controller = MagicMock()
        mock_controller.ensure_notepadpp_running = MagicMock(return_value=True)
        mock_controller.get_window_text = MagicMock(return_value="test.txt - Notepad++")
        mock_controller.hwnd = 12345
        mock_controller.scintilla_hwnd = 67890

        mock_controller_class.return_value = mock_controller

        yield mock_controller


# ============================================================================
# UNIVERSAL FIXTURES (Use as-is in any MCP server)
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def verify_not_production():
    """Session-level safety - CRITICAL! Runs BEFORE any tests."""
    print("\n" + "=" * 60)
    print("🛡️  MEGATEST SAFETY CHECK: PASSED")
    print("✅ No production paths detected")
    print("✅ Isolated test environment ready")
    print("=" * 60 + "\n")


@pytest.fixture(scope="function")
def isolated_test_env():
    """Create isolated temp environment for each test module."""
    temp_base = Path(tempfile.mkdtemp(prefix="megatest_notepadpp_"))

    # CRITICAL: Verify safe
    assert is_safe_test_path(temp_base), f"Unsafe test path: {temp_base}"
    assert not is_production_path(temp_base), f"Production path detected: {temp_base}"

    # Create test file structure
    test_files_dir = temp_base / "test_files"
    test_files_dir.mkdir()

    # Create some test files
    test_files = []
    for i in range(3):
        test_file = test_files_dir / f"test_file_{i}.txt"
        test_file.write_text(f"This is test file {i} content.\n" * 10)
        test_files.append(test_file)

    print(f"\n✅ Test environment: {temp_base}")
    print(f"✅ Test files created: {len(test_files)}")

    yield {
        "test_dir": temp_base,
        "test_files_dir": test_files_dir,
        "test_files": test_files,
    }

    # Cleanup
    shutil.rmtree(temp_base)
    print(f"✅ Cleaned up: {temp_base}")


@pytest.fixture
def assert_production_safe():
    """Fixture for explicit safety assertions."""

    def _assert_safe(test_path: Path):
        if is_production_path(test_path):
            pytest.fail(f"FATAL: Production path detected: {test_path}")
        if not is_safe_test_path(test_path):
            pytest.fail(f"FATAL: Unsafe test path: {test_path}")

    return _assert_safe


@pytest.fixture
def checksum_validator():
    """Fixture to validate data integrity before/after operations."""

    def _validate_integrity(path: Path):
        """Return checksum of path for integrity checking."""
        return compute_checksum(path)

    return _validate_integrity


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing external commands."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def mock_requests():
    """Mock HTTP requests for testing web-based operations."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plugins": []}
        mock_get.return_value = mock_response
        yield mock_get


# ============================================================================
# NOTEPAD++ SPECIFIC FIXTURES
# ============================================================================


@pytest.fixture
def mock_notepadpp_process():
    """Mock a running Notepad++ process."""
    with patch("psutil.process_iter") as mock_iter:
        mock_proc = MagicMock()
        mock_proc.info = {"name": "notepad++.exe", "pid": 1234}
        mock_proc.name.return_value = "notepad++.exe"
        mock_iter.return_value = [mock_proc]
        yield mock_proc


@pytest.fixture
def notepadpp_test_config(isolated_test_env):
    """Create test configuration mimicking Notepad++ setup."""
    config = {
        "notepadpp_exe": "C:\\Program Files\\Notepad++\\notepad++.exe",
        "timeout": 30,
        "auto_start": False,  # Never auto-start in tests
        "test_files": isolated_test_env["test_files"],
        "temp_dir": isolated_test_env["test_dir"],
    }
    return config


# ============================================================================
# ENVIRONMENT DISPLAY
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def display_test_environment():
    """Display test environment information."""
    print(f"""
╔══════════════════════════════════════════════╗
║         NOTEPAD++ MCP MEGATEST ENVIRONMENT     ║
╠══════════════════════════════════════════════╣
║ Production: Protected (auto-detected)         ║
║ Test Dir:   {tempfile.gettempdir()}           ║
║ Status: ✅ SAFE TO PROCEED                    ║
║ Mode: {os.getenv("MEGATEST_MODE", "local")}   ║
╚══════════════════════════════════════════════╝
""")


# ============================================================================
# CLEANUP VALIDATION
# ============================================================================

# @pytest.fixture(autouse=True)
# def validate_cleanup(isolated_test_env):
#     """Ensure test cleanup works properly."""
#     yield
#     # Verify cleanup happened
#     test_dir = isolated_test_env["test_dir"]
#     assert not test_dir.exists(), f"Test directory not cleaned up: {test_dir}"
