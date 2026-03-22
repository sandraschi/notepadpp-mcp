"""HTTP Basic auth for the web dashboard API (same pattern as fleet SOTA servers)."""

import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def authenticate(
    credentials: HTTPBasicCredentials = Security(security),  # noqa: B008
) -> str:
    """Authenticate dashboard API requests (override via MCP_WEB_USER / MCP_WEB_PASSWORD)."""
    current_username_bytes = credentials.username.encode("utf-8")
    correct_username_bytes = os.getenv("MCP_WEB_USER", "sandra").encode("utf-8")
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)

    current_password_bytes = credentials.password.encode("utf-8")
    correct_password_bytes = os.getenv("MCP_WEB_PASSWORD", "vienna2026").encode("utf-8")
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
