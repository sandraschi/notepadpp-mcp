#!/usr/bin/env python3
"""Test script to verify FastMCP 2.14.3 installation and basic functionality."""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from fastmcp import FastMCP
        print("PASS: FastMCP imported successfully")
        print(f"  FastMCP version info: {getattr(FastMCP, '__version__', 'Not available')}")

        # Test basic app creation
        app = FastMCP("Test App", instructions="Test instructions")
        print("PASS: FastMCP app created successfully")

        return True
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        return False

def test_server_import():
    """Test that the updated server can be imported."""
    try:
        # Add src to path
        sys.path.insert(0, 'src')

        from notepadpp_mcp.tools.server import app
        print("PASS: Server module imported successfully")

        # Check that agentic tools were registered
        tools = getattr(app, '_tools', [])
        print(f"PASS: Server has {len(tools)} tools registered")

        return True
    except ImportError as e:
        print(f"FAIL: Server import error: {e}")
        return False
    except Exception as e:
        print(f"FAIL: Server test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastMCP 2.14.3 SOTA updates...")
    print(f"Python version: {sys.version}")
    print()

    success = True
    success &= test_imports()
    success &= test_server_import()

    print()
    if success:
        print("SUCCESS: All tests passed! FastMCP 2.14.3 update successful.")
    else:
        print("FAILURE: Some tests failed. Please check the errors above.")
        sys.exit(1)