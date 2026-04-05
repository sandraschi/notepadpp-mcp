"""Persist named Notepad++ sessions as XML (compatible with File > Load Session / -openSession)."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Live session written by Notepad++ (may update during use; fully flushed on exit per user manual).
_SESSION_XML = "session.xml"


def live_session_xml_path() -> Path:
    """Path to Notepad++'s current session.xml (Roaming). Override: NOTEPADPP_LIVE_SESSION_XML."""
    env = os.environ.get("NOTEPADPP_LIVE_SESSION_XML", "").strip()
    if env:
        return Path(env)
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        raise OSError("APPDATA is not set; cannot locate Notepad++ session.xml")
    return Path(appdata) / "Notepad++" / _SESSION_XML


def session_storage_dir() -> Path:
    """Directory for named session copies ({name}.xml). Override: NOTEPADPP_SESSION_STORAGE_DIR."""
    env = os.environ.get("NOTEPADPP_SESSION_STORAGE_DIR", "").strip()
    if env:
        p = Path(env)
    else:
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            raise OSError("APPDATA is not set")
        p = Path(appdata) / "Notepad++" / "notepadpp-mcp-sessions"
    p.mkdir(parents=True, exist_ok=True)
    return p


_NAME_SAFE = re.compile(r"[^A-Za-z0-9._\-]+")


def sanitize_session_name(name: str) -> str:
    """Filesystem-safe stem for session file (no path separators)."""
    n = name.strip()
    n = _NAME_SAFE.sub("_", n).strip("._")
    if not n or n in (".", ".."):
        raise ValueError("Invalid session_name after sanitization")
    if len(n) > 120:
        n = n[:120]
    return n


def _atomic_write_bytes(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        suffix=".xml",
        dir=str(dest.parent),
        text=False,
    )
    try:
        os.write(fd, data)
        os.close(fd)
        fd = -1
        Path(tmp).replace(dest)
    except Exception:
        try:
            if fd >= 0:
                os.close(fd)
        except OSError:
            pass
        try:
            Path(tmp).unlink(missing_ok=True)  # type: ignore[call-arg]
        except OSError:
            pass
        raise


def parse_session_file_paths(xml_bytes: bytes) -> list[str]:
    """Collect `filename` attributes from File nodes (main and sub view)."""
    try:
        root = ET.fromstring(xml_bytes)  # noqa: S314 — parsed session files are local XML only
    except ET.ParseError:
        return []
    out: list[str] = []
    for el in root.iter():
        if el.tag.endswith("File") or el.tag == "File":
            fn = el.get("filename")
            if fn:
                out.append(fn)
    return out


def minimal_session_xml_for_files(absolute_paths: list[str]) -> bytes:
    """Build a minimal session.xml body Notepad++ can load (single MainView, empty SubView)."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        "<NotepadPlus>",
        '    <Session activeView="0">',
        '        <MainView activeIndex="0">',
    ]
    for p in absolute_paths:
        esc = (
            p.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        )
        parts.append(
            f'            <File firstVisibleLine="0" xOffset="0" scrollWidth="1" '
            f'startPos="0" endPos="0" selMode="0" offset="0" wrapCount="0" lang="None" '
            f'encoding="-1" userReadOnly="no" filename="{esc}" backupFilePath="" '
            f'originalFileLastModifTimestamp="-1" mapFileInitialScrollPos="2147483647" '
            f'mapFileInitialRange="-1" />'
        )
    parts.extend(
        [
            "        </MainView>",
            '        <SubView activeIndex="0" />',
            "    </Session>",
            "</NotepadPlus>",
        ]
    )
    return ("\n".join(parts) + "\n").encode("utf-8")


def read_live_session_bytes(max_attempts: int = 5, delay_s: float = 0.08) -> bytes:
    """Read session.xml; retry briefly if the file is temporarily locked."""
    path = live_session_xml_path()
    last_err: OSError | None = None
    for attempt in range(max_attempts):
        try:
            return path.read_bytes()
        except OSError as e:
            last_err = e
            if attempt < max_attempts - 1:
                time.sleep(delay_s)
    raise OSError(f"Cannot read {path}: {last_err}") from last_err


def save_named_session(
    name: str,
    *,
    fallback_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Copy live session.xml to storage as {sanitized_name}.xml. Optionally build from fallback_paths."""
    stem = sanitize_session_name(name)
    dest = session_storage_dir() / f"{stem}.xml"

    src_path = live_session_xml_path()
    paths: list[str] = []
    data: bytes = b""
    built_from_fallback = False

    if src_path.is_file():
        try:
            data = read_live_session_bytes()
            paths = parse_session_file_paths(data)
        except OSError:
            paths = []

    if not paths and fallback_paths:
        norm = [str(Path(p).resolve()) for p in fallback_paths if p and Path(p).is_file()]
        if not norm:
            raise ValueError(
                "No valid files for session snapshot (live session empty and no valid fallback paths)"
            )
        data = minimal_session_xml_for_files(norm)
        paths = norm
        built_from_fallback = True
    elif not paths:
        raise ValueError(
            "Could not read any files from the current Notepad++ session. "
            "Open files in Notepad++, or ensure session.xml exists and lists files "
            f"({src_path})."
        )

    _atomic_write_bytes(dest, data)
    return {
        "session_name": stem,
        "path": str(dest),
        "file_count": len(paths),
        "files": paths,
        "source": "fallback_paths" if built_from_fallback else "live_session_xml",
    }


def list_saved_sessions() -> list[dict[str, Any]]:
    """List persisted session XML files with size and file count inside each."""
    d = session_storage_dir()
    if not d.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for p in sorted(d.glob("*.xml"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            st = p.stat()
            raw = p.read_bytes()
            files = parse_session_file_paths(raw)
        except OSError:
            continue
        rows.append(
            {
                "name": p.stem,
                "path": str(p),
                "file_count": len(files),
                "files": files,
                "modified_utc": st.st_mtime,
                "size_bytes": st.st_size,
            }
        )
    return rows


def load_session_subprocess(session_name: str, notepad_exe: str) -> dict[str, Any]:
    """Launch Notepad++ with -openSession on a saved session file."""
    stem = sanitize_session_name(session_name)
    path = session_storage_dir() / f"{stem}.xml"
    if not path.is_file():
        raise FileNotFoundError(f"Saved session not found: {path}")

    # Case-sensitive flag per N++ manual
    cmd = [notepad_exe, "-openSession", str(path.resolve())]
    subprocess.Popen(cmd, shell=False, cwd=str(path.parent))  # noqa: S603
    return {"session_name": stem, "path": str(path.resolve()), "command": cmd}
