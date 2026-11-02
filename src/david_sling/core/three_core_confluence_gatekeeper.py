"""L0 core/three_core_confluence_gatekeeper - Three-Core Confluence Gate.

Weights (config/confluence_weights.yaml, enforced here):
  Price Action (PA)            40%
  Candle morphology / CDT      35%
  Indicators                   25%
A setup passes only if the weighted confluence score clears the configured
threshold AND no hard contradiction is present.
"""
from __future__ import annotations

from dataclasses import dataclass

PA_WEIGHT = 0.40
CDT_WEIGHT = 0.35
INDICATOR_WEIGHT = 0.25
DEFAULT_THRESHOLD = 0.55


@dataclass(frozen=True)
class ThreeCoreScore:
    price_action: float        # 0..1
    candle_cdt: float          # 0..1
    indicators: float          # 0..1

    @property
    def weighted(self) -> float:
        return (
            self.price_action * PA_WEIGHT
            + self.candle_cdt * CDT_WEIGHT
            + self.indicators * INDICATOR_WEIGHT
        )

    def passes(self, threshold: float = DEFAULT_THRESHOLD, hard_conflict: bool = False) -> bool:
        return (not hard_conflict) and self.weighted >= threshold


class ThreeCoreConfluenceGatekeeper:
    def __init__(self, threshold: float = DEFAULT_THRESHOLD) -> None:
        self.threshold = threshold

    def evaluate(self, score: ThreeCoreScore, hard_conflict: bool = False) -> bool:
        return score.passes(self.threshold, hard_conflict)
