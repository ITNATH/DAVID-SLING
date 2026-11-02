"""L0 core/session_epoch_manager - 6-Phase Session Epoch Clock (UTC).

Phases: ASIA, LONDON, NY, LONDON_NY_OVERLAP, TEN_AM_CLUB (NY 10:00), OFF_HOURS.
"""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum


class SessionEpoch(StrEnum):
    ASIA = "ASIA"                       # 00:00 - 07:00 UTC
    ASIA_LONDON_OVERLAP = "ASIA_LONDON_OVERLAP"  # 07:00 - 08:00 UTC
    LONDON = "LONDON"                   # 08:00 - 13:00 UTC
    LONDON_NY_OVERLAP = "LONDON_NY_OVERLAP"      # 13:00 - 16:00 UTC
    TEN_AM_CLUB = "TEN_AM_CLUB"         # 14:00 - 15:00 UTC (NY 10:00 AM)
    NY = "NY"                           # 16:00 - 22:00 UTC (outside 10AM club)
    OFF_HOURS = "OFF_HOURS"             # 22:00 - 24:00 UTC


# Exactly six primary trading phases per the blueprint (overlaps reported as
# attributes of the clock while the epoch enum carries the 6-phase model).
SIX_PHASES: tuple[str, ...] = (
    "ASIA", "LONDON", "NY", "OVERLAPS", "TEN_AM_CLUB", "OFF_HOURS",
)


def epoch_at(dt: datetime) -> SessionEpoch:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    h = dt.astimezone(UTC).hour
    if 0 <= h < 7:
        return SessionEpoch.ASIA
    if h == 7:
        return SessionEpoch.ASIA_LONDON_OVERLAP
    if 8 <= h < 13:
        return SessionEpoch.LONDON
    if 13 <= h < 16:
        return SessionEpoch.LONDON_NY_OVERLAP
    if 14 <= h < 15:
        return SessionEpoch.TEN_AM_CLUB
    if 16 <= h < 22:
        return SessionEpoch.NY
    return SessionEpoch.OFF_HOURS


def primary_phase(dt: datetime) -> str:
    """Map the fine-grained epoch onto the 6-phase model."""
    e = epoch_at(dt)
    if e in (SessionEpoch.ASIA_LONDON_OVERLAP, SessionEpoch.LONDON_NY_OVERLAP):
        return "OVERLAPS"
    return e.value


def is_high_liquidity(dt: datetime) -> bool:
    return epoch_at(dt) in (
        SessionEpoch.LONDON, SessionEpoch.LONDON_NY_OVERLAP,
        SessionEpoch.TEN_AM_CLUB, SessionEpoch.NY,
    )
