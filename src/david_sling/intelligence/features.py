"""L3 intelligence - feature extraction across the 16 intelligence families.

Real math (pure Python): EMA/SMA/RSI/MACD/ATR/Bollinger/VWAP/ROC indicators,
fractal swing points, BOS/CHoCH structure, equal highs/lows + sweeps,
displacement/rejection price action, FVG/order-block zones, volume z-score,
orderflow delta. Output is a deterministic FeatureSet consumed by scenario,
fusion, validation, routing and the strategy vault.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from david_sling.core.schemas import Candle, Timeframe
from david_sling.core.utils import clamp, mean, percentile, stdev


# ------------------------------------------------------------ indicators
def ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2.0 / (period + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def sma(values: list[float], period: int) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        window = values[max(0, i - period + 1): i + 1]
        out.append(mean(window))
    return out


def rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) <= period:
        return 50.0
    gains, losses = 0.0, 0.0
    for i in range(-period, 0):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    if losses == 0:
        return 100.0
    rs = (gains / period) / (losses / period)
    return 100.0 - 100.0 / (1.0 + rs)


def macd_hist(closes: list[float]) -> float:
    if len(closes) < 35:
        return 0.0
    e12 = ema(closes, 12)
    e26 = ema(closes, 26)
    macd_line = e12[-1] - e26[-1]
    signal = ema([e12[i] - e26[i] for i in range(len(closes))], 9)[-1]
    return macd_line - signal


def atr(candles: list[Candle], period: int = 14) -> list[float]:
    trs: list[float] = []
    for i in range(1, len(candles)):
        h, lo, pc = candles[i].high, candles[i].low, candles[i - 1].close
        trs.append(max(h - lo, abs(h - pc), abs(lo - pc)))
    out = sma([candles[0].high - candles[0].low] + trs, period)
    return out


def bollinger_pos(closes: list[float], period: int = 20) -> float:
    if len(closes) < period:
        return 0.5
    window = closes[-period:]
    m = mean(window)
    sd = stdev(window) or 1e-12
    return clamp((closes[-1] - m) / (2 * sd), -1.0, 1.0)


def roc(closes: list[float], period: int = 10) -> float:
    if len(closes) <= period:
        return 0.0
    return (closes[-1] - closes[-1 - period]) / closes[-1 - period]


def vwap(candles: list[Candle]) -> float:
    tp_vol = sum((c.high + c.low + c.close) / 3 * (c.volume or 1) for c in candles)
    vol = sum(c.volume or 1 for c in candles)
    return tp_vol / vol if vol else candles[-1].close


# ------------------------------------------------------------ structure
def swing_points(candles: list[Candle], left: int = 2, right: int = 2) -> tuple[list[int], list[int]]:
    highs, lows = [], []
    for i in range(left, len(candles) - right):
        if all(candles[i].high > candles[j].high for j in range(i - left, i + right + 1) if j != i):
            highs.append(i)
        if all(candles[i].low < candles[j].low for j in range(i - left, i + right + 1) if j != i):
            lows.append(i)
    return highs, lows


def structure_signals(candles: list[Candle]) -> dict[str, Any]:
    """BOS / CHoCH detection on a candle series (ICT-style, simplified)."""
    highs, lows = swing_points(candles)
    out = {"bos_up": False, "bos_dn": False, "choch_up": False, "choch_dn": False,
           "swing_high": candles[highs[-1]].high if highs else None,
           "swing_low": candles[lows[-1]].low if lows else None,
           "prev_swing_high": candles[highs[-2]].high if len(highs) >= 2 else None,
           "prev_swing_low": candles[lows[-2]].low if len(lows) >= 2 else None}
    if len(highs) >= 2 and len(lows) >= 2:
        # bullish structure: higher highs and higher lows; BOS = close above prev swing high
        if candles[-1].close > candles[highs[-2]].high and candles[lows[-1]].low > candles[lows[-2]].low:
            out["bos_up"] = True
        if candles[-1].close < candles[lows[-2]].low and candles[highs[-1]].high < candles[highs[-2]].high:
            out["bos_dn"] = True
        # CHoCH: close beyond the most recent opposite extreme after a BOS
        if out["bos_up"] and candles[-1].close < candles[lows[-1]].low:
            out["choch_dn"] = True
        if out["bos_dn"] and candles[-1].close > candles[highs[-1]].high:
            out["choch_up"] = True
    return out


# ------------------------------------------------------------ liquidity / zones
def liquidity_signals(candles: list[Candle], lookback: int = 20) -> dict[str, Any]:
    highs = [c.high for c in candles[-lookback:]]
    lows = [c.low for c in candles[-lookback:]]
    eqh = max(highs) - min(highs[-5:]) < (max(highs) - min(lows)) * 0.02 and len(set(round(h, 6) for h in highs[-4:])) <= 2
    eql = min(lows) - max(lows[-5:]) > -(max(highs) - min(lows)) * 0.02 and len(set(round(lo, 6) for lo in lows[-4:])) <= 2
    sweep_up = candles[-1].high > max(highs[:-1]) and candles[-1].close < max(highs[:-1])
    sweep_dn = candles[-1].low < min(lows[:-1]) and candles[-1].close > min(lows[:-1])
    return {"eqh": eqh, "eql": eql, "sweep_up": sweep_up, "sweep_dn": sweep_dn,
            "range_high": max(highs), "range_low": min(lows)}


def fvg_signals(candles: list[Candle]) -> dict[str, Any]:
    up = dn = False
    if len(candles) >= 3:
        c0, _c1, c2 = candles[-3], candles[-2], candles[-1]
        if c0.low > c2.high:  # bullish FVG
            up = True
        if c0.high < c2.low:  # bearish FVG
            dn = True
    return {"fvg_up": up, "fvg_dn": dn}


def price_action_signals(candles: list[Candle], atr_now: float) -> dict[str, Any]:
    if len(candles) < 3 or atr_now <= 0:
        return {"displacement_up": False, "displacement_dn": False, "rejection_up": False, "rejection_dn": False,
                "wick_ratio": 0.0, "body_ratio": 0.0, "range3": 0.0}
    last3 = candles[-3:]
    range3 = sum(c.high - c.low for c in last3)
    displacement_up = all(c.close > c.open for c in last3) and range3 > 1.5 * atr_now * 3
    displacement_dn = all(c.close < c.open for c in last3) and range3 > 1.5 * atr_now * 3
    c = candles[-1]
    rng = max(c.high - c.low, 1e-12)
    upper_wick = (c.high - max(c.open, c.close)) / rng
    lower_wick = (min(c.open, c.close) - c.low) / rng
    body = abs(c.close - c.open) / rng
    return {
        "displacement_up": displacement_up, "displacement_dn": displacement_dn,
        "rejection_up": upper_wick > 0.6, "rejection_dn": lower_wick > 0.6,
        "wick_ratio": round(upper_wick if upper_wick > lower_wick else -lower_wick, 4),
        "body_ratio": round(body, 4), "range3": range3,
    }


# ------------------------------------------------------------ FeatureSet
@dataclass
class FeatureSet:
    symbol: str
    ts: datetime
    price: float
    spread_points: float
    session: str
    atr_m1: float = 0.0
    atr_h1: float = 0.0
    atr_pct_h1: float = 50.0
    ema20_m1: float = 0.0
    ema50_m1: float = 0.0
    ema20_h1: float = 0.0
    ema50_h1: float = 0.0
    ema20_h4: float = 0.0
    ema50_h4: float = 0.0
    rsi_m1: float = 50.0
    macd_hist_m1: float = 0.0
    bb_pos_m1: float = 0.0
    vwap_m1: float = 0.0
    roc_m1: float = 0.0
    trend_m1: int = 0
    trend_m15: int = 0
    trend_h1: int = 0
    trend_h4: int = 0
    trend_d1: int = 0
    bos_up_h1: bool = False
    bos_dn_h1: bool = False
    choch_up_h1: bool = False
    choch_dn_h1: bool = False
    swing_high_h1: float | None = None
    swing_low_h1: float | None = None
    eqh: bool = False
    eql: bool = False
    sweep_up_m5: bool = False
    sweep_dn_m5: bool = False
    fvg_up_m5: bool = False
    fvg_dn_m5: bool = False
    displacement_up: bool = False
    displacement_dn: bool = False
    rejection_up: bool = False
    rejection_dn: bool = False
    wick_ratio: float = 0.0
    range3_m1: float = 0.0
    volume_z_m1: float = 0.0
    delta_m1: float = 0.0        # simulated orderflow delta (signed)
    news_repricing: bool = False
    observations: list[dict] = field(default_factory=list)

    def trend_alignment(self) -> int:
        """+1 if H4/H1/M15 trends agree up, -1 agree down, else 0."""
        vals = [self.trend_h4, self.trend_h1, self.trend_m15]
        if all(v > 0 for v in vals):
            return 1
        if all(v < 0 for v in vals):
            return -1
        return 0


def _trend(closes: list[float], fast: int = 20, slow: int = 50) -> int:
    if len(closes) < slow + 5:
        return 0
    ef, es = ema(closes, fast), ema(closes, slow)
    if ef[-1] > es[-1] and ef[-1] > ef[-5]:
        return 1
    if ef[-1] < es[-1] and ef[-1] < ef[-5]:
        return -1
    return 0


def compute_features(symbol: str, ts: datetime, price: float, spread_points: float, session: str,
                     candles_by_tf: dict[Timeframe, list[Candle]],
                     deltas: list[float] | None = None, news_repricing: bool = False) -> FeatureSet:
    m1 = candles_by_tf.get(Timeframe.M1, [])
    m5 = candles_by_tf.get(Timeframe.M5, [])
    m15 = candles_by_tf.get(Timeframe.M15, [])
    h1 = candles_by_tf.get(Timeframe.H1, [])
    h4 = candles_by_tf.get(Timeframe.H4, [])
    d1 = candles_by_tf.get(Timeframe.D1, [])

    closes_m1 = [c.close for c in m1]
    closes_h1 = [c.close for c in h1]
    closes_h4 = [c.close for c in h4]
    closes_m15 = [c.close for c in m15]
    closes_d1 = [c.close for c in d1]

    atr_m1 = atr(m1)[-1] if m1 else 0.0
    atr_h1_list = atr(h1)
    atr_h1 = atr_h1_list[-1] if atr_h1_list else 0.0
    atr_pct_h1 = percentile(atr_h1_list, 50)  # refined below
    if len(atr_h1_list) > 30:
        atr_pct_h1 = percentile([ (a / closes_h1[i]) * 100 for i, a in enumerate(atr_h1_list, start=1) ][-30:], 50)

    e20m1 = ema(closes_m1, 20)
    e50m1 = ema(closes_m1, 50)
    e20h1 = ema(closes_h1, 20)
    e50h1 = ema(closes_h1, 50)
    e20h4 = ema(closes_h4, 20)
    e50h4 = ema(closes_h4, 50)

    struct_h1 = structure_signals(h1) if len(h1) >= 10 else {}
    liq_m5 = liquidity_signals(m5) if len(m5) >= 10 else {}
    fvg = fvg_signals(m5)
    pa = price_action_signals(m1, atr_m1)

    vols = [c.volume for c in m1[-30:]]
    vz = 0.0
    if len(vols) >= 10:
        m, s = mean(vols[:-1]), stdev(vols[:-1]) or 1e-9
        vz = (vols[-1] - m) / s

    fs = FeatureSet(
        symbol=symbol, ts=ts, price=price, spread_points=spread_points, session=session,
        atr_m1=atr_m1, atr_h1=atr_h1, atr_pct_h1=atr_pct_h1,
        ema20_m1=e20m1[-1] if e20m1 else price, ema50_m1=e50m1[-1] if e50m1 else price,
        ema20_h1=e20h1[-1] if e20h1 else price, ema50_h1=e50h1[-1] if e50h1 else price,
        ema20_h4=e20h4[-1] if e20h4 else price, ema50_h4=e50h4[-1] if e50h4 else price,
        rsi_m1=rsi(closes_m1), macd_hist_m1=macd_hist(closes_m1), bb_pos_m1=bollinger_pos(closes_m1),
        vwap_m1=vwap(m1[-20:]) if m1 else price, roc_m1=roc(closes_m1),
        trend_m1=_trend(closes_m1), trend_m15=_trend(closes_m15, 10, 30),
        trend_h1=_trend(closes_h1), trend_h4=_trend(closes_h4), trend_d1=_trend(closes_d1, 10, 30),
        bos_up_h1=bool(struct_h1.get("bos_up")), bos_dn_h1=bool(struct_h1.get("bos_dn")),
        choch_up_h1=bool(struct_h1.get("choch_up")), choch_dn_h1=bool(struct_h1.get("choch_dn")),
        swing_high_h1=struct_h1.get("swing_high"), swing_low_h1=struct_h1.get("swing_low"),
        eqh=bool(liq_m5.get("eqh")), eql=bool(liq_m5.get("eql")),
        sweep_up_m5=bool(liq_m5.get("sweep_up")), sweep_dn_m5=bool(liq_m5.get("sweep_dn")),
        fvg_up_m5=fvg["fvg_up"], fvg_dn_m5=fvg["fvg_dn"],
        displacement_up=pa["displacement_up"], displacement_dn=pa["displacement_dn"],
        rejection_up=pa["rejection_up"], rejection_dn=pa["rejection_dn"],
        wick_ratio=pa["wick_ratio"], range3_m1=pa["range3"],
        volume_z_m1=round(vz, 3),
        delta_m1=round(mean(deltas[-20:]) if deltas else 0.0, 4),
        news_repricing=news_repricing,
    )
    return fs
