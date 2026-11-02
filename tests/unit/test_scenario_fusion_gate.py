"""Scenario pool terminal states, 9-layer fusion determinism, three-core weights."""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from david_sling.core.errors import ValidationError
from david_sling.core.policies import (
    TerminalState,
    abstention_for,
    enforce_no_time_expiry,
)
from david_sling.core.schemas import ScenarioId, Timeframe
from david_sling.core.three_core_confluence_gatekeeper import (
    CDT_WEIGHT,
    INDICATOR_WEIGHT,
    PA_WEIGHT,
    ThreeCoreScore,
)
from david_sling.fusion.brain import FUSION_LAYERS, NineLayerFusionBrain
from david_sling.intelligence.features import FeatureSet
from david_sling.scenario_pool.engine import ScenarioPoolEngine
from david_sling.validation.engine import ValidationEngine


def test_terminal_states_map_to_abstention():
    assert abstention_for(TerminalState.UNKNOWN).value == "WAIT"
    assert abstention_for(TerminalState.CONFLICTED).value == "NO_ROUTE"
    assert abstention_for(TerminalState.NOVEL).value == "ABSTAIN"


def test_no_time_expiry_enforced():
    enforce_no_time_expiry(None)
    with pytest.raises(ValidationError):
        enforce_no_time_expiry(3600)


def test_three_core_weights_sum_and_gate():
    assert abs(PA_WEIGHT + CDT_WEIGHT + INDICATOR_WEIGHT - 1.0) < 1e-9
    assert PA_WEIGHT == 0.40 and CDT_WEIGHT == 0.35 and INDICATOR_WEIGHT == 0.25
    s = ThreeCoreScore(price_action=1.0, candle_cdt=1.0, indicators=1.0)
    assert s.weighted == 1.0 and s.passes(0.55)
    assert not ThreeCoreScore(0.6, 0.6, 0.6).passes(0.55, hard_conflict=True)


def _fs(**kw) -> FeatureSet:
    base = dict(symbol="EURUSD", ts=datetime(2026, 1, 5, 10, tzinfo=UTC), price=1.1000,
                spread_points=2.0, session="LONDON", atr_m1=0.001, range3_m1=0.003)
    base.update(kw)
    return FeatureSet(**base)


def test_scenario_classifies_trend_continuation():
    eng = ScenarioPoolEngine()
    fs = _fs(displacement_up=True, trend_h1=1, volume_z_m1=1.2)
    st = eng.classify(fs)
    assert st.scenario == ScenarioId.S1
    assert not eng.is_terminal(st.scenario)


def test_scenario_terminal_unknown_on_empty_data():
    eng = ScenarioPoolEngine()
    st = eng.classify(_fs(atr_m1=0.0, range3_m1=0.0))
    assert st.scenario == ScenarioId.UNKNOWN
    assert eng.is_terminal(st.scenario)


def test_fusion_nine_layers_and_determinism():
    brain = NineLayerFusionBrain()
    assert len(FUSION_LAYERS) == 9
    fs = _fs(trend_m1=1, macd_hist_m1=1e-6)
    candles = {tf: [] for tf in Timeframe}
    snap1 = brain.fuse(fs, candles)
    snap2 = brain.fuse(fs, candles)
    assert snap1.layers == snap2.layers and snap1.convergence == snap2.convergence
    assert set(snap1.layers) >= {tf.value for tf in FUSION_LAYERS}


def test_validation_terminal_fails():
    ve = ValidationEngine()
    from david_sling.core.schemas import FusionSnapshot, ScenarioState
    fs = _fs()
    scen = ScenarioState(scenario=ScenarioId.UNKNOWN, family="terminal/unknown", confidence=0.0,
                         ts=fs.ts)
    fus = FusionSnapshot(symbol="EURUSD", layers={}, convergence=0.0, direction="neutral", ts=fs.ts)
    res = ve.evaluate(fs, scen, fus)
    assert not res.passed and res.hard_conflict
