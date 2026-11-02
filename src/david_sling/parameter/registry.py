"""L2 parameter_registry - every technical parameter must be registered here."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from david_sling.core.errors import UntrackedParameterError
from david_sling.core.schemas import ParameterRecord, ParameterStateValue
from david_sling.core.utils import canonical_json, deterministic_id, sha256_hex, utc_now


@dataclass
class ParameterDefinition:
    name: str
    domain: str
    unit: str = "unitless"
    source: str = "system"


@dataclass
class ParameterEntry:
    definition: ParameterDefinition
    record: ParameterRecord
    stages_done: set[str] = field(default_factory=set)


class ParameterRegistry:
    """Registry of all technical/intelligence parameters. The untracked
    parameter guard raises UntrackedParameterError on any bypass attempt."""

    def __init__(self) -> None:
        self._defs: dict[str, ParameterDefinition] = {}
        self._entries: dict[str, ParameterEntry] = {}

    def register(self, name: str, *, domain: str, unit: str = "unitless", source: str = "system") -> ParameterDefinition:
        definition = ParameterDefinition(name=name, domain=domain, unit=unit, source=source)
        self._defs[name] = definition
        return definition

    def is_registered(self, name: str) -> bool:
        return name in self._defs

    def define_record(self, name: str, value: object, *, state: ParameterStateValue = ParameterStateValue.VALID,
                      source: str | None = None, symbol: str | None = None, timeframe: str | None = None,
                      ts: datetime | None = None) -> ParameterRecord:
        if name not in self._defs:
            raise UntrackedParameterError(
                f"parameter '{name}' bypassed registration - zero silent drops policy", 
                context={"parameter": name},
            )
        definition = self._defs[name]
        param_hash = sha256_hex(canonical_json({"name": name, "value": value, "symbol": symbol, "tf": timeframe}))
        record = ParameterRecord(
            name=name, value=value, state=state,
            source=source or definition.source,
            symbol=symbol, timeframe=timeframe,  # type: ignore[arg-type]
            ts=ts or utc_now(), param_hash=param_hash,
        )
        self._entries[name] = ParameterEntry(definition=definition, record=record)
        return record

    def get(self, name: str) -> ParameterEntry:
        entry = self._entries.get(name)
        if entry is None:
            raise UntrackedParameterError(f"parameter '{name}' has no lifecycle record")
        return entry

    def all_records(self) -> list[ParameterRecord]:
        return [e.record for e in self._entries.values()]

    def deterministic_id(self, *parts: object) -> str:
        return deterministic_id(*parts)
