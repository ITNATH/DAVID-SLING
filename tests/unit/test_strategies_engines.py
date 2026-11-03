"""Strategy vault (54 strategies / 9 families) and peer engine tests (A-D + G)."""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from david_sling.core.errors import BoundaryViolation
from david_sling.engines.supervisor import EngineSupervisor, peer_dependency_guard
from david_sling.intelligence.features import FeatureSet
from david_sling.strategies.vault import STRATEGY_VAULT


def _fs(**kw) -> FeatureSet:
    base = dict(symbol="EURUSD", ts=datetime(2026, 1, 5, 10, tzinfo=UTC), price=1.1000,
                spread_points=2.0, session="LONDON", atr_m1=0.001, ema20_m1=1.1001, ema50_m1=1.0990,
                vwap_m1=1.0999, range3_m1=0.003, trend_m1=1, trend_m15=1, trend_h1=1, trend_h4=1, trend_d1=1)
    base.update(kw)
    return FeatureSet(**base)


def test_vault_has_54_strategies_in_9_families():
    all_s = STRATEGY_VAULT.all()
    assert len(all_s) == 54
    families = {s.family for s in all_s}
    assert len(families) == 9
    assert [s.sid for s in all_s][:4] == ["S01", "S02", "S03", "S04"]
    assert all_s[-1].sid == "S54"


def test_strategies_fire_on_matching_patterns():
    fs = _fs(displacement_up=True, sweep_dn_m5=True, eql=True, volume_z_m1=2.0, rejection_dn=True)
    cands = STRATEGY_VAULT.evaluate(fs)
    ids = {c.strategy_id for c in cands}
    assert "S05" in ids          # turtle soup
    assert "S19" in ids          # quasimodo
    assert "S23" in ids          # wyckoff spring
    for c in cands:
        assert c.direction in ("long", "short")
        assert c.take_profit != c.entry


def test_peer_dependency_guard_blocks_engine_to_engine_import():
    peer_dependency_guard("david_sling.engines.quant_scalping")  # self ok
    with pytest.raises(BoundaryViolation):
        peer_dependency_guard("david_sling.engines.quant_scalping.tactical_intraday")


def test_five_engine_profiles():
    sup = EngineSupervisor()
    assert set(sup.profiles) == {"A", "B", "C", "D", "G"}
    assert sup.profiles["A"].horizon == "15M-30M"
    assert sup.profiles["D"].horizon == "8H-Daily"
    assert sup.profiles["G"].horizon == "1M-5M"  # Gamma HFT market-making
    h = sup.health()
    assert set(h) == {"A", "B", "C", "D", "G"}
