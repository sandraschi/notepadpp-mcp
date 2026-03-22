"""Live Notepad++ snapshot and on-disk plugin enumeration for the HTTP dashboard."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from .tools.controller import NotepadPPController

# Skip counting lines for huge files (read into memory cap)
_MAX_STATS_BYTES = 8_000_000


def _plugin_search_roots(notepad_exe: str) -> list[Path]:
    roots: list[Path] = []
    base = Path(notepad_exe).resolve().parent
    roots.append(base / "plugins")
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        roots.append(Path(appdata) / "Notepad++" / "plugins")
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        roots.append(Path(local) / "Notepad++" / "plugins")
    return roots


def list_installed_plugins_disk(notepad_exe: str) -> dict[str, Any]:
    """List plugin DLLs under standard Notepad++ plugin directories (filesystem, not menu parsing)."""
    roots = _plugin_search_roots(notepad_exe)
    checked: list[str] = []
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    skip_stems = {"config", "libcurl", "dbghelp", "msvcp", "vcruntime"}

    for root in roots:
        if not root.is_dir():
            continue
        checked.append(str(root))
        for dll in root.rglob("*.dll"):
            stem = dll.stem.lower()
            if stem in skip_stems:
                continue
            if stem in seen:
                continue
            seen.add(stem)
            found.append(
                {
                    "name": dll.stem,
                    "path": str(dll),
                    "directory": str(dll.parent),
                }
            )

    found.sort(key=lambda x: x["name"].lower())
    return {
        "count": len(found),
        "plugins": found,
        "roots_scanned": checked,
    }


def _tool_result_payload(result: Any) -> dict[str, Any]:
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        return sc
    return {"raw": str(result)}


def normalize_title_filename(filename: str) -> str:
    """Strip Notepad++ modified prefix like '* ' from the title-derived name."""
    fn = filename.strip()
    while fn.startswith("*"):
        fn = fn[1:].strip()
    return fn.strip() or "Untitled"


def try_resolve_path_from_hint(filename_hint: str) -> str | None:
    """If the active tab title encodes a real path that exists on disk, return absolute path."""
    fn = normalize_title_filename(filename_hint)
    if fn in ("", "Untitled"):
        return None
    # Full Windows/UNC path in title
    if len(fn) >= 2 and fn[1] == ":":
        p = Path(fn)
        if p.is_file():
            return str(p.resolve())
    if fn.startswith("\\\\"):
        p = Path(fn)
        if p.is_file():
            return str(p.resolve())
    # Relative to cwd
    rel = Path(fn)
    if rel.is_file():
        return str(rel.resolve())
    return None


def file_stats_for_path(path: str) -> dict[str, Any]:
    """Size, mtime, line count (if file is small enough), extension."""
    p = Path(path)
    out: dict[str, Any] = {
        "path": str(p.resolve()),
        "exists": p.is_file(),
        "extension": p.suffix.lower() if p.suffix else "",
        "name": p.name,
    }
    if not p.is_file():
        out["error"] = "not_a_file"
        return out

    st = p.stat()
    out["size_bytes"] = st.st_size
    out["modified_utc"] = datetime.fromtimestamp(st.st_mtime, tz=UTC).isoformat()

    if st.st_size > _MAX_STATS_BYTES:
        out["line_count"] = None
        out["line_count_note"] = f"skipped (file > {_MAX_STATS_BYTES} bytes)"
        return out

    try:
        data = p.read_bytes()
    except OSError as e:
        out["read_error"] = str(e)
        return out

    if not data:
        out["line_count"] = 0
    else:
        out["line_count"] = data.count(b"\n") + (0 if data.endswith(b"\n") else 1)

    out["char_count"] = len(data.decode("utf-8", errors="replace"))
    return out


async def build_editor_snapshot(
    mcp_app: FastMCP,
    controller: NotepadPPController | None,
) -> dict[str, Any]:
    """Window title, tab hint from tab_ops, process id, and plugins on disk."""
    if controller is None:
        return {
            "connected": False,
            "reason": "windows_api_unavailable",
            "message": "Controller requires Windows and pywin32.",
        }

    try:
        await controller.ensure_notepadpp_running()
    except Exception as e:
        return {
            "connected": False,
            "reason": "notepad_unreachable",
            "error": str(e),
            "executable": controller.notepadpp_exe,
        }

    window_title = await controller.get_window_text(controller.hwnd)
    filename = "Untitled"
    is_modified = False
    if " - Notepad++" in window_title:
        filename = window_title.split(" - Notepad++")[0]
    if "*" in window_title:
        is_modified = True

    display_name = normalize_title_filename(filename)
    resolved_path = try_resolve_path_from_hint(filename)
    file_stats: dict[str, Any] | None = None
    if resolved_path:
        file_stats = file_stats_for_path(resolved_path)

    tab_tool: dict[str, Any] = {}
    try:
        tr = await mcp_app.call_tool("tab_ops", {"operation": "list"})
        tab_tool = _tool_result_payload(tr)
    except Exception as e:
        tab_tool = {"success": False, "error": str(e)}

    pid: int | None = None
    try:
        import psutil

        exe_lower = str(controller.notepadpp_exe).lower()
        for proc in psutil.process_iter(["pid", "exe"]):
            try:
                pexe = (proc.info.get("exe") or "").lower()
                if not pexe:
                    continue
                if pexe == exe_lower or pexe.endswith("notepad++.exe"):
                    pid = int(proc.info["pid"])
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass

    plugins_disk = list_installed_plugins_disk(controller.notepadpp_exe)

    return {
        "connected": True,
        "executable": controller.notepadpp_exe,
        "pid": pid,
        "hwnd": int(controller.hwnd) if controller.hwnd else None,
        "scintilla_hwnd": int(controller.scintilla_hwnd) if controller.scintilla_hwnd else None,
        "window_title": window_title,
        "active_file_hint": filename,
        "active_file_display_name": display_name,
        "is_modified_hint": is_modified,
        "resolved_path": resolved_path,
        "file_stats": file_stats,
        "tab_ops": tab_tool,
        "plugins_on_disk": plugins_disk,
    }
