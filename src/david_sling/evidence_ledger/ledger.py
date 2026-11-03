"""L2 evidence_ledger/ledger - append-only, hash-chained evidence ledger.

Chain rule: record.hash = SHA3-256(prev_hash || canonical(payload)).
Persisted as JSONL under storage/audit so continuity is verifiable across
restarts. The ledger validator re-computes the chain and detects tampering.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from david_sling.core.errors import EvidenceError
from david_sling.core.schemas import EvidenceRecord
from david_sling.core.utils import (
    canonical_json,
    hash_record,
    new_id,
    sha256_hex,
    utc_now,
)

GENESIS_HASH = "0" * 64


class EvidenceLedger:
    def __init__(self, persist_path: str | Path | None = None, *, fsync: bool | None = None) -> None:
        self._records: list[EvidenceRecord] = []
        # G44: durability switch - default ON (tamper-evidence); DAVID_SLING_LEDGER_FSYNC=0
        # disables per-append fsync for high-rate sim/backtest runs
        self._fsync = fsync if fsync is not None else os.environ.get("DAVID_SLING_LEDGER_FSYNC", "1") == "1"
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            self._load()

    # ------------------------------------------------------------- append
    def append(self, kind: str, payload: dict[str, Any], parent_ids: list[str] | None = None) -> EvidenceRecord:
        prev_hash = self._records[-1].hash if self._records else GENESIS_HASH
        ts = utc_now()
        evidence_id = new_id("ev")
        body = {
            "evidence_id": evidence_id, "kind": kind, "payload": payload,
            "parent_ids": parent_ids or [], "prev_hash": prev_hash,
            "ts": ts.isoformat(),
        }
        digest = hash_record(body, prev_hash)
        record = EvidenceRecord(
            evidence_id=evidence_id, kind=kind, payload=payload,
            parent_ids=parent_ids or [], prev_hash=prev_hash, hash=digest,
            ts=ts,
        )
        self._records.append(record)
        self._persist(record)
        return record

    def _persist(self, record: EvidenceRecord) -> None:
        if not self._persist_path:
            return
        line = json.dumps(record.model_dump(mode="json"), separators=(",", ":"))
        with self._persist_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            if self._fsync:
                os.fsync(fh.fileno())

    def _load(self) -> None:
        assert self._persist_path is not None
        if not self._persist_path.exists():
            return
        with self._persist_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                self._records.append(EvidenceRecord.model_validate(json.loads(line)))

    # ------------------------------------------------------------- queries
    @property
    def head(self) -> EvidenceRecord | None:
        return self._records[-1] if self._records else None

    @property
    def genesis(self) -> str:
        return GENESIS_HASH

    def __len__(self) -> int:
        return len(self._records)

    def all(self) -> list[EvidenceRecord]:
        return list(self._records)

    def by_kind(self, kind: str) -> list[EvidenceRecord]:
        return [r for r in self._records if r.kind == kind]

    def merkle_root(self) -> str:
        """SHA-256 Merkle root over all record hashes (evidence identity)."""
        hashes = [r.hash for r in self._records] or [GENESIS_HASH]
        while len(hashes) > 1:
            nxt = []
            for i in range(0, len(hashes), 2):
                pair = hashes[i] + (hashes[i + 1] if i + 1 < len(hashes) else hashes[i])
                nxt.append(sha256_hex(pair))
            hashes = nxt
        return hashes[0]

    # ----------------------------------------------------------- integrity
    def verify_chain(self) -> bool:
        prev = GENESIS_HASH
        for record in self._records:
            if record.prev_hash != prev:
                return False
            body = {
                "evidence_id": record.evidence_id, "kind": record.kind,
                "payload": record.payload, "parent_ids": record.parent_ids,
                "prev_hash": record.prev_hash, "ts": record.ts.isoformat(),
            }
            if hash_record(body, prev) != record.hash:
                return False
            prev = record.hash
        return True

    def assert_continuity(self) -> None:
        if not self.verify_chain():
            raise EvidenceError("evidence hash chain broken - tampering detected")

    def export_jsonl(self) -> str:
        return "\n".join(canonical_json(r.model_dump(mode="json")) for r in self._records)
