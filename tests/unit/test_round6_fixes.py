"""Round-6 fix regressions: G31 bar-close isolation, G32 killzone, G40 neutral abstain, G41 cap."""
from datetime import UTC, datetime, timedelta

from david_sling.core.schemas import Tick, Timeframe
from david_sling.core.session_epoch_manager import SessionEpoch, epoch_at
from david_sling.core.utils import utc_now
from david_sling.data.market import CandleBuilder
from david_sling.intelligence.features import FeatureSet
from david_sling.risk.gate import RiskGate
from david_sling.strategies.vault import STRATEGY_VAULT, _dir


def test_G32_ten_am_club_reachable():
    dt = datetime(2026, 11, 3, 14, 30, tzinfo=UTC)
    assert epoch_at(dt) == SessionEpoch.TEN_AM_CLUB
    assert epoch_at(datetime(2026, 11, 3, 13, 30, tzinfo=UTC)) == SessionEpoch.LONDON_NY_OVERLAP
    assert epoch_at(datetime(2026, 11, 3, 15, 30, tzinfo=UTC)) == SessionEpoch.LONDON_NY_OVERLAP
    assert epoch_at(datetime(2026, 11, 3, 7, 30, tzinfo=UTC)) == SessionEpoch.ASIA_LONDON_OVERLAP
    assert epoch_at(datetime(2026, 11, 3, 3, 0, tzinfo=UTC)) == SessionEpoch.ASIA


def test_G40_neutral_abstains_no_forced_short():
    fs = FeatureSet(symbol="EURUSD", ts=utc_now(), price=1.10, spread_points=2.0, session="LONDON")
    # all neutral: no displacement, trend_alignment == 0
    assert _dir(fs) is None
    assert STRATEGY_VAULT.evaluate(fs) == []


def test_G31_closed_only_series_excludes_forming():
    b = CandleBuilder()
    base = datetime(2026, 1, 5, tzinfo=UTC)
    for i in range(5):
        b.add_tick(Tick(symbol="EURUSD", bid=1.1 + i * 1e-5, ask=1.1 + i * 1e-5 + 2e-5,
                        ts=base + timedelta(minutes=i)))
    closed = b.candles("EURUSD", Timeframe.M1, include_forming=False)
    forming_incl = b.candles("EURUSD", Timeframe.M1, include_forming=True)
    assert len(closed) == 4          # 5 ticks -> 4 closed + 1 forming
    assert len(forming_incl) == 5
    # closed-only never contains the still-forming bucket
    assert all(c.open_time < base + timedelta(minutes=4) for c in closed)


def test_G41_one_position_per_symbol():
    gate = RiskGate({"risk_policy": {"max_positions_per_symbol": 1, "daily_loss_limit_pct": 3.0,
                                      "max_drawdown_pct": 8.0, "session_risk_cap_pct": 1.5,
                                      "max_open_positions": 8, "min_margin_level_pct": 200.0}})
    gate.start_day(100_000.0)
    from david_sling.core.schemas import OrderIntent, OrderSide, OrderType
    from david_sling.core.utils import new_id

    def intent():
        return OrderIntent(intent_id=new_id("t"), symbol="EURUSD", side=OrderSide.BUY,
                           order_type=OrderType.MARKET, volume=0.01, idempotency_key=new_id("ik"),
                           ts=utc_now())
    acct = {"balance": 100_000.0, "equity": 100_000.0, "margin": 0.0, "margin_level_pct": 10_000.0}
    pos = [{"symbol": "EURUSD", "volume": 0.01, "side": "BUY", "entry_price": 1.1, "unrealized_pnl": 0.0}]
    d = gate.evaluate(intent(), account=acct, open_positions=pos, symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=False)
    assert not d.approved and any("per symbol" in r for r in d.reasons)


# ---------------------------------------------------------------- batch B+C
def test_G37_invalidation_marks_failure():
    from david_sling.core.schemas import HypothesisStateValue, ScenarioId, ScenarioState
    from david_sling.hypothesis.engine import HypothesisEngine

    h = HypothesisEngine()
    fs = FeatureSet(symbol="EURUSD", ts=utc_now(), price=1.10, spread_points=2.0, session="LONDON")
    fs.displacement_up = True
    fs.swing_low_h1 = 1.09
    fs.atr_m1 = 0.001
    scen = ScenarioState(scenario=ScenarioId.S1, family="trend", confidence=0.8, ts=utc_now())
    st = h.build(fs, scen)
    assert st.direction == "bullish" and st.invalidation_price == 1.09
    assert h.check_invalidation("EURUSD", 1.095) is False
    assert h.check_invalidation("EURUSD", 1.085) is True
    assert h.get("EURUSD").state == HypothesisStateValue.FAILURE


def test_G34_forward_probabilities():
    from david_sling.core.schemas import FusionSnapshot
    from david_sling.intelligence.forecast import HORIZONS, forward_probabilities

    fs = FeatureSet(symbol="EURUSD", ts=utc_now(), price=1.10, spread_points=2.0, session="LONDON")
    fs.atr_m1 = 0.0005
    long_f = FusionSnapshot(symbol="EURUSD", layers={"H4": 0.8}, convergence=0.9, direction="long",
                            conflicts=0, ts=utc_now())
    short_f = FusionSnapshot(symbol="EURUSD", layers={"H4": -0.8}, convergence=0.9, direction="short",
                             conflicts=0, ts=utc_now())
    neutral = FusionSnapshot(symbol="EURUSD", layers={}, convergence=0.0, direction="neutral",
                             conflicts=0, ts=utc_now())
    pl = forward_probabilities(fs, long_f)
    ps = forward_probabilities(fs, short_f)
    pn = forward_probabilities(fs, neutral)
    assert set(pl) == set(HORIZONS)
    assert all(0.01 <= v <= 0.99 for v in pl.values())
    assert pl["1H"] > 0.5 > ps["1H"]
    assert abs(pn["1H"] - 0.5) < 0.05
    assert pl["8H"] >= pl["5m"] and pl["5m"] > 0.5  # drift accumulates with horizon


def test_G35_per_engine_context_gate():
    from david_sling.engines.supervisor import EngineSupervisor

    sup = EngineSupervisor()
    from david_sling.core.schemas import (
        FusionSnapshot,
        ScenarioId,
        ScenarioState,
        ValidationResult,
    )
    from david_sling.strategies.vault import SetupCandidate

    cand = SetupCandidate(strategy_id="S01", family="trend", direction="long", engines=("A", "D"),
                          entry=1.10, stop_loss=1.09, take_profit=1.13, risk_reward=2.0, confidence=0.9)
    scen = ScenarioState(scenario=ScenarioId.S1, family="trend", confidence=0.9, ts=utc_now())
    val = ValidationResult(passed=True, pa_score=0.9, cdt_score=0.9, indicator_score=0.9, weighted=0.9)
    bear_macro = FusionSnapshot(symbol="EURUSD", layers={"W1": -0.9, "MN1": -0.9, "D1": -0.9},
                                convergence=0.9, direction="long", conflicts=0, ts=utc_now())
    d = sup.qualify("D", cand, scen, val, bear_macro)
    assert not d.qualified and any("context" in r for r in d.reasons)
    a = sup.qualify("A", cand, scen, val, bear_macro)  # A's context (H4/H1/M30) absent -> no veto
    assert a.qualified


def test_G39_drift_consumption():
    from david_sling.monitoring_learning.engine import MonitoringEngine

    m = MonitoringEngine()

    class T:
        pnl = 1.0

    for _ in range(20):
        m.record_outcome("S01", T())
    for _ in range(20):
        T.pnl = -1.0
        m.record_outcome("S01", T())
    assert m.active_drift_strategies() == {"S01"}
    m.mark_drift_consumed()
    assert m.active_drift_strategies() == set()


def test_G43_news_calendar():
    from datetime import datetime

    from david_sling.data.news_calendar import is_high_impact

    assert is_high_impact(datetime(2026, 11, 6, 13, 30)) is True          # first Friday = NFP
    assert is_high_impact(datetime(2026, 11, 2, 10, 0)) is False          # Monday morning
    assert is_high_impact(datetime(2026, 11, 11, 18, 30)) is True         # FOMC Wed mid-month
    assert is_high_impact(datetime(2026, 1, 28, 13, 40), ["2026-01-28 13:30"]) is True
    assert is_high_impact(datetime(2026, 1, 28, 20, 0), ["2026-01-28 13:30"]) is False


def test_G47_calibrated_confidence():
    from david_sling.monitoring_learning.engine import MonitoringEngine

    m = MonitoringEngine()
    assert m.calibrated_confidence("S99", 0.7) == 0.7  # <10 trades -> base

    class T:
        pnl = 1.0

    for _ in range(20):  # 100% wins -> confidence rises, clamped <= 0.99
        m.record_outcome("S01", T())
    cal = m.calibrated_confidence("S01", 0.6)
    assert cal > 0.6 and cal <= 0.99
    for _ in range(20):  # now losing -> win rate drops to 50%
        T.pnl = -1.0
        m.record_outcome("S01", T())
    cal2 = m.calibrated_confidence("S01", 0.6)
    assert cal2 < cal


def test_G57_no_index_error_on_short_candle_sets():
    """Round-9 regression: 'pipeline error: list index out of range' fired once H1 crossed
    30 bars (atr_pct_h1 off-by-one) and on empty TF lists (atr()). Fuzz degenerate inputs."""
    import random
    from datetime import datetime, timedelta

    from david_sling.core.schemas import TF_MINUTES, Candle, Timeframe
    from david_sling.intelligence.features import atr, compute_features

    assert atr([]) == []
    rng = random.Random(7)
    base = datetime(2026, 1, 5, tzinfo=UTC)
    for _ in range(400):
        cb = {}
        for tf in Timeframe:
            n = rng.choice([0, 1, 2, 3, 5, 10, 31, 35, 60, 120])
            bars, p = [], 1.1
            for i in range(n):
                o = p
                p *= 1 + rng.uniform(-0.002, 0.002)
                bars.append(Candle(symbol="EURUSD", tf=tf,
                                   open_time=base + timedelta(minutes=i * TF_MINUTES[tf]),
                                   open=o, high=max(o, p) + 1e-5, low=min(o, p) - 1e-5,
                                   close=p, volume=rng.uniform(1, 100)))
            cb[tf] = bars
        compute_features("EURUSD", base, 1.1, 2.0, "LONDON", cb, deltas=[0.1], news_repricing=True)
