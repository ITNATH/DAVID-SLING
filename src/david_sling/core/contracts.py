"""L0 core/contracts - master system contract protocols (blueprint: contracts/*,
28 contract modules consolidated into typed Protocols + dataclasses).

A contract is the typed boundary between two layers. The runtime enforces the
most load-bearing ones:
  - ParameterContract   : 8-stage lifecycle, zero silent drops
  - EvidenceContract    : append-only hash chain
  - ExecutionBoundaryContract : the ONLY technical->downstream handoff
  - RiskContract        : hard veto, never mutates technical evidence
  - SizingContract      : broker minimum lot is the authority
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol

from .schemas import (
    AlertEvent,
    EvidenceRecord,
    MultiTradeIntent,
    OrderIntent,
    ParameterRecord,
    PrecisionGrade,
    RouteDecision,
    SignalTicket,
)


class ParameterLifecycleStage(StrEnum):
    INGEST = "INGEST"
    VALIDATE = "VALIDATE"
    DERIVE = "DERIVE"
    CONTEXTUALIZE = "CONTEXTUALIZE"
    FUSE = "FUSE"
    CONTRIBUTE = "CONTRIBUTE"
    DECIDE = "DECIDE"
    RECORD = "RECORD"


ALL_STAGES: tuple[ParameterLifecycleStage, ...] = tuple(ParameterLifecycleStage)


class ParameterContract(Protocol):
    def register(self, name: str, *, source: str) -> ParameterRecord: ...
    def transition(self, name: str, stage: ParameterLifecycleStage) -> ParameterRecord: ...


class EvidenceContract(Protocol):
    def append(self, kind: str, payload: dict[str, Any], parent_ids: list[str] | None = None) -> EvidenceRecord: ...
    def verify_chain(self) -> bool: ...


class ExecutionBoundaryContract(Protocol):
    """L10: converts a TechnicalSignalTicket into a downstream OrderIntent.

    Technical layers must never call this with broker/risk objects; the
    firewall checks the caller domain against the architecture manifest."""

    def to_order_intent(self, ticket: SignalTicket, *, idempotency_key: str) -> OrderIntent: ...


class RiskContract(Protocol):
    """L11: pre-trade hard veto. May approve/reject and resize, but must never
    rewrite the technical evidence attached to the signal."""

    def evaluate(self, intent: OrderIntent, context: dict[str, Any]) -> dict[str, Any]: ...


class SizingContract(Protocol):
    """L11: resolves effective lot. Broker minimum lot is the authority."""

    def effective_lot(self, symbol: str, requested_lot: float, risk_based_lot: float) -> float: ...


class MultiTradeContract(Protocol):
    def execute_basket(self, intent: MultiTradeIntent) -> list[dict[str, Any]]: ...


class AlertContract(Protocol):
    def emit(self, event: AlertEvent) -> None: ...


# Type aliases used across layers
RouteDecisionT = RouteDecision
PrecisionGradeT = PrecisionGrade
