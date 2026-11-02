"""L1 control panel - the operator change console.

All runtime configuration mutations flow through here: versioned via the
ConfigurationEngine, recorded in the evidence ledger, telemetry-emitted,
and rollback-able. Nothing else in the stack mutates configuration directly.
"""
from __future__ import annotations

from typing import Any

from david_sling.configuration.configuration_engine import ConfigurationEngine
from david_sling.core.utils import utc_now
from david_sling.evidence_ledger.ledger import EvidenceLedger


class ControlPanel:
    def __init__(self, config_engine: ConfigurationEngine, ledger: EvidenceLedger,
                 telemetry: Any = None) -> None:
        self.config_engine = config_engine
        self.ledger = ledger
        self.telemetry = telemetry

    def change(self, key: str, value: Any, *, actor: str = "operator") -> dict:
        cfg = self.config_engine.apply_change(key, value, actor=actor)
        record = {"key": key, "value": value, "actor": actor, "version": cfg.version, "ts": utc_now().isoformat()}
        self.ledger.append("config.change", record)
        if self.telemetry is not None:
            import asyncio

            coro = self.telemetry.emit("config.changed", record)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(coro)
            except RuntimeError:
                asyncio.run(coro)
        return {"version": cfg.version, "key": key, "value": value, "actor": actor}

    def rollback(self, *, actor: str = "operator") -> dict:
        cfg = self.config_engine.rollback()
        record = {"action": "rollback", "actor": actor, "version": cfg.version, "ts": utc_now().isoformat()}
        self.ledger.append("config.rollback", record)
        return {"version": cfg.version, "action": "rollback"}

    def history(self) -> list[dict]:
        return [{"version": c.version, "ts": getattr(c, "ts", None)} for c in self.config_engine.history()]

    def status(self) -> dict:
        eff = self.config_engine.effective
        return {
            "version": eff.version,
            "source_files": list(eff.source_files),
            "versions": len(self.config_engine.history()),
        }
