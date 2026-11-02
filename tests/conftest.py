from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("DAVID_SLING_LEDGER_PATH", "storage/test/evidence_ledger.jsonl")

import pytest


@pytest.fixture()
def ledger_path(tmp_path):
    return tmp_path / "ledger.jsonl"
