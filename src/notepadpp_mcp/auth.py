"""HTTP Basic auth for the web dashboard API (same pattern as fleet SOTA servers)."""

import logging
import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

logger = logging.getLogger(__name__)

security = HTTPBasic()

# Fail closed: credentials must come from the environment (see .env.example).
# No hardcoded defaults — a missing password means the dashboard API stays locked.
_WEB_USER = os.getenv("MCP_WEB_USER", "").strip()
_WEB_PASSWORD = os.getenv("MCP_WEB_PASSWORD", "")

if not _WEB_USER or not _WEB_PASSWORD:
    logger.warning(
        "MCP_WEB_USER / MCP_WEB_PASSWORD not set - dashboard API is locked (401). "
        "Copy .env.example to .env and configure credentials."
    )


def authenticate(
    credentials: HTTPBasicCredentials = Security(security),
) -> str:
    """Authenticate dashboard API requests (configure via MCP_WEB_USER / MCP_WEB_PASSWORD)."""
    if not _WEB_USER or not _WEB_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dashboard auth is not configured - set MCP_WEB_USER and MCP_WEB_PASSWORD",
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
