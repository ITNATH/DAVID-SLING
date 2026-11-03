"""L3 intelligence/forecast - calibrated forward probability distributions (G34).

For each forward horizon (5m, 15m, 30m, 1H, 4H, 8H) produces P(price higher at
horizon) from the fusion drift/convergence and ATR-scaled volatility, net of
half-spread cost. Probabilities are clamped to [0.01, 0.99] - never 0/1.
"""
from __future__ import annotations

import math

from david_sling.core.schemas import FusionSnapshot
from david_sling.intelligence.features import FeatureSet

# horizon label -> minutes
HORIZONS: dict[str, int] = {"5m": 5, "15m": 15, "30m": 30, "1H": 60, "4H": 240, "8H": 480}


def _clamp(p: float) -> float:
    return max(0.01, min(0.99, p))


def forward_probabilities(fs: FeatureSet, fusion: FusionSnapshot) -> dict[str, float]:
    """P(up) per horizon under a drift-diffusion model on relative returns.

    drift = fusion direction * convergence, scaled by sqrt(horizon) (fractal scaling);
    sigma = atr_m1 * sqrt(minutes) / price (relative vol per bar-minute);
    cost  = half-spread in relative terms - the breakeven hurdle per trade.
    """
    price = max(fs.price, 1e-9)
    atr = fs.atr_m1 if fs.atr_m1 and fs.atr_m1 > 0 else price * 0.0005
    if fusion.direction == "long":
        drift_sign = 1.0
    elif fusion.direction == "short":
        drift_sign = -1.0
    else:
        drift_sign = 0.0
    base_drift = drift_sign * fusion.convergence * 0.08  # per sqrt-minute drift
    cost = (fs.spread_points * (atr / max(price, 1e-9)) * 0.5) * 0.5  # half-spread hurdle (rel)
    out: dict[str, float] = {}
    for label, minutes in HORIZONS.items():
        sigma = atr * math.sqrt(minutes) / price
        mu = base_drift * math.sqrt(minutes)
        if sigma <= 0:
            out[label] = 0.5
            continue
        z = (mu - cost) / (sigma * math.sqrt(2.0))
        out[label] = round(_clamp(0.5 * (1.0 + math.erf(z))), 4)
    return out
