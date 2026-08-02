"""
Automation Operations Portmanteau Tool

Consolidates Notepad++ automation helpers (macro list/play) into one tool.
"""

import os
import subprocess
from pathlib import Path
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field


def _macro_dirs(exe_path: str | None) -> list[Path]:
    """Locate Notepad++ macro directories (roaming + portable beside the exe)."""
    dirs: list[Path] = []
    appdata = os.getenv("APPDATA", "")
    if appdata:
        dirs.append(Path(appdata) / "Notepad++" / "macros")
    if exe_path:
        dirs.append(Path(exe_path).parent / "macros")
    return [d for d in dirs if d.is_dir()]


def _list_macros(exe_path: str | None) -> list[dict[str, str]]:
    """Enumerate saved macro XML files (name -> absolute path)."""
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for d in _macro_dirs(exe_path):
        for xml in sorted(d.glob("*.xml")):
            if xml.stem in seen:
                continue
            seen.add(xml.stem)
            found.append({"name": xml.stem, "path": str(xml)})
    return found


class AutomationOperationsTool:
    """Portmanteau tool for Notepad++ automation helpers (macros)."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the automation operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register the automation operations portmanteau tool."""

        @self.app.tool()
        async def automation_ops(
            operation: Annotated[
                Literal["macro_list", "macro_play"],
                Field(
                    description=(
                        "Operation: macro_list enumerates saved Notepad++ macros "
                        "(macro XML files), macro_play runs a saved macro by name via the CLI."
                    )
                ),
            ],
            name: Annotated[str | None, Field(description="Macro name for macro_play (from macro_list).")] = None,
        ) -> dict[str, Any]:
            """AUTOMATION_OPS — List and run saved Notepad++ macros.

            PORTMANTEAU PATTERN RATIONALE: Groups macro automation under one entry point
            (TOOL_DESIGN_STANDARDS.md §1).

            Operations:
            - macro_list: List saved macros (name + path) from the macros folders.
            - macro_play: Run a saved macro by name via `notepad++.exe -macro:<path>`.

            ## Return Format
            {"success": bool, "operation": str, "message": str, "result": {"macros": [...], "macro_path": str}, "error": str | null}

            ## Examples
            automation_ops(operation="macro_list")
            automation_ops(operation="macro_play", name="Format-Python")

            Notes:
             - macro_play launches the macro through the Notepad++ CLI; the editor must be running and the macro file must exist (create macros via Notepad++ Macro > Record).
             - Recording macros is not supported (use Notepad++'s recorder); only playback of existing macros.
            """
            exe = self.controller.notepadpp_exe if self.controller else os.getenv("NOTEPADPP_PATH")

            if operation == "macro_list":
                macros = _list_macros(exe)
                return {
                    "success": True,
                    "operation": operation,
                    "summary": f"Found {len(macros)} saved macro(s)",
                    "result": {"macros": macros, "count": len(macros)},
                    "next_steps": ["automation_ops(operation='macro_play', name=...) to run one"],
                }

            if operation == "macro_play":
                if not name:
                    return {
                        "success": False,
                        "error": "missing_name",
                        "operation": operation,
                        "summary": "macro_play requires the macro name",
                        "recovery_options": ["Run automation_ops(operation='macro_list') to see available names"],
                    }
                macros = _list_macros(exe)
                target = next((m for m in macros if m["name"].lower() == name.lower()), None)
                if not target:
                    return {
                        "success": False,
                        "error": "macro_not_found",
                        "operation": operation,
                        "summary": f"Macro '{name}' not found",
                        "result": {"available": [m["name"] for m in macros]},
                        "recovery_options": [
                            "Pick a name from macro_list output",
                            "Record the macro in Notepad++ first",
                        ],
                    }
                if not exe:
                    return {
                        "success": False,
                        "error": "notepadpp_not_found",
                        "operation": operation,
                        "summary": "Notepad++ executable not found",
                        "recovery_options": ["Set NOTEPADPP_PATH"],
                    }
                subprocess.Popen(
                    [exe, f"-macro:{target['path']}"],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return {
                    "success": True,
                    "operation": operation,
                    "summary": f"Macro '{target['name']}' launched via CLI",
                    "result": {"macro_path": target["path"], "launched": True},
                    "next_steps": ["Check the editor for the macro's effect"],
                }

            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "operation": operation,
                "summary": f"Unknown automation operation '{operation}'",
                "recovery_options": ["Use 'macro_list' or 'macro_play'"],
            }
