"""L3 regime/classifier - master regime classifier (8 regimes).

trend / range / compression / expansion / transition / mean_reversion /
volatility / liquidity - classified deterministically from FeatureSet.
"""
from __future__ import annotations

from david_sling.core.schemas import RegimeState
from david_sling.core.utils import utc_now
from david_sling.intelligence.features import FeatureSet


class RegimeClassifier:
    REGIMES = ("trend", "range", "compression", "expansion", "transition",
               "mean_reversion", "volatility", "liquidity")

    def classify(self, fs: FeatureSet) -> RegimeState:
        atr_pct = fs.atr_pct_h1
        align = fs.trend_alignment()
        if fs.sweep_up_m5 or fs.sweep_dn_m5 or fs.eqh or fs.eql:
            regime, conf = "liquidity", 0.7
        elif atr_pct >= 80:
            regime, conf = "volatility", 0.75
        elif atr_pct <= 20:
            regime, conf = "compression", 0.75
        elif align != 0 and atr_pct >= 55:
            regime, conf = "trend", 0.8
        elif align != 0:
            regime, conf = "transition", 0.6
        elif abs(fs.bb_pos_m1) >= 0.9:
            regime, conf = "mean_reversion", 0.7
        elif atr_pct >= 65:
            regime, conf = "expansion", 0.7
        else:
            regime, conf = "range", 0.6
        return RegimeState(regime=regime, confidence=conf, ts=fs.ts or utc_now())
