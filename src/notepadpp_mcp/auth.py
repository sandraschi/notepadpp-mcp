"""HTTP Basic auth for the web dashboard API (same pattern as fleet SOTA servers)."""

import logging
import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

logger = logging.getLogger(__name__)

# auto_error=False: a missing Authorization header yields None instead of an
# automatic 401, so auth can be fully deactivated when no credentials are set.
security = HTTPBasic(auto_error=False)

# Optional auth: credentials come from the environment (see .env.example).
# When MCP_WEB_USER / MCP_WEB_PASSWORD are NOT set, the dashboard API is open
# (localhost-only service). Setting them turns auth on. No hardcoded defaults.
_WEB_USER = os.getenv("MCP_WEB_USER", "").strip()
_WEB_PASSWORD = os.getenv("MCP_WEB_PASSWORD", "")

_AUTH_DISABLED = not _WEB_USER or not _WEB_PASSWORD

if _AUTH_DISABLED:
    logger.warning(
        "MCP_WEB_USER / MCP_WEB_PASSWORD not set - dashboard API is OPEN (no auth). "
        "Copy .env.example to .env and configure credentials to lock it down."
    )


def authenticate(
    credentials: HTTPBasicCredentials | None = Security(security),
) -> str:
    """Authenticate dashboard API requests (configure via MCP_WEB_USER / MCP_WEB_PASSWORD)."""
    if _AUTH_DISABLED:
        # Auth deactivated: allow anonymous access (localhost-only service).
        return "anonymous"
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    current_username_bytes = credentials.username.encode("utf-8")
    correct_username_bytes = _WEB_USER.encode("utf-8")
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)

    current_password_bytes = credentials.password.encode("utf-8")
    correct_password_bytes = _WEB_PASSWORD.encode("utf-8")
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
