"""End-to-end: boot runtime (sim feed), run pipeline, exercise API + trades."""
from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def runtime():
    from david_sling.bootstrap.david_os_boot import DavidOSBoot

    rt = asyncio.run(DavidOSBoot(mode="sim").run(feed=True))
    asyncio.run(asyncio.sleep(2.5))  # let the feed produce ticks/candles
    yield rt
    asyncio.run(rt.stop())


def test_boot_status(runtime):
    assert "mode=sim" in runtime.status_summary()
    assert runtime.ledger.verify_chain()


def test_pipeline_produced_features_and_ledger_entries(runtime):
    assert runtime.sim.tick_count > 0
    assert runtime.intelligence.last_features  # features computed for symbols
    assert len(runtime.ledger) > 0


def test_api_endpoints(runtime):
    from david_sling.api.app import create_app

    app = create_app(runtime)
    # bypass lifespan (runtime already started)
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"
    assert client.get("/api/mission-control/overview").status_code == 200
    ov = client.get("/api/mission-control/overview").json()
    assert ov["brand"] == "DAVID SLING"
    assert len(ov["health"]) == 15
    assert client.get("/api/strategies").json()["count"] == 52
    assert client.get("/api/engines").status_code == 200
    assert client.get("/api/market/EURUSD/candles?tf=M1").status_code == 200
    assert client.get("/api/evidence/status").json()["chain_ok"] is True


def test_manual_trade_flow_open_close(runtime):
    from david_sling.api.app import create_app

    app = create_app(runtime)
    client = TestClient(app)
    # open a manual trade through the full L10->L11->L12 path
    r = client.post("/api/trade/single", json={
        "symbol": "EURUSD", "side": "BUY", "order_type": "MARKET",
        "volume": 0.10, "sl": 1.0000, "tp": 1.2000, "risk_pct": 0.5})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"], body
    pos_id = body["orders"][0]["position_id"]
    assert pos_id in runtime.broker.account.positions
    # positions visible via API
    positions = client.get("/api/trade/positions").json()["positions"]
    assert any(p["position_id"] == pos_id for p in positions)
    # partial close 50%
    r2 = client.post("/api/trade/close", json={"position_id": pos_id, "pct": 0.5})
    assert r2.json()["closed"] is True
    # full close
    r3 = client.post("/api/trade/close", json={"position_id": pos_id})
    assert r3.json()["closed"] is True
    assert pos_id not in runtime.broker.account.positions
    # panic flatten is safe when flat
    r4 = client.post("/api/trade/panic-flatten", json={})
    assert r4.json()["flattened"] >= 0


def test_cross_pair_basket_and_pnl_matrix(runtime):
    from david_sling.api.app import create_app

    app = create_app(runtime)
    client = TestClient(app)
    r = client.post("/api/trade/cross-pair-basket", json={
        "symbols": ["EURUSD", "XAUUSD"], "side": "BUY", "lots": 0.05, "sl_atr_mult": 2.0, "tp_rr": 2.0})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"], body
    assert len(body["orders"]) == 2
    matrix = client.get("/api/mission-control/pnl-matrix").json()["matrix"]
    assert any(m["symbol"] == "EURUSD" and m["open_positions"] >= 1 for m in matrix)
    # correlated basket guard: same symbol twice must be rejected by correlation guard
    r2 = client.post("/api/trade/cross-pair-basket", json={
        "symbols": ["EURUSD", "EURUSD"], "side": "BUY", "lots": 0.05})
    assert r2.json()["ok"] is False
