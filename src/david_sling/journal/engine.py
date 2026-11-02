"""L13 journal_engine - immutable journal with outcome attribution.

Every signal / execution / exit / rescan is journaled into the evidence ledger
(kind journal.*) with parent links back to the originating evidence records.
"""
from __future__ import annotations

from typing import Any

from david_sling.evidence_ledger.ledger import EvidenceLedger


class JournalEngine:
    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger

    def log(self, kind: str, payload: dict[str, Any], parent_ids: list[str] | None = None) -> str:
        rec = self.ledger.append(f"journal.{kind}", payload, parent_ids)
        return rec.evidence_id

    def signal(self, ticket: dict) -> str:
        return self.log("signal", {"ticket": ticket})

    def execution(self, intent: dict, report: dict | None, risk: dict) -> str:
        return self.log("execution", {"intent": intent, "report": report, "risk": risk})

    def exit(self, trade: dict) -> str:
        return self.log("exit", {"trade": trade})

    def rescan(self, event: dict) -> str:
        return self.log("rescan", {"event": event})
