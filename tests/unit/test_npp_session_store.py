"""Tests for Notepad++ session XML persistence helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest

from notepadpp_mcp import npp_session_store

SAMPLE_SESSION = b"""<?xml version="1.0" encoding="UTF-8" ?>
<NotepadPlus>
    <Session activeView="0">
        <MainView activeIndex="0">
            <File filename="C:/a/one.txt" />
            <File filename="D:/b/two.txt" />
        </MainView>
        <SubView activeIndex="0" />
    </Session>
</NotepadPlus>
"""


def test_sanitize_session_name() -> None:
    assert npp_session_store.sanitize_session_name("  my-work  ") == "my-work"
    assert npp_session_store.sanitize_session_name("a" * 200) == "a" * 120
    with pytest.raises(ValueError):
        npp_session_store.sanitize_session_name("..")


def test_parse_session_file_paths() -> None:
    paths = npp_session_store.parse_session_file_paths(SAMPLE_SESSION)
    assert paths == ["C:/a/one.txt", "D:/b/two.txt"]


def test_minimal_session_xml_roundtrip() -> None:
    xml = npp_session_store.minimal_session_xml_for_files([r"C:\tmp\z.txt"])
    paths = npp_session_store.parse_session_file_paths(xml)
    assert paths == [r"C:\tmp\z.txt"]
    ET.fromstring(xml)  # noqa: S314 — test fixture


def test_save_named_session_from_live(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = tmp_path / "store"
    live = tmp_path / "session.xml"
    live.write_bytes(SAMPLE_SESSION)
    monkeypatch.setenv("NOTEPADPP_SESSION_STORAGE_DIR", str(store))
    monkeypatch.setenv("NOTEPADPP_LIVE_SESSION_XML", str(live))

    out = npp_session_store.save_named_session("demo")
    assert out["session_name"] == "demo"
    assert out["file_count"] == 2
    assert out["source"] == "live_session_xml"
    saved = store / "demo.xml"
    assert saved.is_file()
    assert npp_session_store.parse_session_file_paths(saved.read_bytes()) == [
        "C:/a/one.txt",
        "D:/b/two.txt",
    ]


def test_save_named_session_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = tmp_path / "store"
    f = tmp_path / "only.txt"
    f.write_text("x", encoding="utf-8")
    monkeypatch.setenv("NOTEPADPP_SESSION_STORAGE_DIR", str(store))
    # Point live session at a non-existent file so we exercise fallback, not real %APPDATA%.
    monkeypatch.setenv("NOTEPADPP_LIVE_SESSION_XML", str(tmp_path / "missing_session.xml"))

    out = npp_session_store.save_named_session("fb", fallback_paths=[str(f)])
    assert out["source"] == "fallback_paths"
    assert out["file_count"] == 1
    assert str(f.resolve()) in out["files"][0] or out["files"][0].endswith("only.txt")


def test_list_saved_sessions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = tmp_path / "store"
    store.mkdir()
    (store / "a.xml").write_bytes(SAMPLE_SESSION)
    monkeypatch.setenv("NOTEPADPP_SESSION_STORAGE_DIR", str(store))
    rows = npp_session_store.list_saved_sessions()
    assert len(rows) == 1
    assert rows[0]["name"] == "a"
    assert rows[0]["file_count"] == 2


def test_load_session_subprocess(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = tmp_path / "store"
    store.mkdir()
    (store / "x.xml").write_bytes(SAMPLE_SESSION)
    monkeypatch.setenv("NOTEPADPP_SESSION_STORAGE_DIR", str(store))
    with patch("notepadpp_mcp.npp_session_store.subprocess.Popen") as popen:
        out = npp_session_store.load_session_subprocess("x", r"C:\npp\notepad++.exe")
    assert out["session_name"] == "x"
    popen.assert_called_once()
    args = popen.call_args[0][0]
    assert args[0] == r"C:\npp\notepad++.exe"
    assert args[1] == "-openSession"
    assert args[2].endswith("x.xml")
