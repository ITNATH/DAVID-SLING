"""Regression tests for audit deep-pass fixes (G1,G2,G11-G22)."""
from datetime import UTC, datetime

import pytest

from david_sling.broker.adapter import BrokerRegistry
from david_sling.broker.fix_adapter import build_message, parse_message
from david_sling.broker.simulated import SimulatedBrokerAdapter
from david_sling.core.errors import ExecutionError, SecurityError
from david_sling.core.schemas import OrderIntent, OrderSide, OrderType, SymbolSpec
from david_sling.core.utils import new_id, utc_now
from david_sling.data.store import DataStore
from david_sling.intelligence.features import FeatureSet
from david_sling.intelligence.fibonacci import (
    in_golden_zone,
    ote_signal,
    retracement_ratio,
)
from david_sling.monitoring_learning.engine import MonitoringEngine
from david_sling.portfolio.exposure import PortfolioExposure
from david_sling.risk.gate import RiskGate
from david_sling.strategies.vault import _s18


def spec(name, **kw):
    d = dict(name=name, digits=5, tick_size=0.00001, tick_value=1.0, contract_size=100000,
             min_lot=0.01, lot_step=0.01, max_lot=20.0, spread_points=0.0, margin_rate=0.02)
    d.update(kw)
    return SymbolSpec(**d)


def intent(symbol, side=OrderSide.BUY, volume=0.10):
    return OrderIntent(intent_id=new_id("t"), symbol=symbol, side=side, order_type=OrderType.MARKET,
                       volume=volume, idempotency_key=new_id("ik"), ts=utc_now())


# ---------------------------------------------------------------- G11: PnL golden values
def test_pnl_golden_per_symbol():
    specs = {
        "EURUSD": spec("EURUSD"),
        "USDJPY": spec("USDJPY", digits=3, tick_size=0.001, tick_value=100.0, currency_profit="JPY"),
        "XAUUSD": spec("XAUUSD", digits=2, tick_size=0.01, tick_value=1.0, contract_size=100, max_lot=10.0),
    }
    b = SimulatedBrokerAdapter(specs, slippage_points=0.0)
    # EURUSD: 0.10 lot, +10 pips (1.10000->1.10100) = 1000 ticks * 1.0 USD/tick * 0.1 = 10.00 USD
    b.set_price("EURUSD", 1.10000)
    r = b.submit(intent("EURUSD"))
    b.set_price("EURUSD", 1.10100)
    assert b.close(r.position_id)[1] == pytest.approx(10.00, abs=0.01)
    # USDJPY: 0.10 lot, +10 pips = 100 ticks * 100 JPY * 0.1 = 1000 JPY / 150 = 6.67 USD
    b.set_price("USDJPY", 150.000)
    r = b.submit(intent("USDJPY"))
    b.set_price("USDJPY", 150.100)
    assert b.close(r.position_id)[1] == pytest.approx(1000 / 150, abs=0.02)
    # XAUUSD: 0.05 lot, +$1.00 = 100 ticks * 1.0 * 0.05 = 5.00 USD
    b.set_price("XAUUSD", 2400.00)
    r = b.submit(intent("XAUUSD", volume=0.05))
    b.set_price("XAUUSD", 2401.00)
    assert b.close(r.position_id)[1] == pytest.approx(5.00, abs=0.01)


def test_sizing_with_per_tick_value():
    from david_sling.sizing.engine import SizingEngine

    sz = SizingEngine({})
    eurusd = spec("EURUSD")
    # risk 500 USD, SL 50 pips = 500 ticks * 1.0 USD/tick = 500 USD per lot -> 1.0 lot
    lot = sz.lots_for_risk(eurusd, 500.0, 0.0050)
    assert lot == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------- G13: halt / resume
def test_halt_vetoes_everything_until_resume():
    gate = RiskGate({})
    gate.start_day(100_000.0)
    acct = {"balance": 100_000.0, "equity": 100_000.0, "margin": 0.0, "margin_level_pct": 10_000.0}
    d = gate.evaluate(intent("EURUSD"), account=acct, open_positions=[], symbol_exposure={},
                      atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=False)
    assert d.approved
    gate.halt("test halt")
    d2 = gate.evaluate(intent("EURUSD"), account=acct, open_positions=[], symbol_exposure={},
                       atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=False)
    assert not d2.approved and "HALT" in d2.reasons[0]
    gate.resume()
    d3 = gate.evaluate(intent("EURUSD"), account=acct, open_positions=[], symbol_exposure={},
                       atr_now=0.001, atr_avg=0.001, spread_now=2.0, spread_avg=2.0, news_active=False)
    assert d3.approved


# ---------------------------------------------------------------- G1: fibonacci / OTE
def _candle(ts_min: int, o: float, h: float, lo: float, c: float):
    from david_sling.core.schemas import Candle, Timeframe

    base = datetime(2026, 1, 5, tzinfo=UTC)
    from datetime import timedelta

    t = base + timedelta(minutes=ts_min * 240)
    return Candle(symbol="EURUSD", tf=Timeframe.H4, open_time=t, open=o, high=h, low=lo, close=c,
                  volume=1000.0, tick_count=240)


def test_golden_zone_detection():
    assert retracement_ratio(1.1000, 1.0900, 1.0930) == pytest.approx(0.70)
    assert in_golden_zone(1.1000, 1.0900, 1.0930)          # 70% retracement -> in zone
    assert not in_golden_zone(1.1000, 1.0900, 1.0990)      # 10% -> not in zone
    candles = [_candle(i, 1.09, 1.10 if i == 49 else 1.095, 1.09, 1.095) for i in range(50)]
    candles.append(_candle(50, 1.093, 1.0935, 1.0925, 1.0930))
    sig = ote_signal(candles, trend_up=True)
    assert sig["long_ote"] is True
    assert sig["retracement"] == pytest.approx(0.70, abs=0.01)


def test_s18_uses_true_OTE():
    fs = FeatureSet(symbol="EURUSD", ts=utc_now(), price=1.0930, spread_points=2.0, session="LONDON")
    fs.trend_h4 = 1
    fs.rsi_m1 = 40.0
    fs.ote_long_h4 = True
    fs.atr_m1 = 0.001
    cand = _s18(fs, "long")
    assert cand is not None and cand.strategy_id == "S18"
    fs.ote_long_h4 = False
    assert _s18(fs, "long") is None


# ---------------------------------------------------------------- G2: adapters
def test_registry_simulated_default_and_unknown():
    b = BrokerRegistry.create({"type": "simulated"}, {})
    assert isinstance(b, SimulatedBrokerAdapter)
    with pytest.raises(ExecutionError):
        BrokerRegistry.create({"type": "quantum"}, {})


def test_mt5_connect_requires_credentials(monkeypatch):
    from david_sling.broker.mt5_adapter import Mt5Adapter

    for k in ("DAVID_SLING_MT5_LOGIN", "DAVID_SLING_MT5_PASSWORD", "DAVID_SLING_MT5_SERVER"):
        monkeypatch.delenv(k, raising=False)
    a = Mt5Adapter({}, {"type": "mt5"})
    try:
        import MetaTrader5  # noqa: F401
        with pytest.raises(SecurityError):
            a.connect()
    except ImportError:
        with pytest.raises(ExecutionError):
            a.connect()


def test_fix_message_roundtrip_and_checksum():
    msg = build_message("D", {11: "abc", 55: "EURUSD", 54: "1", 38: "0.10"}, 7, "DAVIDSLING", "BROKER")
    f = parse_message(msg)
    assert f[35] == "D" and f[11] == "abc" and f[55] == "EURUSD" and f[34] == "7"
    assert f[10] == f"{sum((msg.decode().split('10=')[0]).encode()) % 256:03d}"
    corrupted = msg.replace(b"38=0.10", b"38=0.20")
    with pytest.raises(ExecutionError):
        parse_message(corrupted)


# ---------------------------------------------------------------- G15: concentration guard wired
def test_concentration_ok_veto():
    pe = PortfolioExposure({"EURUSD": {"GBPUSD": 0.85}})
    ok, probs = pe.concentration_ok({"EUR": 30_000.0, "USD": 30_000.0}, equity=100_000.0)
    assert not ok and probs
    ok2, _ = pe.concentration_ok({"EUR": 10_000.0}, equity=100_000.0)
    assert ok2


# ---------------------------------------------------------------- G16: drift proposal
def test_concept_drift_proposal():
    m = MonitoringEngine()

    class T:
        pnl = 1.0

    for _ in range(20):
        m.record_outcome("S01", T())
    for _ in range(20):
        T.pnl = -1.0
        m.record_outcome("S01", T())
    assert any(p["type"] == "concept_drift" for p in m.proposals)
    s = m.summary()
    assert "dispatch" in s and s["dispatch"]["count"] == 0


# ---------------------------------------------------------------- G19: data store
def test_data_store_roundtrip(tmp_path):
    from david_sling.core.schemas import Tick

    st = DataStore(tmp_path)
    tick = Tick(symbol="EURUSD", ts=utc_now(), bid=1.1, ask=1.1002)
    st.append_tick(tick)
    rows = st.read_ticks("EURUSD")
    assert len(rows) == 1 and rows[0]["symbol"] == "EURUSD"
