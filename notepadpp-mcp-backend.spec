# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for notepadpp-mcp backend sidecar."""

from PyInstaller.utils.hooks import copy_metadata

pkg_name = "notepadpp_mcp"

datas = [(f"src/notepadpp_mcp", "notepadpp_mcp")]
for pkg in (
    "fastmcp",
    "fastapi",
    "uvicorn",
    "pydantic",
    "starlette",
    "httpx",
):
    datas += copy_metadata(pkg)

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "notepadpp_mcp.server",
    "notepadpp_mcp.api",
    "notepadpp_mcp.app",
    "notepadpp_mcp.main",
    "notepadpp_mcp.tools",
]

a = Analysis(
    ["run_server.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pandas", "scipy", "torch", "tensorflow"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="notepadpp-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
