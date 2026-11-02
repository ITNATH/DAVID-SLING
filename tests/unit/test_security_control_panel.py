"""L1 security (license engine + operator session) and control panel tests."""
import pytest

from david_sling.configuration.configuration_engine import ConfigurationEngine
from david_sling.control_panel.panel import ControlPanel
from david_sling.core.errors import SecurityError
from david_sling.evidence_ledger.ledger import EvidenceLedger
from david_sling.security.license_engine import ENTITLEMENTS, LicenseEngine
from david_sling.security.session import OperatorSession


def test_sim_license_active_with_entitlements():
    lic = LicenseEngine(mode="sim")
    assert lic.license.status == "ACTIVE"
    assert lic.license.type == "simulated-institutional"
    assert lic.license.entitlements == ENTITLEMENTS
    assert lic.permits("strategy_vault_52")
    assert lic.status()["status"] == "ACTIVE"


def test_live_license_requires_credentials(monkeypatch):
    monkeypatch.delenv("DAVID_SLING_LICENSE_TOKEN", raising=False)
    monkeypatch.delenv("DAVID_SLING_LICENSE_KEY", raising=False)
    with pytest.raises(SecurityError):
        LicenseEngine(mode="live")


def test_live_license_verifies_hmac_signature(monkeypatch):
    import base64
    import hashlib
    import hmac
    import json

    key = "test-key"
    payload = base64.urlsafe_b64encode(json.dumps({"product": "DAVID-SLING"}).encode()).decode().rstrip("=")
    sig = hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    monkeypatch.setenv("DAVID_SLING_LICENSE_KEY", key)
    monkeypatch.setenv("DAVID_SLING_LICENSE_TOKEN", f"{payload}.{sig}")
    lic = LicenseEngine(mode="live")
    assert lic.license.status == "ACTIVE" and lic.license.type == "institutional"
    monkeypatch.setenv("DAVID_SLING_LICENSE_TOKEN", f"{payload}.deadbeef")
    with pytest.raises(SecurityError):
        LicenseEngine(mode="live")


def test_operator_session_token_gate(monkeypatch):
    monkeypatch.delenv("DAVID_SLING_API_TOKEN", raising=False)
    sess = OperatorSession()
    assert sess.status() == {"authenticated": True, "role": "master_admin", "token_required": False}
    sess.verify(None)  # dev-open
    monkeypatch.setenv("DAVID_SLING_API_TOKEN", "s3cret")
    assert OperatorSession().token_required() is True
    assert OperatorSession().check("Bearer s3cret") is True
    assert OperatorSession().check("Bearer wrong") is False
    with pytest.raises(SecurityError):
        OperatorSession().verify("Bearer wrong")


def test_control_panel_change_versions_and_rolls_back(ledger_path, monkeypatch):
    monkeypatch.setenv("DAVID_SLING_LEDGER_PATH", str(ledger_path))
    cfg = ConfigurationEngine()
    cfg.load()
    ledger = EvidenceLedger(str(ledger_path))
    panel = ControlPanel(cfg, ledger)
    v0 = cfg.effective.version
    res = panel.change("risk.session_risk_cap_pct", 1.25, actor="tester")
    assert res["version"] == v0 + 1 and res["value"] == 1.25
    assert cfg.effective.get("risk.session_risk_cap_pct") == 1.25
    assert any(e.kind == "config.change" for e in ledger.all())
    rb = panel.rollback(actor="tester")
    assert rb["version"] == v0
    assert cfg.effective.get("risk.session_risk_cap_pct") != 1.25
    assert panel.status()["source_files"]
