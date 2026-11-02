"""api/dependencies - dependency injection boundaries + optional bearer auth."""
from __future__ import annotations

import os

from fastapi import Header, Request

from david_sling.core.errors import SecurityError


def get_runtime(request: Request):
    return request.app.state.runtime


async def require_token(authorization: str | None = Header(default=None)) -> None:
    """If DAVID_SLING_API_TOKEN is configured, require it; otherwise dev-open."""
    expected = os.environ.get("DAVID_SLING_API_TOKEN")
    if not expected:
        return
    if authorization != f"Bearer {expected}":
        raise SecurityError("invalid or missing API token")
