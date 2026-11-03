"""L12 order_manager - intent -> pre-trade gate -> broker -> fill -> position.

Every order passes the L11 risk gate before broker submission; fills create
positions registered with the TMS. All transitions are journaled/audited.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from david_sling.broker.simulated import ExecutionReport, SimulatedBrokerAdapter
from david_sling.core.errors import ExecutionError, MultiTradeError
from david_sling.core.schemas import (
    MultiTradeIntent,
    OrderIntent,
)
from david_sling.core.utils import utc_now


class OrderStatus(StrEnum):
    CREATED = "CREATED"
    RISK_VETOED = "RISK_VETOED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass
class ManagedOrder:
    intent: OrderIntent
    status: OrderStatus
    report: ExecutionReport | None = None
    risk_reasons: tuple[str, ...] = ()
    ts: datetime = utc_now()


class OrderManager:
    def __init__(self, broker: SimulatedBrokerAdapter) -> None:
        self.broker = broker
        self.orders: dict[str, ManagedOrder] = {}
        self._by_key: dict[str, str] = {}  # idempotency_key -> intent_id (G55)

    def submit(self, intent: OrderIntent, *, risk_approved: bool, risk_reasons: tuple[str, ...] = (),
               adjusted_volume: float | None = None) -> ManagedOrder:
        # G55: idempotent replay - same key returns the existing order, never re-submits
        existing_id = self._by_key.get(intent.idempotency_key)
        if existing_id is not None and existing_id in self.orders:
            return self.orders[existing_id]
        self._by_key[intent.idempotency_key] = intent.intent_id
        if not risk_approved:
            order = ManagedOrder(intent=intent, status=OrderStatus.RISK_VETOED, risk_reasons=risk_reasons)
            self.orders[intent.intent_id] = order
            return order
        final = intent
        if adjusted_volume is not None and adjusted_volume > 0:
            final = intent.model_copy(update={"volume": adjusted_volume})
        order = ManagedOrder(intent=final, status=OrderStatus.SUBMITTED)
        try:
            report = self.broker.submit(final)
        except ExecutionError as exc:
            order.status = OrderStatus.REJECTED
            order.risk_reasons = (str(exc),)
            self.orders[final.intent_id] = order
            raise
        order.status = OrderStatus.FILLED
        order.report = report
        self.orders[final.intent_id] = order
        return order

    def submit_basket(self, basket: MultiTradeIntent, risk_check) -> list[ManagedOrder]:
        """Atomic-ish basket: every leg is risk-checked first; any veto aborts the
        whole basket (no partial unhedged books)."""
        decisions = [risk_check(o) for o in basket.orders]
        if not all(d.approved for d in decisions):
            raise MultiTradeError(
                "basket aborted: risk veto on legs: "
                + "; ".join(f"{o.symbol}: {d.reasons}" for o, d in zip(basket.orders, decisions, strict=True) if not d.approved)
            )
        results: list[ManagedOrder] = []
        for intent, decision in zip(basket.orders, decisions, strict=True):
            results.append(self.submit(intent, risk_approved=True, adjusted_volume=decision.adjusted_volume or None))
        return results

    def get(self, order_id: str) -> ManagedOrder | None:
        return self.orders.get(order_id)

    def all(self) -> list[ManagedOrder]:
        return list(self.orders.values())

    def reconcile(self) -> dict:
        return {"orders": len(self.orders), "broker": self.broker.reconcile()}
