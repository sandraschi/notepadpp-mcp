"""Official nppPluginList (pl.x64.json) fetch, cache, and merge with on-disk plugin DLL names."""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

from .editor_bridge import list_installed_plugins_disk

# Upstream moved from pluginList.json to arch-specific pl.*.json
DEFAULT_PLUGIN_LIST_URL = (
    "https://raw.githubusercontent.com/notepad-plus-plus/nppPluginList/master/src/pl.x64.json"
)

_CACHE_LOCK = threading.Lock()
_cached_plugins: list[dict[str, Any]] | None = None
_cached_at: float = 0.0
_CACHE_TTL_SEC = float(os.environ.get("NOTEPADPP_PLUGIN_CATALOG_TTL_SEC", "3600"))


def plugin_list_url() -> str:
    return os.environ.get("NOTEPADPP_PLUGIN_LIST_URL", DEFAULT_PLUGIN_LIST_URL).strip() or DEFAULT_PLUGIN_LIST_URL


def parse_plugins_array(data: Any) -> list[dict[str, Any]]:
    """Normalize old pluginList.json vs current pl.x64.json payloads to a list of plugin dicts."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    if isinstance(data.get("plugins"), list):
        return [x for x in data["plugins"] if isinstance(x, dict)]
    if isinstance(data.get("npp-plugins"), list):
        return [x for x in data["npp-plugins"] if isinstance(x, dict)]
    return []


def fetch_plugin_list_json() -> dict[str, Any]:
    """Fetch raw JSON from NOTEPADPP_PLUGIN_LIST_URL (default pl.x64.json)."""
    url = plugin_list_url()
    scheme = urlparse(url).scheme.lower()
    if scheme not in ("https", "http"):
        raise ValueError(f"NOTEPADPP_PLUGIN_LIST_URL must be http(s): got {scheme!r}")
    req = urllib.request.Request(url, headers={"User-Agent": "notepadpp-mcp/0.2"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=25) as resp:  # noqa: S310
        raw = resp.read()
    return json.loads(raw.decode("utf-8"))


def get_plugins_list_cached() -> tuple[list[dict[str, Any]] | None, str | None]:
    """Return (plugins, error_message). Cached in-process with TTL."""
    global _cached_plugins, _cached_at
    now = time.monotonic()
    with _CACHE_LOCK:
        if _cached_plugins is not None and (now - _cached_at) < _CACHE_TTL_SEC:
            return _cached_plugins, None
    try:
        payload = fetch_plugin_list_json()
        plugins = parse_plugins_array(payload)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        with _CACHE_LOCK:
            stale = _cached_plugins
        err = f"{type(e).__name__}: {e}"
        return stale, err
    with _CACHE_LOCK:
        _cached_plugins = plugins
        _cached_at = time.monotonic()
    return plugins, None


def _compact_key(s: str) -> str:
    return "".join(s.lower().split())


def build_catalog_indexes(
    plugins: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """folder-name (lower) -> entry; compact(folder-name) -> entry (first wins)."""
    by_folder: dict[str, dict[str, Any]] = {}
    by_compact: dict[str, dict[str, Any]] = {}
    for p in plugins:
        fn = (p.get("folder-name") or "").strip()
        if not fn:
            continue
        fl = fn.lower()
        if fl not in by_folder:
            by_folder[fl] = p
        ck = _compact_key(fn)
        if ck and ck not in by_compact:
            by_compact[ck] = p
    return by_folder, by_compact


def match_catalog_entry(
    dll_stem: str,
    by_folder: dict[str, dict[str, Any]],
    by_compact: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    """Match installed DLL stem (e.g. XMLTools) to catalog row."""
    stem = dll_stem.strip()
    if not stem:
        return None
    low = stem.lower()
    if low in by_folder:
        return by_folder[low]
    ck = _compact_key(stem)
    if ck in by_compact:
        return by_compact[ck]
    return None


def one_line_description(description: str, max_len: int = 200) -> str:
    """First line of description, normalized whitespace; ellipsis if long."""
    if not description or not description.strip():
        return ""
    line = description.replace("\r\n", "\n").split("\n", 1)[0].strip()
    line = " ".join(line.split())
    if len(line) > max_len:
        return line[: max_len - 1].rstrip() + "…"
    return line


def enrich_installed_plugins_disk(notepad_exe: str) -> dict[str, Any]:
    """
    Same as list_installed_plugins_disk, plus per-plugin catalog fields when the official list matches.

    Added keys on each plugin dict:
    - catalog_match: bool
    - catalog_display_name: str
    - description_one_line: str
    - catalog_version, author, homepage: str (when matched)
    """
    base = list_installed_plugins_disk(notepad_exe)
    plugins, err = get_plugins_list_cached()
    base["catalog_url"] = plugin_list_url()
    base["catalog_fetched_ok"] = plugins is not None
    if err:
        base["catalog_error"] = err
    if not plugins:
        for p in base.get("plugins", []):
            if isinstance(p, dict):
                p.setdefault("catalog_match", False)
                p.setdefault("catalog_display_name", "")
                p.setdefault("description_one_line", "")
        base["catalog_entries"] = 0
        return base

    by_folder, by_compact = build_catalog_indexes(plugins)
    base["catalog_entries"] = len(plugins)

    for p in base.get("plugins", []):
        if not isinstance(p, dict):
            continue
        stem = p.get("name") or ""
        meta = match_catalog_entry(str(stem), by_folder, by_compact)
        if meta:
            p["catalog_match"] = True
            p["catalog_display_name"] = (meta.get("display-name") or "").strip()
            p["description_one_line"] = one_line_description(meta.get("description") or "")
            p["catalog_version"] = (meta.get("version") or "").strip()
            p["author"] = (meta.get("author") or "").strip()
            p["homepage"] = (meta.get("homepage") or "").strip()
        else:
            p["catalog_match"] = False
            p["catalog_display_name"] = ""
            p["description_one_line"] = ""
            p["catalog_version"] = ""
            p["author"] = ""
            p["homepage"] = ""

    matched = sum(1 for p in base.get("plugins", []) if isinstance(p, dict) and p.get("catalog_match"))
    base["catalog_matched_count"] = matched
    return base
