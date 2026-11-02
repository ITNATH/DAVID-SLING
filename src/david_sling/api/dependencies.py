"""api/dependencies - dependency injection boundaries + optional bearer auth."""
from __future__ import annotations

from fastapi import Header, Request

from david_sling.security.session import OperatorSession


def get_runtime(request: Request):
    return request.app.state.runtime


async def require_token(authorization: str | None = Header(default=None)) -> None:
    """L1 security session gate: Bearer token required when DAVID_SLING_API_TOKEN is set."""
    OperatorSession().verify(authorization)
