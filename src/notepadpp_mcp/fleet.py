"""Probe other MCP webapps (fleet) via /api/health on registered ports."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

DEFAULT_REGISTRY = Path(r"D:\Dev\repos\mcp-central-docs\operations\webapp-registry.json")


def _registry_path() -> Path | None:
    raw = os.getenv("NOTEPADPP_FLEET_REGISTRY", str(DEFAULT_REGISTRY))
    p = Path(raw)
    return p if p.is_file() else None


def _load_ports() -> list[int]:
    path = _registry_path()
    if not path:
        return [
            10700,
            10704,
            10706,
            10720,
            10721,
            10742,
            10743,
            10748,
            10749,
            10813,
            10814,
            10815,
            10818,
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        webapps: list[dict[str, Any]] = data.get("webapps", [])
        ports: list[int] = []
        for w in webapps:
            p = w.get("port")
            if isinstance(p, int) and 10700 <= p <= 10900:
                ports.append(p)
        return sorted(set(ports))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return [10815]


async def probe_fleet(host: str = "127.0.0.1") -> list[dict[str, Any]]:
    """GET http://host:port/api/health on each known port; mark reachable."""
    ports = _load_ports()
    results: list[dict[str, Any]] = []
    timeout = httpx.Timeout(0.35)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for port in ports:
            url = f"http://{host}:{port}/api/health"
            reachable = False
            detail: dict[str, Any] | None = None
            try:
                r = await client.get(url)
                reachable = r.status_code == 200
                if reachable:
                    try:
                        detail = r.json()
                    except json.JSONDecodeError:
                        detail = {"raw": r.text[:200]}
            except (httpx.HTTPError, OSError):
                reachable = False
            results.append(
                {
                    "port": port,
                    "url": f"http://{host}:{port}/",
                    "health_url": url,
                    "reachable": reachable,
                    "health": detail,
                }
            )
    return results
