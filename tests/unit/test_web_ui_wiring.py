"""Official web UI (api/static) wiring audit: shell intact, every widget bound.

Covers the Milestone-B surgical additions on the web Command Center:
- /api/protection_status endpoint (News Filter / Breakeven / Spike Defence /
  Thesis Failure + halted + broker link)
- the 4 batch buttons + PANIC/HALT/RESUME present in BOTH operational modules
  (Single-Pair Multi and Cross-Pair Basket tabs)
- every JS $("id") reference exists in index.html; every /api literal in app.js
  maps to a real route
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

STATIC = Path(__file__).resolve().parents[2] / "src" / "david_sling" / "api" / "static"


def _html() -> str:
    return (STATIC / "index.html").read_text()


def _js() -> str:
    return (STATIC / "app.js").read_text()


# ---------------------------------------------------------------- static shell
def test_shell_structure_preserved():
    html = _html()
    for sec in ["topbar", "kpi-strip", "rail-left", "rail-center", "rail-right",
                "card-monitoring", "card-health", "card-signals", "card-globe",
                "card-market", "card-scenario", "card-fusion", "card-engines",
                "card-trade", "card-control", "card-positions", "card-chart", "console"]:
        assert f'id="{sec}"' in html, f"missing section {sec}"
    # the three omni-trade tabs
    for tab in ["tab-single", "tab-multi", "tab-basket"]:
        assert f'id="{tab}"' in html


def test_both_operational_modules_have_all_ops_buttons():
    html = _html()
    multi = html.split('id="tab-multi"')[1].split('id="tab-basket"')[0]
    basket = html.split('id="tab-basket"')[1].split('id="trade-result"')[0]
    for name, pane in [("multi", multi), ("basket", basket)]:
        for label in ["Close Losing", "Close Profitable", "Close All", "Break-Even All",
                      "PANIC FLATTEN", "EMERGENCY HALT", "RESUME TRADING"]:
            assert label in pane, f"{name} module missing {label}"
        # 4 batch buttons wired via data-batch in each module
        assert pane.count("data-batch") == 3, f"{name} module needs Close Losing/Profitable/All"
        # break-even + panic + halt + resume wired (id in multi, data-action in basket)
        assert ("btn-be-all" in pane) or ('data-action="be-all"' in pane)
        assert ("btn-panic" in pane) or ('data-action="panic"' in pane)
        assert ("btn-halt" in pane) or ('data-action="halt"' in pane)
        assert ("btn-resume" in pane) or ('data-action="resume"' in pane)


def test_protection_indicators_present_in_layout():
    html = _html()
    for pid in ["protections", "prot-news", "prot-be", "prot-spike", "prot-thesis"]:
        assert f'id="{pid}"' in html
    for label in ["News Filter", "Breakeven", "Spike Defence", "Thesis Failure"]:
        assert label in html


def test_every_js_id_ref_exists_in_html():
    html, js = _html(), _js()
    html_ids = set(re.findall(r'id="([^"]+)"', html))
    js_ids = set(re.findall(r'\$\("([^"]+)"\)', js))
    missing = js_ids - html_ids
    assert not missing, f"JS refs missing in HTML: {sorted(missing)}"


def test_js_api_literals_match_routes():
    js = _js()
    import importlib

    from david_sling.api.app import create_app  # noqa: F401  (import check only)

    routes = set()
    for mod in ["core", "market", "mission_control", "trade_execution", "analysis", "audit"]:
        m = importlib.import_module(f"david_sling.api.routers.{mod}")
        for r in getattr(m, "router", []).routes:
            routes.add(r.path)
    lits = set(re.findall(r'["\'`](/api/[^"\'`]*?)["\'`]', js))
    lits |= set(re.findall(r'`(/api/[^`]+)`', js))
    bad = []
    for f in lits:
        f2 = re.sub(r"\$\{[^}]+\}", "{x}", f).split("?")[0]
        if not any(re.sub(r"\{[^}]+\}", "{x}", p) == f2 for p in routes):
            bad.append(f)
    assert not bad, f"JS api literals without routes: {bad}"


def test_no_duplicate_ids_in_html():
    html = _html()
    ids = re.findall(r'id="([^"]+)"', html)
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate ids: {dupes}"


# ---------------------------------------------------------------- live API
@pytest.fixture(scope="module")
def runtime(tmp_path_factory):
    os.environ["DAVID_SLING_LEDGER_PATH"] = str(tmp_path_factory.mktemp("ledger") / "evidence_ledger.jsonl")
    from david_sling.bootstrap.david_os_boot import DavidOSBoot

    rt = asyncio.run(DavidOSBoot(mode="sim").run(feed=True))
    asyncio.run(asyncio.sleep(1.5))
    yield rt
    asyncio.run(rt.stop())


def test_api_protection_status_shape(runtime):
    from david_sling.api.app import create_app

    client = TestClient(create_app(runtime))
    r = client.get("/api/protection_status")
    assert r.status_code == 200
    d = r.json()
    for key in ["news_filter", "breakeven", "spike_defence", "thesis_failure", "halted", "broker"]:
        assert key in d, f"missing {key}"
    assert set(d["news_filter"]) == {"active", "seconds_left"}
    assert "trigger_atr_mult" in d["breakeven"] and "positions_armed" in d["breakeven"]
    assert "atr_spike_mult" in d["spike_defence"] and "per_symbol" in d["spike_defence"]
    assert "invalidations_total" in d["thesis_failure"]
    assert d["broker"]["mode"] == "sim" and d["broker"]["connected"] is True


def test_api_health_carries_broker(runtime):
    from david_sling.api.app import create_app

    client = TestClient(create_app(runtime))
    d = client.get("/api/health").json()
    assert d["status"] == "ok" and "broker" in d and "halted" in d


def test_trade_ops_endpoints_from_ui_payloads(runtime):
    """The exact payloads the UI sends must execute end-to-end."""
    from david_sling.api.app import create_app

    client = TestClient(create_app(runtime))
    r = client.post("/api/trade/single", json={
        "symbol": "EURUSD", "side": "BUY", "order_type": "MARKET",
        "volume": 0.10, "price": None, "sl": None, "tp": None, "risk_pct": 1.0})
    assert r.status_code == 200 and r.json()["ok"] is True
    r = client.post("/api/trade/single-pair-multi", json={
        "symbol": "GBPUSD", "side": "SELL", "tranches": 3, "lots": 0.05, "sl": None, "tp": None})
    assert r.status_code == 200 and r.json()["ok"] is True
    r = client.post("/api/trade/cross-pair-basket", json={
        "symbols": ["USDJPY"], "side": "BUY", "lots": 0.05, "sl_atr_mult": 1.5, "tp_rr": 2.0})
    assert r.status_code == 200  # may be vetoed by correlation guard - handled, not 500
    for payload in [{"only_losing": True, "symbol": "EURUSD"},
                    {"only_profitable": True, "symbol": "EURUSD"}, {"symbol": "EURUSD"}]:
        r = client.post("/api/trade/batch-close", json=payload)
        assert r.status_code == 200
    assert client.post("/api/trade/breakeven-all", json={}).status_code == 200
    assert client.post("/api/trade/panic-flatten", json={}).status_code == 200
    assert client.post("/api/trade/halt", json={"reason": "test"}).status_code == 200
    assert client.post("/api/trade/resume", json={}).json()["halted"] is False
