"""Notepad++ MCP Server package."""

__version__ = "0.1.0"
__author__ = "Sandra"
__email__ = "sandra@example.com"
__description__ = "MCP Server for Notepad++ automation and control"

from .tools.server import app

__all__ = ["app"]
