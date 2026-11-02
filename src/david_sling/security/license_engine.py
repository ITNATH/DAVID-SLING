"""L1 security - license engine.

Sim mode boots on a simulated institutional entitlement (ACTIVE).
Live mode verifies a signed license token: HMAC-SHA256 signature over the
base64url entitlement payload, keyed by DAVID_SLING_LICENSE_KEY. Any
verification failure raises SecurityError and halts the boot sequence.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass

from david_sling.core.errors import SecurityError

ENTITLEMENTS: tuple[str, ...] = (
    "engines ABCD",
    "strategy_vault_52",
    "evidence_ledger",
    "multi_trade_ops",
)


@dataclass(frozen=True)
class License:
    status: str  # ACTIVE | INVALID
    type: str  # simulated-institutional | institutional
    entitlements: tuple[str, ...]
    detail: str = ""


class LicenseEngine:
    def __init__(self, mode: str = "sim") -> None:
        self.mode = mode
        self.license = self.check()

    def check(self) -> License:
        if self.mode == "sim":
            return License(
                status="ACTIVE",
                type="simulated-institutional",
                entitlements=ENTITLEMENTS,
                detail="simulation mode - institutional entitlement simulated",
            )
        token = os.environ.get("DAVID_SLING_LICENSE_TOKEN", "")
        key = os.environ.get("DAVID_SLING_LICENSE_KEY", "")
        if not token or not key:
            raise SecurityError(
                "live mode requires DAVID_SLING_LICENSE_TOKEN and DAVID_SLING_LICENSE_KEY - boot halted"
            )
        payload_b64, _, sig = token.partition(".")
        expected = hmac.new(key.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            raise SecurityError("license signature invalid - boot halted")
        try:
            data = json.loads(base64.urlsafe_b64decode(payload_b64 + "=="))
        except Exception as exc:
            raise SecurityError("license payload unreadable - boot halted") from exc
        if data.get("product") != "DAVID-SLING":
            raise SecurityError("license is not issued for DAVID-SLING - boot halted")
        return License(
            status="ACTIVE",
            type="institutional",
            entitlements=tuple(data.get("entitlements", ENTITLEMENTS)),
            detail="cryptographic license verified (HMAC-SHA256)",
        )

    def permits(self, feature: str) -> bool:
        if self.license.status != "ACTIVE":
            return False
        return any(feature in ent for ent in self.license.entitlements)

    def status(self) -> dict:
        return {
            "status": self.license.status,
            "type": self.license.type,
            "entitlements": list(self.license.entitlements),
            "detail": self.license.detail,
        }
