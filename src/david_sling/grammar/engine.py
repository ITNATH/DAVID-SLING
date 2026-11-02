"""L4 grammar_engine - formation grammar with causal sequence integrity.

A formation is valid when: precondition (non-terminal scenario) -> formation
step (displacement/structure present) -> confirmation step (1CDT/2CDT/3CDT
displacement candle count satisfied) and no invalidation step fired.
"""
from __future__ import annotations

from dataclasses import dataclass

from david_sling.core.schemas import ScenarioState
from david_sling.intelligence.features import FeatureSet
from david_sling.scenario_pool.engine import TERMINAL_IDS


@dataclass(frozen=True)
class GrammarResult:
    valid: bool
    confirmation: str          # none | 1CDT | 2CDT | 3CDT | Multi-CDT
    invalidated: bool
    reasons: tuple[str, ...]


class GrammarEngine:
    def __init__(self) -> None:
        self.last: dict[str, GrammarResult] = {}

    def validate(self, fs: FeatureSet, scenario: ScenarioState) -> GrammarResult:
        reasons: list[str] = []
        if scenario.scenario in TERMINAL_IDS:
            result = GrammarResult(False, "none", False, ("terminal scenario - grammar abstains",))
            self.last[fs.symbol] = result
            return result
        has_displacement = fs.displacement_up or fs.displacement_dn
        has_structure = fs.bos_up_h1 or fs.bos_dn_h1 or fs.choch_up_h1 or fs.choch_dn_h1
        if not has_displacement and not has_structure:
            reasons.append("no formation step")
        if not has_displacement:
            reasons.append("no CDT confirmation (displacement)")
        invalidated = (fs.displacement_up and fs.rejection_up) or (fs.displacement_dn and fs.rejection_dn)
        confirmation = "1CDT" if has_displacement else "none"
        if fs.range3_m1 > 3 * fs.atr_m1:
            confirmation = "3CDT"
        elif fs.range3_m1 > 2 * fs.atr_m1:
            confirmation = "2CDT"
        valid = has_displacement and not invalidated
        if invalidated:
            reasons.append("invalidation step fired")
        result = GrammarResult(valid, confirmation, invalidated, tuple(reasons))
        self.last[fs.symbol] = result
        return result

    def get(self, symbol: str) -> GrammarResult | None:
        return self.last.get(symbol)
