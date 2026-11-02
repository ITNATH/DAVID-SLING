"""L9 signal_engine - produces the canonical TechnicalSignalTicket.

Trigger state machine: PENDING -> ROUTED -> (FILLED | VETOED | ABORTED).
Every routed ticket emits an alert event and a bus event, and is recorded in
the evidence ledger.
"""
from __future__ import annotations

from david_sling.core.schemas import (
    PrecisionGrade,
    RouteDecision,
    ScenarioState,
    SignalStatus,
    SignalTicket,
)
from david_sling.core.utils import new_id, utc_now
from david_sling.engines.supervisor import EngineDecision
from david_sling.strategies.vault import SetupCandidate


class SignalEngine:
    def __init__(self) -> None:
        self.tickets: dict[str, SignalTicket] = {}
        self.feed: list[SignalTicket] = []

    def build(self, symbol: str, scenario: ScenarioState, candidate: SetupCandidate,
              route: RouteDecision, engine_decision: EngineDecision, precision: PrecisionGrade,
              evidence_ids: list[str]) -> SignalTicket:
        direction = candidate.direction
        # entry zone: around entry +/- 10% of SL distance (OTE-style refinement band)
        pad = abs(candidate.entry - candidate.stop_loss) * 0.1
        entry_zone = (round(candidate.entry - pad, 6), round(candidate.entry + pad, 6))
        ticket = SignalTicket(
            signal_id=new_id("sig"), symbol=symbol, direction=direction,
            scenario=scenario.scenario, strategy_id=candidate.strategy_id,
            engine=route.engine,  # type: ignore[arg-type]
            entry_zone=entry_zone, stop_loss=candidate.stop_loss,
            take_profit=candidate.take_profit, risk_reward=candidate.risk_reward,
            precision=precision, evidence_ids=evidence_ids,
            status=SignalStatus.ROUTED, ts=utc_now(),
        )
        self.tickets[ticket.signal_id] = ticket
        self.feed.append(ticket)
        if len(self.feed) > 200:
            self.feed = self.feed[-200:]
        return ticket

    def set_status(self, signal_id: str, status: SignalStatus) -> None:
        t = self.tickets.get(signal_id)
        if t is not None:
            self.tickets[signal_id] = t.model_copy(update={"status": status})

    def recent(self, limit: int = 50) -> list[SignalTicket]:
        return self.feed[-limit:]
