"""Read/write Notepad++ theme settings via %APPDATA%\\Notepad++\\config.xml (GUIConfig name=\"DarkMode\")."""

from __future__ import annotations

import os
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_CONFIG_NAME = "DarkMode"
_THEME_XML_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-]*\.xml$")


def config_xml_path() -> Path:
    """User config.xml (Roaming). Override with NOTEPADPP_CONFIG_XML."""
    env = os.environ.get("NOTEPADPP_CONFIG_XML", "").strip()
    if env:
        return Path(env)
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        raise OSError("APPDATA is not set; cannot locate Notepad++ config.xml")
    return Path(appdata) / "Notepad++" / "config.xml"


def install_dir(notepad_exe: str) -> Path:
    return Path(notepad_exe).resolve().parent


def list_theme_files(notepad_exe: str) -> list[str]:
    """Basenames of *.xml in the installation `themes` folder (e.g. DarkModeDefault.xml)."""
    tdir = install_dir(notepad_exe) / "themes"
    if not tdir.is_dir():
        return []
    names = sorted({p.name for p in tdir.glob("*.xml") if p.is_file()}, key=str.lower)
    return names


def _load_tree(path: Path) -> ET.ElementTree:
    if not path.is_file():
        raise FileNotFoundError(f"config.xml not found: {path}")
    try:
        tree = ET.parse(path)  # noqa: S314 — local user config.xml path only
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in {path}: {e}") from e
    root = tree.getroot()
    if root.tag != "NotepadPlus":
        raise ValueError("config.xml root must be <NotepadPlus>")
    return tree


def _get_or_create_dark_node(root: ET.Element) -> ET.Element:
    gui = root.find("GUIConfigs")
    if gui is None:
        gui = ET.SubElement(root, "GUIConfigs")
    for child in gui.findall("GUIConfig"):
        if child.get("name") == _CONFIG_NAME:
            return child
    el = ET.SubElement(gui, "GUIConfig")
    el.set("name", _CONFIG_NAME)
    el.set("enable", "no")
    el.set("colorTone", "0")
    el.set("darkThemeName", "DarkModeDefault.xml")
    el.set("lightThemeName", "")
    return el


def read_theme_state(config_path: Path | None = None) -> dict[str, Any]:
    """Return current DarkMode GUIConfig fields + config path."""
    path = config_path or config_xml_path()
    tree = _load_tree(path)
    root = tree.getroot()
    gui = root.find("GUIConfigs")
    dark: ET.Element | None = None
    if gui is not None:
        for child in gui.findall("GUIConfig"):
            if child.get("name") == _CONFIG_NAME:
                dark = child
                break
    if dark is None:
        return {
            "config_path": str(path),
            "dark_mode_configured": False,
            "dark_mode_enabled": False,
            "color_tone": 0,
            "dark_theme_name": "DarkModeDefault.xml",
            "light_theme_name": "",
            "raw_attributes": {},
        }
    raw = dict(dark.attrib)
    en = (dark.get("enable") or "no").strip().lower()
    dark_on = en in ("yes", "true", "1")
    try:
        tone = int(dark.get("colorTone") or "0")
    except ValueError:
        tone = 0
    return {
        "config_path": str(path),
        "dark_mode_configured": True,
        "dark_mode_enabled": dark_on,
        "color_tone": tone,
        "dark_theme_name": (dark.get("darkThemeName") or "DarkModeDefault.xml").strip()
        or "DarkModeDefault.xml",
        "light_theme_name": (dark.get("lightThemeName") or "").strip(),
        "raw_attributes": raw,
    }


def _validate_theme_basename(name: str, notepad_exe: str) -> str:
    n = name.strip()
    if not n:
        raise ValueError("theme_xml is empty")
    if not _THEME_XML_RE.match(n):
        raise ValueError(
            "theme_xml must be a safe .xml basename (letters, digits, ._-), e.g. Solarized.xml"
        )
    if n.lower() == "stylers.xml":
        return n
    available = {x.lower() for x in list_theme_files(notepad_exe)}
    if n.lower() not in available:
        all_t = list_theme_files(notepad_exe)
        raise ValueError(
            f"Theme file not found in Notepad++ themes folder: {n}. "
            f"Available: {', '.join(all_t[:40])}"
            + (" …" if len(all_t) > 40 else "")
        )
    return n


def patch_config_xml(
    notepad_exe: str,
    *,
    dark_mode_enabled: bool | None = None,
    dark_theme_name: str | None = None,
    light_theme_name: str | None = None,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """
    Merge settings into GUIConfig name=DarkMode and atomically replace config.xml.

    Notepad++ applies changes on next start; if it is running it may overwrite config on exit.
    """
    path = config_path or config_xml_path()
    tree = _load_tree(path)
    root = tree.getroot()
    node = _get_or_create_dark_node(root)

    before = {k: node.get(k) for k in node.keys()}

    if dark_mode_enabled is not None:
        node.set("enable", "yes" if dark_mode_enabled else "no")

    if dark_theme_name is not None:
        dt = _validate_theme_basename(dark_theme_name, notepad_exe)
        node.set("darkThemeName", dt)

    if light_theme_name is not None:
        lt = light_theme_name.strip()
        if lt == "":
            node.set("lightThemeName", "")
        else:
            node.set("lightThemeName", _validate_theme_basename(lt, notepad_exe))

    after = {k: node.get(k) for k in node.keys()}

    _atomic_write_tree(tree, path)
    return {
        "config_path": str(path),
        "updated": True,
        "before": before,
        "after": after,
        "restart_required": True,
        "note": "Close Notepad++ before changing, or restart it after saving so it does not overwrite config.xml on exit.",
    }


def _atomic_write_tree(tree: ET.ElementTree, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix="npp_config_", suffix=".xml", dir=str(path.parent), text=False
    )
    tmp_path = Path(tmp)
    try:
        os.close(fd)
        tree.write(
            tmp_path,
            encoding="utf-8",
            xml_declaration=True,
        )
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def theme_status_payload(notepad_exe: str, config_path: Path | None = None) -> dict[str, Any]:
    """Combined state for display_ops theme_status."""
    path = config_path or config_xml_path()
    themes = list_theme_files(notepad_exe)
    try:
        state = read_theme_state(path)
    except (OSError, ValueError, FileNotFoundError) as e:
        return {
            "success": False,
            "error": str(e),
            "config_path": str(path),
            "themes_dir": str(install_dir(notepad_exe) / "themes"),
            "theme_files": themes,
        }
    return {
        "success": True,
        "config_path": state["config_path"],
        "themes_dir": str(install_dir(notepad_exe) / "themes"),
        "theme_files": themes,
        "dark_mode_enabled": state["dark_mode_enabled"],
        "dark_theme_name": state["dark_theme_name"],
        "light_theme_name": state["light_theme_name"],
        "color_tone": state["color_tone"],
        "active_editor_theme": state["dark_theme_name"]
        if state["dark_mode_enabled"]
        else (state["light_theme_name"] or "stylers.xml (default)"),
        "hint": "Use set_dark_mode / set_editor_theme, then restart Notepad++ (avoid running N++ while editing config).",
    }
