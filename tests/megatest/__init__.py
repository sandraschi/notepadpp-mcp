"""
Notepad++ MCP Megatest Framework

Multi-level testing framework for Notepad++ MCP server with safety guarantees.

Levels:
- Level 1: Smoke Test - Quick sanity check (2 min)
- Level 2: Standard Test - Core functionality (10 min)
- Level 3: Advanced Test - Advanced features (20 min)
- Level 4: Integration Test - Multi-tool workflows (45 min)
- Level 5: Full Blast Test - Complete validation (90 min)

Safety Features:
- Isolated test environments (never touches production data)
- Production path detection and blocking
- Automatic cleanup of test artifacts
- Comprehensive mocking for CI environments

Usage:
    # Run smoke tests
    python scripts/run_megatest.py smoke

    # Run standard tests
    python scripts/run_megatest.py standard

    # Run all levels
    python scripts/run_megatest.py all

    # Run with Notepad++ (if available)
    python scripts/run_megatest.py standard --with-notepadpp
"""

__version__ = "1.0.0"
__description__ = "Multi-level testing framework for Notepad++ MCP server"
