"""L1 services/time_service - canonical UTC time service."""
from __future__ import annotations

from datetime import UTC, datetime

from david_sling.core import utils


class TimeService:
    def now(self) -> datetime:
        return utils.utc_now()

    def epoch_ms(self) -> int:
        return utils.epoch_ms()

    def utc(self) -> datetime:
        return datetime.now(UTC)
