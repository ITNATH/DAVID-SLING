"""L4 scenario_pool_engine - single scenario authority ("Scenario is King").

Deterministic rule-based classification of a FeatureSet into one of the
28 concrete scenario families S1-S28 (S29-S31 are reserved macro states
mapped from D-engine conditions), or a terminal state:
UNKNOWN (insufficient data -> WAIT), CONFLICTED (hard conflict -> NO_ROUTE),
NOVEL (no family matches -> ABSTAIN).
"""
from __future__ import annotations

from david_sling.core.policies import TerminalState
from david_sling.core.schemas import ScenarioId, ScenarioState
from david_sling.core.utils import utc_now
from david_sling.intelligence.features import FeatureSet

FAMILY_BY_ID: dict[ScenarioId, str] = {
    ScenarioId.S1: "trend_continuation", ScenarioId.S2: "trend_failure",
    ScenarioId.S3: "pullback", ScenarioId.S4: "momentum",
    ScenarioId.S5: "breakout", ScenarioId.S6: "breakout_continuation",
    ScenarioId.S7: "breakout_failure", ScenarioId.S8: "fakeout",
    ScenarioId.S9: "liquidity_sweep", ScenarioId.S10: "reversal",
    ScenarioId.S11: "expansion", ScenarioId.S12: "compression",
    ScenarioId.S13: "consolidation", ScenarioId.S14: "mean_reversion",
    ScenarioId.S15: "accumulation", ScenarioId.S16: "distribution",
    ScenarioId.S17: "markup", ScenarioId.S18: "markdown",
    ScenarioId.S19: "exhaustion", ScenarioId.S20: "breakout_pullback_continuation",
    ScenarioId.S21: "breakout_failure_reversal", ScenarioId.S22: "quasimodo",
    ScenarioId.S23: "diamond", ScenarioId.S24: "parabolic_expansion",
    ScenarioId.S25: "turtle_soup", ScenarioId.S26: "taipan_soup",
    ScenarioId.S27: "multi_timeframe_alignment", ScenarioId.S28: "news_repricing",
    ScenarioId.S29: "macro_regime_shift", ScenarioId.S30: "macro_liquidity_cycle",
    ScenarioId.S31: "macro_expansion",
}

TERMINAL_IDS = {ScenarioId.UNKNOWN, ScenarioId.CONFLICTED, ScenarioId.NOVEL}


class ScenarioPoolEngine:
    def __init__(self) -> None:
        self.current: dict[str, ScenarioState] = {}
        self.forming: dict[str, ScenarioState] = {}

    def classify(self, fs: FeatureSet, min_bars: int = 60) -> ScenarioState:
        # terminal: insufficient data
        if fs.atr_m1 <= 0 or fs.range3_m1 <= 0:
            return self._terminal(fs, ScenarioId.UNKNOWN, 0.0)
        # terminal: hard conflict (opposing displacement + opposing structure same window)
        hard_conflict = (
            (fs.displacement_up and fs.bos_dn_h1 and fs.sweep_up_m5)
            or (fs.displacement_dn and fs.bos_up_h1 and fs.sweep_dn_m5)
        )
        if hard_conflict:
            return self._terminal(fs, ScenarioId.CONFLICTED, 0.5)

        sid = self._family(fs)
        if sid is None:
            return self._terminal(fs, ScenarioId.NOVEL, 0.2)
        conf = self._confidence(fs, sid)
        state = ScenarioState(scenario=sid, family=FAMILY_BY_ID[sid], confidence=conf,
                              forming=True, ts=fs.ts or utc_now())
        prev = self.current.get(fs.symbol)
        if prev and prev.scenario == sid:
            state = ScenarioState(scenario=sid, family=state.family, confidence=conf,
                                  forming=False, ts=state.ts)
        self.current[fs.symbol] = state
        return state

    def _terminal(self, fs: FeatureSet, sid: ScenarioId, conf: float) -> ScenarioState:
        name = sid.value
        state = ScenarioState(scenario=sid, family=f"terminal/{name.lower()}", confidence=conf,
                              forming=False, ts=fs.ts or utc_now())
        self.current[fs.symbol] = state
        return state

    def _confidence(self, fs: FeatureSet, sid: ScenarioId) -> float:
        base = 0.5
        if fs.trend_alignment() != 0:
            base += 0.15
        if fs.volume_z_m1 > 1.0:
            base += 0.1
        if fs.atr_pct_h1 >= 30:
            base += 0.1
        return min(0.99, base)

    def _family(self, fs: FeatureSet) -> ScenarioId | None:
        if fs.news_repricing and (fs.displacement_up or fs.displacement_dn):
            return ScenarioId.S28
        if fs.atr_pct_h1 >= 90 and (fs.displacement_up or fs.displacement_dn):
            return ScenarioId.S24  # parabolic expansion
        if abs(fs.wick_ratio) >= 0.8 and (fs.rejection_up or fs.rejection_dn):
            return ScenarioId.S26  # taipan soup
        if (fs.sweep_dn_m5 or fs.eql) and fs.displacement_up:
            return ScenarioId.S25  # turtle soup (sweep of lows + reclaim)
        if fs.trend_alignment() != 0 and fs.volume_z_m1 > 0.5:
            return ScenarioId.S27  # multi-timeframe alignment
        if fs.sweep_up_m5 and fs.rejection_dn:
            return ScenarioId.S8   # fakeout
        if fs.sweep_dn_m5 and fs.rejection_up:
            return ScenarioId.S8
        if fs.sweep_up_m5 or fs.sweep_dn_m5:
            return ScenarioId.S9   # liquidity sweep
        if fs.choch_up_h1 and fs.displacement_dn:
            return ScenarioId.S21  # breakout-failure-reversal
        if fs.choch_dn_h1 and fs.displacement_up:
            return ScenarioId.S21
        if fs.bos_up_h1 and fs.swing_high_h1 and fs.price > fs.swing_high_h1 and fs.volume_z_m1 > 1.0:
            return ScenarioId.S5   # breakout
        if fs.bos_dn_h1 and fs.swing_low_h1 and fs.price < fs.swing_low_h1 and fs.volume_z_m1 > 1.0:
            return ScenarioId.S5
        if fs.bos_up_h1 and fs.trend_h4 > 0 and fs.displacement_up:
            return ScenarioId.S6   # breakout continuation
        if fs.bos_dn_h1 and fs.trend_h4 < 0 and fs.displacement_dn:
            return ScenarioId.S6
        if (fs.displacement_up and fs.trend_h1 < 0) or (fs.displacement_dn and fs.trend_h1 > 0):
            return ScenarioId.S2   # trend failure
        if fs.displacement_up and fs.trend_h1 > 0:
            return ScenarioId.S1   # trend continuation
        if fs.displacement_dn and fs.trend_h1 < 0:
            return ScenarioId.S1
        if fs.trend_h1 > 0 and abs(fs.price - fs.ema20_m1) / max(fs.atr_m1, 1e-12) < 2 and 40 <= fs.rsi_m1 <= 65:
            return ScenarioId.S3   # pullback
        if fs.trend_h1 < 0 and abs(fs.price - fs.ema20_m1) / max(fs.atr_m1, 1e-12) < 2 and 35 <= fs.rsi_m1 <= 60:
            return ScenarioId.S3
        if fs.macd_hist_m1 != 0 and ((fs.macd_hist_m1 > 0) == (fs.trend_m1 > 0)) and abs(fs.roc_m1) > 0.001:
            return ScenarioId.S4   # momentum
        if fs.atr_pct_h1 >= 80:
            return ScenarioId.S11  # expansion
        if fs.atr_pct_h1 <= 20:
            return ScenarioId.S12  # compression
        if abs(fs.trend_h1) == 0 and fs.atr_pct_h1 < 45:
            return ScenarioId.S13  # consolidation
        if abs(fs.bb_pos_m1) >= 0.9:
            return ScenarioId.S14  # mean reversion
        if fs.rejection_dn and fs.volume_z_m1 > 0.5 and fs.trend_h1 >= 0:
            return ScenarioId.S15  # accumulation
        if fs.rejection_up and fs.volume_z_m1 > 0.5 and fs.trend_h1 <= 0:
            return ScenarioId.S16  # distribution
        if fs.trend_h4 > 0 and fs.price > fs.ema50_h4:
            return ScenarioId.S17  # markup
        if fs.trend_h4 < 0 and fs.price < fs.ema50_h4:
            return ScenarioId.S18  # markdown
        if fs.displacement_up and fs.rejection_up:
            return ScenarioId.S19  # exhaustion
        if fs.fvg_up_m5 and fs.displacement_up:
            return ScenarioId.S20  # breakout-pullback-continuation
        if fs.fvg_dn_m5 and fs.displacement_dn:
            return ScenarioId.S20
        if fs.eql and fs.displacement_up:
            return ScenarioId.S22  # quasimodo (sweep of equal lows + shift)
        if fs.eqh and fs.displacement_dn:
            return ScenarioId.S22
        if fs.atr_pct_h1 >= 70 and fs.atr_pct_h1 <= 80:
            return ScenarioId.S23  # diamond-ish compression after expansion
        return None

    def is_terminal(self, scenario: ScenarioId) -> bool:
        return scenario in TERMINAL_IDS

    def terminal_state(self, scenario: ScenarioId) -> TerminalState | None:
        return TerminalState(scenario.value) if scenario in TERMINAL_IDS else None
