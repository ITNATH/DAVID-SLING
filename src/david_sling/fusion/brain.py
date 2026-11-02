"""L5 fusion/nine_layer_fusion_brain - 9-layer bidirectional HTF<->MTF<->LTF.

Layers (config/timeframes.yaml fusion_layers): MN1, W1, D1, H8, H4, H1, M30,
M15, M5 - M1 is the trigger timeframe feeding the LTF state. Each layer emits
a directional score in [-1, 1]; top-down context (HTF->LTF) and ground-up
feedback (LTF->HTF) are combined 60/40; cross-layer disagreement above the
conflict threshold is recorded as a fusion conflict.

Latency budget: < 500 microseconds per evaluation.
"""
from __future__ import annotations

import time
from typing import Literal

from david_sling.core.errors import FusionError
from david_sling.core.schemas import Candle, FusionSnapshot, Timeframe
from david_sling.core.utils import clamp, utc_now
from david_sling.intelligence.features import FeatureSet, ema

FUSION_LAYERS: tuple[Timeframe, ...] = (
    Timeframe.MN1, Timeframe.W1, Timeframe.D1, Timeframe.H8,
    Timeframe.H4, Timeframe.H1, Timeframe.M30, Timeframe.M15, Timeframe.M5,
)

TOP_DOWN_WEIGHT = 0.6
GROUND_UP_WEIGHT = 0.4
CONFLICT_THRESHOLD = 0.6


def layer_score(candles: list[Candle]) -> float:
    """Directional score of one timeframe from EMA alignment + close position."""
    if len(candles) < 55:
        return 0.0
    closes = [c.close for c in candles]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    if not e20 or not e50:
        return 0.0
    alignment = (e20[-1] - e50[-1]) / max(e50[-1], 1e-12)
    slope = (e20[-1] - e20[-5]) / max(abs(e20[-5]), 1e-12)
    price_pos = (closes[-1] - e20[-1]) / max(e20[-1], 1e-12)
    score = clamp(alignment * 50 + slope * 100 + price_pos * 10, -1.0, 1.0)
    return round(score, 4)


class NineLayerFusionBrain:
    def __init__(self, conflict_threshold: float = CONFLICT_THRESHOLD,
                 convergence_threshold: float = 0.55) -> None:
        self.conflict_threshold = conflict_threshold
        self.convergence_threshold = convergence_threshold
        self.last: dict[str, FusionSnapshot] = {}

    def fuse(self, fs: FeatureSet, candles_by_tf: dict[Timeframe, list[Candle]]) -> FusionSnapshot:
        start = time.perf_counter()
        scores: dict[str, float] = {}
        for tf in FUSION_LAYERS:
            scores[tf.value] = layer_score(candles_by_tf.get(tf, []))
        # LTF trigger (M1) feeds ground-up
        ltf_score = float(fs.trend_m1) * 0.8 + clamp(fs.macd_hist_m1 * 1e6, -1, 1) * 0.2
        scores["M1"] = round(clamp(ltf_score, -1, 1), 4)

        # top-down: HTF layers bias the stack; ground-up: LTF momentum lifts it
        htf = [scores[tf.value] for tf in FUSION_LAYERS[:4]]   # MN1..H8
        mtf = [scores[tf.value] for tf in FUSION_LAYERS[4:7]]  # H4..M30
        ltf = [scores[tf.value] for tf in FUSION_LAYERS[7:]] + [scores["M1"]]
        top_down = sum(htf) / len(htf) * 0.7 + sum(mtf) / len(mtf) * 0.3
        ground_up = sum(ltf) / len(ltf)
        combined = TOP_DOWN_WEIGHT * top_down + GROUND_UP_WEIGHT * ground_up

        # conflicts: adjacent layer disagreement above threshold
        conflicts = 0
        ordered = [scores[tf.value] for tf in FUSION_LAYERS] + [scores["M1"]]
        for a, b in zip(ordered, ordered[1:], strict=False):
            if abs(a - b) >= self.conflict_threshold and a * b < 0:
                conflicts += 1

        # convergence: 1 - normalized dispersion
        m = sum(ordered) / len(ordered)
        dispersion = sum(abs(s - m) for s in ordered) / len(ordered) / 2.0
        convergence = clamp(1.0 - dispersion, 0.0, 1.0)

        direction: Literal["long", "short", "neutral"] = "long" if combined > 0.15 else ("short" if combined < -0.15 else "neutral")
        snap = FusionSnapshot(
            symbol=fs.symbol, layers=scores, convergence=round(convergence, 4),
            direction=direction, conflicts=conflicts, ts=fs.ts or utc_now(),
        )
        self.last[fs.symbol] = snap
        elapsed_us = (time.perf_counter() - start) * 1e6
        if elapsed_us > 500:
            raise FusionError(f"fusion latency budget exceeded: {elapsed_us:.0f}us > 500us")
        return snap

    def get(self, symbol: str) -> FusionSnapshot | None:
        return self.last.get(symbol)
