"""Risk gate (1.50% session cap, hard veto) & sizing (broker min lot) tests."""
from __future__ import annotations

from david_sling.core.schemas import OrderIntent, OrderSide, SymbolSpec
from david_sling.core.utils import utc_now
from david_sling.risk.gate import RiskGate
from david_sling.sizing.engine import SizingEngine

CFG = {"risk_policy": {"session_risk_cap_pct": 1.50, "risk_per_trade_pct": 1.00,
                       "daily_loss_limit_pct": 3.00, "max_drawdown_pct": 8.00,
                       "max_open_positions": 2, "max_positions_per_symbol": 1,
                       "min_margin_level_pct": 200.0, "news_blackout": True},
       "exposure_policy": {"per_currency_exposure_limit_pct": 25.0, "total_exposure_limit_pct": 60.0},
       "circuit_breaker": {"atr_spike_mult": 3.0, "spread_widen_mult": 4.0}}

SPEC = SymbolSpec(name="EURUSD", digits=5, tick_size=0.00001, tick_value=10.0,
                  contract_size=100000, min_lot=0.01, lot_step=0.01, max_lot=20.0)


def intent(symbol="EURUSD", side=OrderSide.BUY, volume=0.1, sl=1.0990):
    return OrderIntent(intent_id="t1", symbol=symbol, side=side, volume=volume, stop_loss=sl,
                       idempotency_key="k1", ts=utc_now())


def account(equity=100000.0, balance=100000.0):
    return {"equity": equity, "balance": balance, "margin": 0.0, "margin_level_pct": 10000.0}


def test_risk_approves_normal_trade():
    gate = RiskGate(CFG)
    gate.start_day(100000.0)
    d = gate.evaluate(intent(), account=account(), open_positions=[], symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0)
    assert d.approved, d.reasons


def test_risk_vetoes_on_news_blackout():
    gate = RiskGate(CFG)
    gate.start_day(100000.0)
    d = gate.evaluate(intent(), account=account(), open_positions=[], symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=True)
    assert not d.approved and any("blackout" in r for r in d.reasons)


def test_risk_vetoes_daily_loss_limit():
    gate = RiskGate(CFG)
    gate.start_day(100000.0)
    d = gate.evaluate(intent(), account=account(balance=96000.0), open_positions=[], symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0)
    assert not d.approved and any("daily loss" in r for r in d.reasons)


def test_risk_vetoes_position_cap_and_circuit_breaker():
    gate = RiskGate(CFG)
    gate.start_day(100000.0)
    open_pos = [{"symbol": "EURUSD", "risk_amount": 500.0}] * 2
    d = gate.evaluate(intent(), account=account(), open_positions=open_pos, symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0)
    assert not d.approved
    d2 = gate.evaluate(intent(), account=account(), open_positions=[], symbol_exposure={},
                       atr_now=0.01, atr_avg=0.001, spread_now=2.0, spread_avg=2.0)
    assert not d2.approved and any("ATR spike" in r for r in d2.reasons)


def test_sizing_respects_broker_min_lot_and_step():
    sz = SizingEngine({"lot_policy": {"mode": "risk_based", "kelly_fraction_cap": 0.25,
                                       "max_lot_cap": 20.0, "enforce_broker_min_lot": True}})
    lot = sz.lots_for_risk(SPEC, risk_amount=100.0, sl_distance=0.0010)
    assert lot >= SPEC.min_lot
    assert abs(lot / SPEC.lot_step - round(lot / SPEC.lot_step)) < 1e-9  # on lot_step grid
    tiny = sz.lots_for_risk(SPEC, risk_amount=0.01, sl_distance=0.5)
    assert tiny == 0.0 or tiny >= SPEC.min_lot
    big = sz.lots_for_risk(SPEC, risk_amount=1e9, sl_distance=0.0001)
    assert big <= SPEC.max_lot
