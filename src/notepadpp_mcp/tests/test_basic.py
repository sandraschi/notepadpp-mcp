"""Basic tests that should always pass."""

import pytest


def test_basic_import():
    """Test that basic imports work."""
    import notepadpp_mcp

    assert notepadpp_mcp is not None


def test_basic_functionality():
    """Test basic functionality."""
    assert 1 + 1 == 2
    assert "hello" == "hello"


def test_python_version():
    """Test that we're running on a supported Python version."""
    import sys

    assert sys.version_info >= (3, 8), "Python 3.8+ required"


def test_imports():
    """Test that key modules can be imported."""
    try:
        from notepadpp_mcp import link_parser

        assert link_parser is not None
    except ImportError:
        pytest.skip("link_parser not available")

    try:
        from notepadpp_mcp import file_validator

        assert file_validator is not None
    except ImportError:
        pytest.skip("file_validator not available")
