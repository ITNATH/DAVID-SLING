"""L4 hypothesis_engine - builds and maintains the technical thesis.

States: ARMED -> TRIGGERED -> (HOLD | CHANGE | FAILURE). Direction comes from
the feature set; invalidation price is the opposing structural level.
"""
from __future__ import annotations

from typing import Literal, cast

from david_sling.core.schemas import (
    HypothesisState,
    HypothesisStateValue,
    ScenarioState,
)
from david_sling.core.utils import utc_now
from david_sling.intelligence.features import FeatureSet


class HypothesisEngine:
    def __init__(self) -> None:
        self.theses: dict[str, HypothesisState] = {}

    def build(self, fs: FeatureSet, scenario: ScenarioState) -> HypothesisState:
        direction = "neutral"
        if fs.displacement_up or fs.bos_up_h1 or (fs.sweep_dn_m5 and fs.rejection_up):
            direction = "bullish"
        elif fs.displacement_dn or fs.bos_dn_h1 or (fs.sweep_up_m5 and fs.rejection_dn):
            direction = "bearish"
        elif fs.trend_alignment() > 0:
            direction = "bullish"
        elif fs.trend_alignment() < 0:
            direction = "bearish"

        if direction == "bullish":
            invalidation = fs.swing_low_h1 if fs.swing_low_h1 else fs.price - 3 * fs.atr_m1
        elif direction == "bearish":
            invalidation = fs.swing_high_h1 if fs.swing_high_h1 else fs.price + 3 * fs.atr_m1
        else:
            invalidation = None

        state = HypothesisState(direction=cast("Literal['bullish', 'bearish', 'neutral']", direction), state=HypothesisStateValue.ARMED,
                                invalidation_price=invalidation, ts=fs.ts or utc_now())
        self.theses[fs.symbol] = state
        return state

    def check_invalidation(self, symbol: str, price: float) -> bool:
        """G37: live invalidation - a broken thesis is marked FAILURE and reported."""
        thesis = self.theses.get(symbol)
        if thesis is None or thesis.invalidation_price is None:
            return False
        hit = False
        if thesis.direction == "bullish":
            hit = price < thesis.invalidation_price
        elif thesis.direction == "bearish":
            hit = price > thesis.invalidation_price
        if hit:
            self.theses[symbol] = thesis.model_copy(update={"state": HypothesisStateValue.FAILURE})
        return hit

    def get(self, symbol: str) -> HypothesisState | None:
        return self.theses.get(symbol)
