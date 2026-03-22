"""Unit tests for plugin_catalog (matching + one-line descriptions)."""

from notepadpp_mcp.plugin_catalog import (
    build_catalog_indexes,
    match_catalog_entry,
    one_line_description,
    parse_plugins_array,
)


def test_parse_plugins_array_npp_plugins_list() -> None:
    raw = {"npp-plugins": [{"folder-name": "X", "display-name": "Y"}]}
    assert len(parse_plugins_array(raw)) == 1


def test_parse_plugins_array_legacy_plugins_key() -> None:
    raw = {"plugins": [{"folder-name": "A"}]}
    assert len(parse_plugins_array(raw)) == 1


def test_one_line_description_multiline() -> None:
    s = "First line\r\nSecond line"
    assert one_line_description(s) == "First line"


def test_one_line_description_long() -> None:
    s = "x" * 300
    out = one_line_description(s, max_len=50)
    assert len(out) <= 50
    assert out.endswith("…")


def test_match_by_folder_name() -> None:
    plugins = [
        {
            "folder-name": "XMLTools",
            "display-name": "XML Tools",
            "description": "Hello",
        }
    ]
    by_f, by_c = build_catalog_indexes(plugins)
    m = match_catalog_entry("XMLTools", by_f, by_c)
    assert m is not None
    assert m["display-name"] == "XML Tools"


def test_match_compact_spacing() -> None:
    plugins = [{"folder-name": "My Plugin", "display-name": "MP"}]
    by_f, by_c = build_catalog_indexes(plugins)
    m = match_catalog_entry("MyPlugin", by_f, by_c)
    assert m is not None
    assert m["display-name"] == "MP"
