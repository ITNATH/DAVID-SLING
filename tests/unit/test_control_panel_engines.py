"""Round-3 audit fixes: control-panel engine enable/disable (G26-G29)."""
import asyncio
import json
from pathlib import Path

import pytest

from david_sling.core.schemas import (
    FusionSnapshot,
    ScenarioId,
    ScenarioState,
    ValidationResult,
)
from david_sling.core.utils import utc_now
from david_sling.engines.supervisor import EngineSupervisor
from david_sling.routing.router import Router
from david_sling.strategies.vault import SetupCandidate


def _candidate(engines=("C",)):
    return SetupCandidate(strategy_id="S01", family="trend", direction="long",
                          engines=tuple(engines), entry=1.10, stop_loss=1.095, take_profit=1.12,
                          risk_reward=2.0, confidence=0.8)


def _fusion():
    return FusionSnapshot(symbol="EURUSD", layers={"M1": 0.5}, convergence=0.9,
                          direction="long", conflicts=0, ts=utc_now())


def _validation():
    return ValidationResult(passed=True, pa_score=0.8, cdt_score=0.8, indicator_score=0.8,
                            weighted=0.8)


def _scenario():
    return ScenarioState(scenario=ScenarioId.S1, family="trend", confidence=0.9, ts=utc_now())


def test_disabled_engine_abstains_in_supervisor():
    sup = EngineSupervisor()
    sup.set_enabled("C", False)
    d = sup.qualify("C", _candidate(), _scenario(), _validation(), _fusion())
    assert not d.qualified and any("disabled" in r for r in d.reasons)
    assert sup.states["C"] == "DISABLED"
    sup.set_enabled("C", True)
    d2 = sup.qualify("C", _candidate(), _scenario(), _validation(), _fusion())
    assert d2.qualified


def test_router_no_route_when_only_eligible_engine_disabled():
    sup = EngineSupervisor()
    router = Router(sup, matrix={"S1": ["C"]}, min_score=0.0)
    sup.set_enabled("C", False)
    route, dec = router.route(_scenario(), _candidate(), _validation(), _fusion())
    assert route.engine == "NO_ROUTE" and dec is None
    assert any("disabled" in e for e in route.explanation)
    sup.set_enabled("C", True)
    route2, _ = router.route(_scenario(), _candidate(), _validation(), _fusion())
    assert route2.engine == "C"


def test_runtime_engine_toggle_ledgered_and_persisted(tmp_path, monkeypatch):
    from david_sling.bootstrap.runtime import Runtime

    monkeypatch.setenv("DAVID_SLING_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setattr(Runtime, "OVERRIDE_PATH", str(tmp_path / "overrides.json"))
    rt = Runtime(mode="sim")
    rec = rt.set_engine_enabled("B", False, actor="tester")
    assert rec["engine"] == "B" and rec["enabled"] is False
    assert rt.supervisor.profiles["B"].enabled is False
    assert rt.supervisor.states["B"] == "DISABLED"
    # persisted override file
    ov = json.loads(Path(rt.OVERRIDE_PATH).read_text())
    assert ov["engines.B.enabled"] is False
    # ledgered
    kinds = [e.kind for e in rt.ledger.by_kind("engine.toggled")]
    assert kinds == ["engine.toggled"]
    # config versioned
    assert rt.cfg.get("engines.B.enabled") is False
    # replay on boot applies override
    rt2 = Runtime(mode="sim")  # OVERRIDE_PATH still patched; ledger isolated via env
    rt2._apply_persisted_overrides()
    assert rt2.supervisor.profiles["B"].enabled is False
    # unknown engine rejected
    from david_sling.core.errors import ExecutionError
    with pytest.raises(ExecutionError):
        rt.set_engine_enabled("Z", True)


def test_api_engine_controls_endpoints(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from david_sling.api.app import create_app
    from david_sling.bootstrap.david_os_boot import DavidOSBoot

    monkeypatch.setenv("DAVID_SLING_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    runtime = asyncio.run(DavidOSBoot(mode="sim").run(feed=False, scan=False, loops=False))
    app = create_app(runtime)
    client = TestClient(app)
    r = client.get("/api/control/engines")
    assert r.status_code == 200
    body = r.json()
    assert set(body["engines"]) == {"A", "B", "C", "D"}
    assert all(e["enabled"] for e in body["engines"].values())
    r2 = client.post("/api/control/engines/D", json={"enabled": False, "actor": "pytest"})
    assert r2.status_code == 200 and r2.json()["enabled"] is False
    r3 = client.get("/api/control/engines")
    assert r3.json()["engines"]["D"]["enabled"] is False
    r4 = client.post("/api/control/engines/D", json={"enabled": True})
    assert r4.json()["enabled"] is True
    r5 = client.post("/api/control/engines/Z", json={"enabled": True})
    assert r5.status_code in (400, 500)
