"""Zero-silent-drop parameter lifecycle tests."""
from __future__ import annotations

import pytest

from david_sling.core.contracts import ALL_STAGES, ParameterLifecycleStage
from david_sling.core.errors import UntrackedParameterError
from david_sling.parameter.lifecycle import ParameterLifecycleManager
from david_sling.parameter.registry import ParameterRegistry


def make():
    reg = ParameterRegistry()
    reg.register("atr.m1", domain="intelligence")
    return reg, ParameterLifecycleManager(reg)


def test_full_lifecycle_passes_all_eight_stages():
    reg, mgr = make()
    mgr.ingest("atr.m1", 0.0012, symbol="EURUSD")
    for stage in ALL_STAGES[1:]:
        mgr.advance("atr.m1", stage)
    assert mgr.stage_log("atr.m1") == [s.value for s in ALL_STAGES]
    mgr.assert_no_silent_drops()  # must not raise


def test_untracked_parameter_raises():
    reg, mgr = make()
    with pytest.raises(UntrackedParameterError):
        reg.define_record("rogue.param", 1.0)


def test_out_of_order_stage_raises():
    reg, mgr = make()
    mgr.ingest("atr.m1", 0.001)
    with pytest.raises(UntrackedParameterError):
        mgr.advance("atr.m1", ParameterLifecycleStage.RECORD)


def test_silent_drop_detected_by_auditor():
    reg, mgr = make()
    mgr.ingest("atr.m1", 0.001)  # stuck at INGEST
    assert mgr.audit_no_silent_drops() == ["atr.m1"]
    with pytest.raises(UntrackedParameterError):
        mgr.assert_no_silent_drops()
