"""Notepad++ MCP Server package (FastMCP 3.1)."""

__version__ = "0.2.0"
__author__ = "Sandra"
__email__ = "sandra@example.com"
__description__ = "MCP Server for Notepad++ automation and control"

from .server import mcp as app

__all__ = ["app"]
