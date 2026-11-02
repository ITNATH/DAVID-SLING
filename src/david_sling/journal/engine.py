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
        self.index: list[dict] = []  # queryable journal index (ledger chain itself is immutable)

    def log(self, kind: str, payload: dict[str, Any], parent_ids: list[str] | None = None) -> str:
        rec = self.ledger.append(f"journal.{kind}", payload, parent_ids)
        self.index.append({"ts": rec.ts, "kind": kind, "evidence_id": rec.evidence_id})
        return rec.evidence_id

    def prune(self, retention_days: int = 90) -> int:
        """Retention policy: drop journal index entries older than retention_days.
        The evidence hash chain is append-only and never pruned (tamper-evident)."""
        from datetime import timedelta

        from david_sling.core.utils import utc_now

        cutoff = utc_now() - timedelta(days=retention_days)
        before = len(self.index)
        self.index = [e for e in self.index if e["ts"] >= cutoff]
        return before - len(self.index)

    def signal(self, ticket: dict) -> str:
        return self.log("signal", {"ticket": ticket})

    def execution(self, intent: dict, report: dict | None, risk: dict) -> str:
        return self.log("execution", {"intent": intent, "report": report, "risk": risk})

    def exit(self, trade: dict) -> str:
        return self.log("exit", {"trade": trade})

    def rescan(self, event: dict) -> str:
        return self.log("rescan", {"event": event})
