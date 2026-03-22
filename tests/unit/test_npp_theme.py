"""Tests for npp_theme config.xml helpers (no real Notepad++ required)."""

from __future__ import annotations

from pathlib import Path

import pytest

from notepadpp_mcp import npp_theme

MINIMAL_CONFIG = """<?xml version='1.0' encoding='utf-8'?>
<NotepadPlus>
  <GUIConfigs>
    <GUIConfig name="DarkMode" enable="no" colorTone="0"
      darkThemeName="DarkModeDefault.xml" lightThemeName="" />
  </GUIConfigs>
</NotepadPlus>
"""


def test_read_theme_state_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "config.xml"
    cfg.write_text(MINIMAL_CONFIG, encoding="utf-8")
    monkeypatch.setenv("NOTEPADPP_CONFIG_XML", str(cfg))
    st = npp_theme.read_theme_state()
    assert st["dark_mode_enabled"] is False
    assert st["dark_theme_name"] == "DarkModeDefault.xml"


def test_patch_dark_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "config.xml"
    cfg.write_text(MINIMAL_CONFIG, encoding="utf-8")
    monkeypatch.setenv("NOTEPADPP_CONFIG_XML", str(cfg))
    inst = tmp_path / "npp"
    inst.mkdir()
    (inst / "notepad++.exe").write_bytes(b"")
    themes = inst / "themes"
    themes.mkdir()
    (themes / "DarkModeDefault.xml").write_bytes(b"<t/>")
    (themes / "Zenburn.xml").write_bytes(b"<t/>")
    exe = str(inst / "notepad++.exe")
    out = npp_theme.patch_config_xml(exe, dark_mode_enabled=True, config_path=cfg)
    assert out["updated"] is True
    st = npp_theme.read_theme_state(cfg)
    assert st["dark_mode_enabled"] is True


def test_set_light_theme_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "config.xml"
    cfg.write_text(MINIMAL_CONFIG, encoding="utf-8")
    monkeypatch.setenv("NOTEPADPP_CONFIG_XML", str(cfg))
    inst = tmp_path / "npp"
    inst.mkdir()
    (inst / "notepad++.exe").write_bytes(b"")
    themes = inst / "themes"
    themes.mkdir()
    (themes / "Zenburn.xml").write_bytes(b"<t/>")
    exe = str(inst / "notepad++.exe")
    npp_theme.patch_config_xml(exe, light_theme_name="Zenburn.xml", config_path=cfg)
    st = npp_theme.read_theme_state(cfg)
    assert st["light_theme_name"] == "Zenburn.xml"
