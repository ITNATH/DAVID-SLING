"""L2 data/integrity - ingestion integrity validators.

schema / timestamp / sequence / duplicate / gap / stale / outlier checks.
Violations raise DataError (or mark the event) - never silently pass.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from david_sling.core.errors import DataError
from david_sling.core.schemas import Candle, Tick

MAX_TICK_AGE_S = 5.0
OUTLIER_Z = 6.0


def validate_tick(tick: Tick, *, now: datetime, last_ts: datetime | None, prev_mid: float | None,
                  recent_moves: list[float]) -> None:
    if tick.ask <= tick.bid:
        raise DataError(f"tick {tick.symbol}: ask <= bid ({tick.ask} <= {tick.bid})")
    if tick.ts > now + timedelta(seconds=MAX_TICK_AGE_S):
        raise DataError(f"tick {tick.symbol}: timestamp in the future")
    if last_ts is not None and tick.ts < last_ts:
        raise DataError(f"tick {tick.symbol}: non-monotonic timestamp (sequence violation)")
    if prev_mid is not None and len(recent_moves) >= 5:
        move = tick.mid - prev_mid
        mean = sum(recent_moves) / len(recent_moves)
        var = sum((m - mean) ** 2 for m in recent_moves) / len(recent_moves)
        sd = var ** 0.5
        if sd > 0 and abs(move - mean) / sd > OUTLIER_Z:
            raise DataError(f"tick {tick.symbol}: outlier move detected (z={(move - mean) / sd:.1f})")


def validate_candle(c: Candle) -> None:
    if c.high < c.low or c.high < max(c.open, c.close) or c.low > min(c.open, c.close):
        raise DataError(f"candle {c.symbol} {c.tf.value}: OHLC inconsistent")
    if c.tick_count < 0 or c.volume < 0:
        raise DataError(f"candle {c.symbol} {c.tf.value}: negative volume/ticks")


def detect_gap(symbol: str, tf_minutes: int, prev_close_time: datetime, next_open_time: datetime) -> bool:
    expected = prev_close_time + timedelta(minutes=tf_minutes)
    return next_open_time > expected


def is_stale(last_ts: datetime, now: datetime, max_age_s: float = MAX_TICK_AGE_S) -> bool:
    return (now - last_ts).total_seconds() > max_age_s
