"""L6 validation_engine - Three-Core Confluence Gate + contradiction engine.

PA (price action) 40% + Candle/CDT 35% + Indicators 25%. Hard conflicts
(opposing displacement + opposing structure) force a fail regardless of score.
"""
from __future__ import annotations

from david_sling.core.schemas import FusionSnapshot, ScenarioState, ValidationResult
from david_sling.core.three_core_confluence_gatekeeper import (
    CDT_WEIGHT,
    INDICATOR_WEIGHT,
    PA_WEIGHT,
)
from david_sling.core.utils import clamp
from david_sling.intelligence.features import FeatureSet
from david_sling.scenario_pool.engine import TERMINAL_IDS


class ValidationEngine:
    def __init__(self, threshold: float = 0.55) -> None:
        self.threshold = threshold

    def evaluate(self, fs: FeatureSet, scenario: ScenarioState, fusion: FusionSnapshot) -> ValidationResult:
        if scenario.scenario in TERMINAL_IDS:
            return ValidationResult(passed=False, pa_score=0.0, cdt_score=0.0, indicator_score=0.0,
                                    weighted=0.0, hard_conflict=True,
                                    contradictions=[f"terminal scenario {scenario.scenario.value}"])

        direction = 1 if fusion.direction == "long" else (-1 if fusion.direction == "short" else 0)

        # PA score: displacement / rejection aligned with fusion direction
        pa = 0.0
        if direction > 0:
            pa += 0.5 if fs.displacement_up else 0.0
            pa += 0.3 if fs.rejection_dn else 0.0
            pa += 0.2 if fs.bos_up_h1 else 0.0
        elif direction < 0:
            pa += 0.5 if fs.displacement_dn else 0.0
            pa += 0.3 if fs.rejection_up else 0.0
            pa += 0.2 if fs.bos_dn_h1 else 0.0
        pa = clamp(pa, 0.0, 1.0)

        # Candle/CDT score: displacement strength + wick structure
        cdt = 0.0
        if fs.displacement_up or fs.displacement_dn:
            cdt += 0.5
        if fs.range3_m1 > 2 * fs.atr_m1:
            cdt += 0.3
        if abs(fs.wick_ratio) > 0.3:
            cdt += 0.2
        cdt = clamp(cdt, 0.0, 1.0)

        # Indicator score: RSI / MACD / BB alignment with direction
        ind = 0.0
        if direction > 0:
            if 50 < fs.rsi_m1 < 75:
                ind += 0.35
            if fs.macd_hist_m1 > 0:
                ind += 0.35
            if fs.bb_pos_m1 > -0.2:
                ind += 0.3
        elif direction < 0:
            if 25 < fs.rsi_m1 < 50:
                ind += 0.35
            if fs.macd_hist_m1 < 0:
                ind += 0.35
            if fs.bb_pos_m1 < 0.2:
                ind += 0.3
        else:
            ind = 0.3 if 40 < fs.rsi_m1 < 60 else 0.1
        ind = clamp(ind, 0.0, 1.0)

        contradictions: list[str] = []
        hard = False
        if fs.displacement_up and fs.displacement_dn:
            contradictions.append("opposing displacement in window")
            hard = True
        if fs.bos_up_h1 and fs.bos_dn_h1:
            contradictions.append("opposing BOS on H1")
            hard = True
        if direction != 0 and ((direction > 0 and fs.sweep_up_m5 and fs.rejection_dn)
                                or (direction < 0 and fs.sweep_dn_m5 and fs.rejection_up)):
            contradictions.append("sweep-reject against fusion direction")

        weighted = pa * PA_WEIGHT + cdt * CDT_WEIGHT + ind * INDICATOR_WEIGHT
        passed = (not hard) and weighted >= self.threshold and len(contradictions) == 0
        return ValidationResult(
            passed=passed, pa_score=round(pa, 4), cdt_score=round(cdt, 4),
            indicator_score=round(ind, 4), weighted=round(weighted, 4),
            hard_conflict=hard, contradictions=contradictions,
        )
