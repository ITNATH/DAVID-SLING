"""L1 security - operator session and API token gate.

The operator console authenticates as master_admin. When the environment
variable DAVID_SLING_API_TOKEN is set, every API call must present it as
`Authorization: Bearer <token>`; otherwise the API is dev-open (sim).
"""
from __future__ import annotations

import hmac
import os

from david_sling.core.errors import SecurityError


class OperatorSession:
    role = "master_admin"

    def __init__(self) -> None:
        self.authenticated = True

    @staticmethod
    def token_required() -> bool:
        return bool(os.environ.get("DAVID_SLING_API_TOKEN"))

    def verify(self, authorization: str | None) -> None:
        expected = os.environ.get("DAVID_SLING_API_TOKEN")
        if not expected:
            return
        if authorization != f"Bearer {expected}":
            raise SecurityError("invalid or missing API token")

    def check(self, authorization: str | None) -> bool:
        expected = os.environ.get("DAVID_SLING_API_TOKEN")
        if not expected:
            return True
        if not authorization:
            return False
        return hmac.compare_digest(authorization, f"Bearer {expected}")

    def status(self) -> dict:
        return {
            "authenticated": self.authenticated,
            "role": self.role,
            "token_required": self.token_required(),
        }
