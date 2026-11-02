"""L2 parameter_lifecycle_manager - the mandatory 8-stage lifecycle.

INGEST -> VALIDATE -> DERIVE -> CONTEXTUALIZE -> FUSE -> CONTRIBUTE -> DECIDE
-> RECORD

The no-silent-drop auditor verifies every registered parameter traversed all
8 stages; any gap halts execution via UntrackedParameterError.
"""
from __future__ import annotations

from david_sling.core.contracts import ALL_STAGES, ParameterLifecycleStage
from david_sling.core.errors import UntrackedParameterError
from david_sling.core.schemas import ParameterRecord, ParameterStateValue
from david_sling.parameter.registry import ParameterRegistry


class ParameterLifecycleManager:
    def __init__(self, registry: ParameterRegistry) -> None:
        self.registry = registry
        self._stage_log: dict[str, list[ParameterLifecycleStage]] = {}

    def transition(self, name: str, stage: ParameterLifecycleStage) -> ParameterRecord:
        if stage not in ALL_STAGES:
            raise UntrackedParameterError(f"unknown lifecycle stage: {stage}")
        entry = self.registry.get(name)  # raises if untracked
        log = self._stage_log.setdefault(name, [])
        expected = ALL_STAGES[len(log)] if len(log) < len(ALL_STAGES) else None
        if expected is not None and stage != expected:
            raise UntrackedParameterError(
                f"parameter '{name}' out-of-order lifecycle: expected {expected.value}, got {stage.value}"
            )
        log.append(stage)
        entry.stages_done.add(stage.value)
        return entry.record

    def ingest(self, name: str, value: object, **kwargs: object) -> ParameterRecord:
        record = self.registry.define_record(name, value, **kwargs)  # type: ignore[arg-type]
        self._stage_log[name] = [ParameterLifecycleStage.INGEST]
        self.registry.get(name).stages_done.add(ParameterLifecycleStage.INGEST.value)
        return record

    def advance(self, name: str, stage: ParameterLifecycleStage) -> ParameterRecord:
        return self.transition(name, stage)

    def complete(self, name: str) -> ParameterRecord:
        """Drive a parameter through any remaining stages up to RECORD."""
        for stage in ALL_STAGES:
            if stage.value not in self.registry.get(name).stages_done:
                self.transition(name, stage)
        return self.registry.get(name).record

    def audit_no_silent_drops(self) -> list[str]:
        """Return names of parameters with incomplete lifecycles (empty = clean)."""
        bad: list[str] = []
        for name in self._stage_log:
            done = set(self._stage_log[name])
            if done != {s.value for s in ALL_STAGES}:
                bad.append(name)
        return bad

    def assert_no_silent_drops(self) -> None:
        bad = self.audit_no_silent_drops()
        if bad:
            raise UntrackedParameterError(
                f"silent drop detected: parameters missing lifecycle stages: {sorted(bad)}"
            )

    def mark_state(self, name: str, state: ParameterStateValue) -> ParameterRecord:
        entry = self.registry.get(name)
        entry.record = ParameterRecord(
            name=entry.record.name, value=entry.record.value, state=state,
            source=entry.record.source, symbol=entry.record.symbol,
            timeframe=entry.record.timeframe, ts=entry.record.ts, param_hash=entry.record.param_hash,
        )
        return entry.record

    def stage_log(self, name: str) -> list[str]:
        return [s.value for s in self._stage_log.get(name, [])]
