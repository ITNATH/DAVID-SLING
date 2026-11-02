"""L3 intelligence/geometry/fibonacci - retracements, golden zone (OTE), extensions.

Blueprint: fibonacci/retracement.py, golden_zone.py, extension.py, sniper_zone.py.
Golden Zone / OTE = the 61.8%-78.6% retracement band of a prior impulsive swing.
"""
from __future__ import annotations

FIB_LEVELS: tuple[float, ...] = (0.236, 0.382, 0.5, 0.618, 0.786, 1.0)
GOLDEN_ZONE = (0.618, 0.786)


def retracement_ratio(swing_high: float, swing_low: float, price: float) -> float | None:
    """Retracement depth of `price` inside the swing [low, high], 0..1+. None if degenerate."""
    rng = swing_high - swing_low
    if rng <= 0:
        return None
    return (swing_high - price) / rng


def fib_level(swing_high: float, swing_low: float, ratio: float) -> float:
    return swing_high - (swing_high - swing_low) * ratio


def in_golden_zone(swing_high: float, swing_low: float, price: float) -> bool:
    """True when price sits inside the 61.8%-78.6% retracement of the swing."""
    r = retracement_ratio(swing_high, swing_low, price)
    return r is not None and GOLDEN_ZONE[0] <= r <= GOLDEN_ZONE[1]


def swing_extremes(candles: list, lookback: int = 50) -> tuple[float, float] | None:
    """Most recent significant swing high/low over the lookback window."""
    if len(candles) < 10:
        return None
    window = candles[-lookback:]
    return max(c.high for c in window), min(c.low for c in window)


def ote_signal(candles: list, trend_up: bool, lookback: int = 50) -> dict:
    """OTE / golden-zone detection on the latest swing.

    Long setup: uptrend swing (higher high), price pulling back into 61.8-78.6%.
    Short setup: mirror image.
    """
    ext = swing_extremes(candles, lookback)
    if ext is None or not candles:
        return {"in_golden_zone": False, "retracement": None, "swing_high": None, "swing_low": None}
    hi, lo = ext
    price = candles[-1].close
    r = retracement_ratio(hi, lo, price)
    zone = in_golden_zone(hi, lo, price)
    if not trend_up:  # invert for shorts: measure from the low
        r = (price - lo) / (hi - lo) if hi > lo else None
        zone = r is not None and GOLDEN_ZONE[0] <= r <= GOLDEN_ZONE[1]
    return {"in_golden_zone": zone and (trend_up or True), "retracement": round(r, 4) if r is not None else None,
            "swing_high": hi, "swing_low": lo,
            "long_ote": trend_up and zone, "short_ote": (not trend_up) and zone}
