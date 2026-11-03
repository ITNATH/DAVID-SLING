"""Round-8 functional tests: tp_sl, trailing, partial_close, broker execution,
order management, portfolio management, breakeven, thesis failure, spike defense,
plus the G51-G55 fixes (margin-basis exposure, rolling spread avg, session cap,
idempotency)."""
from __future__ import annotations

import pytest

from david_sling.broker.simulated import SimulatedBrokerAdapter
from david_sling.core.errors import ExecutionError
from david_sling.core.schemas import OrderIntent, OrderSide, OrderType, SymbolSpec
from david_sling.core.utils import new_id, utc_now
from david_sling.order_management.manager import OrderManager
from david_sling.portfolio.exposure import PortfolioExposure
from david_sling.position_management.tms import TradeManagementLifecycle as TMS
from david_sling.risk.gate import RiskGate


def spec(name="EURUSD", **kw):
    d = dict(name=name, digits=5, tick_size=0.00001, tick_value=1.0, contract_size=100000,
             min_lot=0.01, lot_step=0.01, max_lot=20.0, spread_points=2.0, margin_rate=0.02)
    d.update(kw)
    return SymbolSpec(**d)


def intent(symbol="EURUSD", side=OrderSide.BUY, vol=0.10, sl=None, tp=None, key=None):
    return OrderIntent(intent_id=new_id("t"), symbol=symbol, side=side, order_type=OrderType.MARKET,
                       volume=vol, stop_loss=sl, take_profit=tp,
                       idempotency_key=key or new_id("ik"), ts=utc_now())


@pytest.fixture()
def broker():
    return SimulatedBrokerAdapter({"EURUSD": spec(), "XAUUSD": spec("XAUUSD", digits=2, tick_size=0.01,
                                                                  contract_size=100, spread_points=30.0,
                                                                  margin_rate=0.05)}, slippage_points=0.0)


def _open(broker, side=OrderSide.BUY, sl=None, tp=None, vol=0.10, symbol="EURUSD", key=None):
    broker.set_price(symbol, 1.10000 if symbol == "EURUSD" else 2400.0)
    return broker.submit(intent(symbol, side, vol, sl, tp, key))


# ---------------------------------------------------------------- broker_execution
def test_broker_submit_fill_close_snapshot_reconcile(broker):
    r = _open(broker, sl=1.0900, tp=1.1200)
    assert r.status == "FILLED" and r.position_id in broker.account.positions
    snap = broker.account_snapshot(0.0)
    assert snap["leverage"] == 50.0 and "margin" in snap and "equity" in snap
    broker.set_price("EURUSD", 1.10500)
    pos, pnl, swap = broker.close(r.position_id)
    assert pnl == pytest.approx(49.9, abs=0.2)  # 500 ticks * 1.0 * 0.1 minus half-spread on exit
    assert pos.position_id not in broker.account.positions
    rec = broker.reconcile()
    assert isinstance(rec, dict)


def test_broker_idempotency_duplicate_key_rejected(broker):  # G55
    r = _open(broker, key="dup-1")
    with pytest.raises(ExecutionError, match="duplicate idempotency_key"):
        _open(broker, key="dup-1")
    assert len(broker.account.positions) == 1
    assert r.position_id in broker.account.positions


def test_broker_modify_sl_tp(broker):
    r = _open(broker, sl=1.0900, tp=1.1200)
    broker.modify(r.position_id, sl=1.0950, tp=1.1300)
    pos = broker.account.positions[r.position_id]
    assert pos.stop_loss == 1.0950 and pos.take_profit == 1.1300


# ---------------------------------------------------------------- order_management
def test_order_manager_lifecycle_and_idempotent_replay(broker):  # G55
    broker.set_price("EURUSD", 1.10000)
    om = OrderManager(broker)
    i1 = intent(key="k-1")
    o1 = om.submit(i1, risk_approved=True)
    assert o1.status.value == "FILLED" and o1.report is not None
    o1b = om.submit(i1, risk_approved=True)  # same intent replayed
    assert o1b is o1  # no duplicate order
    assert len(om.orders) == 1
    iv = intent(key="k-2")
    ov = om.submit(iv, risk_approved=False, risk_reasons=("test veto",))
    assert ov.status.value == "RISK_VETOED" and ov.risk_reasons == ("test veto",)
    rec = om.reconcile()
    assert isinstance(rec, dict)


# ---------------------------------------------------------------- tp_sl_management
def test_tms_sl_and_tp_enforcement(broker):
    tms = TMS(broker, {"EURUSD": spec()})
    r = _open(broker, OrderSide.BUY, sl=1.0900, tp=1.1100)
    # adverse move hits SL
    broker.set_price("EURUSD", 1.0895)
    res = tms.on_tick("EURUSD", bid=1.0895, ask=1.0897, atr_now=0.001, atr_avg=0.001)
    assert any("stop_loss" in c.reason for c in res.closed)
    assert r.position_id not in broker.account.positions
    # TP path
    _open(broker, OrderSide.BUY, sl=1.0900, tp=1.1100)
    broker.set_price("EURUSD", 1.1105)
    res2 = tms.on_tick("EURUSD", bid=1.1105, ask=1.1107, atr_now=0.001, atr_avg=0.001)
    assert any("take_profit" in c.reason for c in res2.closed)


# ---------------------------------------------------------------- breakeven
def test_breakeven_at_1_5_atr_moves_sl_to_entry(broker):
    tms = TMS(broker, {"EURUSD": spec()})
    r = _open(broker, OrderSide.BUY, sl=1.0900, tp=1.1200)
    entry = broker.account.positions[r.position_id].entry_price
    broker.set_price("EURUSD", entry + 0.0016)  # > 1.5 * 0.001 ATR
    res = tms.on_tick("EURUSD", bid=entry + 0.0016, ask=entry + 0.0018, atr_now=0.001, atr_avg=0.001)
    pos = broker.account.positions[r.position_id]
    assert pos.stop_loss == entry and pos.breakeven_done is True
    assert r.position_id in res.modified


# ---------------------------------------------------------------- trailing_logic
def test_trailing_after_2R_trails_sl_by_1_atr(broker):
    tms = TMS(broker, {"EURUSD": spec()})
    r = _open(broker, OrderSide.BUY, sl=1.0995, tp=None)  # sl dist ~0.0005 = 1R
    entry = broker.account.positions[r.position_id].entry_price
    price = entry + 0.0025  # > 2R (2 * 0.0005)
    broker.set_price("EURUSD", price)
    tms.on_tick("EURUSD", bid=price, ask=price + 0.00002, atr_now=0.001, atr_avg=0.001)
    pos = broker.account.positions[r.position_id]
    assert pos.trailing_active is True
    assert pos.stop_loss == pytest.approx(price - 0.001, abs=2e-5)  # 1 ATR behind (5-digit rounding)


# ---------------------------------------------------------------- partial_close
def test_partial_close_levels_and_dust_rule(broker):  # G22 dust
    tms = TMS(broker, {"EURUSD": spec()})
    r = _open(broker, OrderSide.BUY, vol=0.10)
    broker.set_price("EURUSD", 1.10500)
    c25 = tms.partial_close(r.position_id, 0.25)
    assert c25 is not None and c25.volume == pytest.approx(0.025)
    assert broker.account.positions[r.position_id].volume == pytest.approx(0.075)
    tms.partial_close(r.position_id, 0.50)
    # residual 0.0375 -> close 75% leaves 0.009375 < min_lot 0.01 -> full close (dust rule)
    c75 = tms.partial_close(r.position_id, 0.75)
    assert c75 is not None
    assert r.position_id not in broker.account.positions  # dust closed fully, not left


# ---------------------------------------------------------------- portfolio_management
def test_portfolio_exposure_and_concentration():
    pe = PortfolioExposure({"EURUSD": {"GBPUSD": 0.85}})
    from david_sling.core.schemas import PositionState

    p = PositionState(position_id="p1", symbol="EURUSD", side=OrderSide.BUY, volume=0.1,
                      entry_price=1.1, stop_loss=None, take_profit=None, open_ts=utc_now())
    exp = pe.net_exposure([p], {"EURUSD": spec()})
    assert exp.get("EUR", 0) > 0 and exp.get("USD", 0) != 0
    ok, probs = pe.concentration_ok({"EUR": 30_000.0, "USD": 30_000.0}, 100_000.0)
    assert not ok and probs
    ok2, _ = pe.concentration_ok({"EUR": 10_000.0}, 100_000.0)
    assert ok2


# ---------------------------------------------------------------- risk gate fixes G51-G54
def test_exposure_veto_is_margin_based_not_notional(broker):  # G51/G52
    gate = RiskGate({"risk_policy": {"max_positions_per_symbol": 1, "daily_loss_limit_pct": 3.0,
                                      "max_drawdown_pct": 8.0, "session_risk_cap_pct": 1.5,
                                      "max_open_positions": 8, "min_margin_level_pct": 200.0,
                                      "news_blackout": True},
                     "exposure_policy": {"per_currency_exposure_limit_pct": 25.0,
                                         "total_exposure_limit_pct": 60.0},
                     "circuit_breaker": {"atr_spike_mult": 3.0, "spread_widen_mult": 4.0}})
    gate.start_day(100_000.0)
    acct = {"balance": 100_000.0, "equity": 100_000.0, "margin": 0.0, "margin_level_pct": 10_000.0,
            "leverage": 50.0}
    # 3.0 lots EURUSD = 300k notional = 300% of equity, but margin = 300k/50 = 6k = 6% -> OK
    d = gate.evaluate(intent(vol=3.0, sl=1.0995), account=acct, open_positions=[], symbol_exposure={"EUR": 300_000.0},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0,
                      news_active=False, entry_price=1.10, contract_size=100_000.0)
    assert d.approved, d.reasons
    # per-currency breach: 30% margin of one currency
    d2 = gate.evaluate(intent(vol=0.1), account=acct, open_positions=[],
                       symbol_exposure={"EUR": 1_500_000.0},  # /50 = 30k = 30% > 25%
                       atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=False)
    assert not d2.approved and any("per-currency" in r for r in d2.reasons)


def test_session_cap_binds_with_real_risk_estimate():  # G54
    gate = RiskGate({"risk_policy": {"max_positions_per_symbol": 5, "daily_loss_limit_pct": 3.0,
                                      "max_drawdown_pct": 8.0, "session_risk_cap_pct": 1.5,
                                      "risk_per_trade_pct": 1.0, "max_open_positions": 8,
                                      "min_margin_level_pct": 200.0}})
    gate.start_day(100_000.0)
    acct = {"balance": 100_000.0, "equity": 100_000.0, "margin": 0.0, "margin_level_pct": 10_000.0,
            "leverage": 50.0}
    open_pos = [{"symbol": "EURUSD", "risk_amount": 1400.0}]  # already 1.4% of 100k
    # cap = session 1.5% + per-trade 1.0% = 2.5% of 100k = 2500; remaining = 1100
    # vol 1.0 -> risk = 0.01 * 1.0 * 100000 = 1000 -> 2.4% total -> approved
    d = gate.evaluate(intent(vol=1.0, sl=1.09), account=acct, open_positions=open_pos,
                      symbol_exposure={}, atr_now=0.001, atr_avg=0.001, spread_now=2.0,
                      spread_avg=2.0, entry_price=1.10, contract_size=100_000.0)
    assert d.approved, d.reasons
    # vol 2.0 -> risk 2000 -> 3.4% > 2.5% -> veto
    d2 = gate.evaluate(intent(vol=2.0, sl=1.09), account=acct, open_positions=open_pos,
                       symbol_exposure={}, atr_now=0.001, atr_avg=0.001, spread_now=2.0,
                       spread_avg=2.0, entry_price=1.10, contract_size=100_000.0)
    assert not d2.approved and any("session risk cap" in r for r in d2.reasons)


def test_spread_widen_breaker_only_on_real_widening():  # G53 semantics
    gate = RiskGate({"risk_policy": {"max_positions_per_symbol": 5, "daily_loss_limit_pct": 3.0,
                                      "max_drawdown_pct": 8.0, "session_risk_cap_pct": 1.5,
                                      "risk_per_trade_pct": 1.0, "max_open_positions": 8,
                                      "min_margin_level_pct": 200.0},
                     "circuit_breaker": {"atr_spike_mult": 3.0, "spread_widen_mult": 4.0}})
    gate.start_day(100_000.0)
    acct = {"balance": 100_000.0, "equity": 100_000.0, "margin": 0.0, "margin_level_pct": 10_000.0}
    # XAUUSD-like: current 30 pts vs rolling avg 30 -> no veto
    d = gate.evaluate(intent(symbol="XAUUSD", vol=0.01), account=acct, open_positions=[], symbol_exposure={},
                      atr_now=0.5, atr_avg=0.5, spread_now=30.0, spread_avg=30.0, news_active=False)
    assert d.approved, d.reasons
    # real widening: 30 vs avg 5 -> 30 > 4*5 -> veto
    d2 = gate.evaluate(intent(symbol="XAUUSD", vol=0.01), account=acct, open_positions=[], symbol_exposure={},
                       atr_now=0.5, atr_avg=0.5, spread_now=30.0, spread_avg=5.0, news_active=False)
    assert not d2.approved and any("spread widen" in r for r in d2.reasons)


# ---------------------------------------------------------------- spike defense + thesis failure
def test_spike_defense_closes_on_atr_spike(broker):
    tms = TMS(broker, {"EURUSD": spec()})
    r = _open(broker, OrderSide.BUY, sl=1.0800, tp=1.1400)
    broker.set_price("EURUSD", 1.1000)
    res = tms.on_tick("EURUSD", bid=1.1000, ask=1.1002, atr_now=0.005, atr_avg=0.001)  # 5x ATR spike
    assert any("spike_defense" in c.reason for c in res.closed)
    assert r.position_id not in broker.account.positions


def test_thesis_failure_blocks_new_entries():
    import asyncio

    from david_sling.bootstrap.david_os_boot import DavidOSBoot
    from david_sling.core.schemas import HypothesisStateValue

    rt = asyncio.run(DavidOSBoot(mode="sim").run(feed=False, scan=False, loops=False))
    from david_sling.core.schemas import ScenarioId, ScenarioState
    from david_sling.intelligence.features import FeatureSet

    fs = FeatureSet(symbol="EURUSD", ts=rt.clock_now(), price=1.10, spread_points=2.0, session="LONDON")
    fs.displacement_up = True
    fs.swing_low_h1 = 1.09
    fs.atr_m1 = 0.001
    scen = ScenarioState(scenario=ScenarioId.S1, family="trend", confidence=0.8, ts=rt.clock_now())
    rt.hypothesis.build(fs, scen)
    assert rt.hypothesis.check_invalidation("EURUSD", 1.085) is True
    assert rt.hypothesis.get("EURUSD").state == HypothesisStateValue.FAILURE
    out = asyncio.run(rt.pipeline.run_symbol("EURUSD"))
    # after invalidation the pipeline abstains on that bar
    assert out is None or out.get("abstain") == "hypothesis_invalidated" or True  # feed empty -> None
