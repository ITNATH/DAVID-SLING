"""Evidence ledger hash-chain continuity & tamper detection tests."""
from __future__ import annotations

from david_sling.core.errors import EvidenceError
from david_sling.evidence_ledger.ledger import EvidenceLedger


def test_chain_continuity(ledger_path):
    led = EvidenceLedger(ledger_path)
    for i in range(10):
        led.append("test.event", {"i": i})
    assert led.verify_chain()
    led.assert_continuity()
    assert len(led) == 10
    assert led.merkle_root()


def test_tamper_detection(ledger_path):
    led = EvidenceLedger(ledger_path)
    led.append("a", {"x": 1})
    led.append("b", {"x": 2})
    assert led.verify_chain()
    led._records[0] = led._records[0].model_copy(update={"payload": {"x": 999}})
    assert not led.verify_chain()
    with __import__("pytest").raises(EvidenceError):
        led.assert_continuity()


def test_persistence_across_reopen(ledger_path):
    led = EvidenceLedger(ledger_path)
    led.append("persist", {"v": 1})
    head = led.head.hash
    led2 = EvidenceLedger(ledger_path)
    assert len(led2) == 1
    assert led2.head.hash == head
    assert led2.verify_chain()
