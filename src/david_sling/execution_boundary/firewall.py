"""L10 execution_firewall - converts TechnicalSignalTicket -> OrderIntent.

Structural law: technical layers (L0-L9) may call this boundary only. The
boundary is the sole importer of L11/L12 domains from the technical side.
`assert_caller` enforces the caller domain against the architecture manifest.
"""
from __future__ import annotations

from datetime import datetime

from david_sling.core.errors import BoundaryViolation
from david_sling.core.laws import layer_of
from david_sling.core.schemas import OrderIntent, OrderSide, OrderType, SignalTicket
from david_sling.core.utils import new_id, utc_now

ALLOWED_CALLERS = {"signal", "rescan", "execution_boundary", "mission_control", "application", "api", "control_panel"}


class ExecutionBoundary:
    def __init__(self) -> None:
        self.handed_off: int = 0

    @staticmethod
    def assert_caller(caller_domain: str) -> None:
        if caller_domain in ALLOWED_CALLERS:
            return
        li = layer_of(caller_domain)
        if li <= 9:
            raise BoundaryViolation(
                f"technical domain '{caller_domain}' (L{li}) must hand off via L10 execution_boundary"
            )

    def to_order_intent(self, ticket: SignalTicket, *, volume: float, caller: str = "signal",
                        ts: datetime | None = None) -> OrderIntent:
        self.assert_caller(caller)
        self.handed_off += 1
        side = OrderSide.BUY if ticket.direction == "long" else OrderSide.SELL
        return OrderIntent(
            intent_id=new_id("ord"), symbol=ticket.symbol, side=side,
            order_type=OrderType.MARKET, volume=volume,
            stop_loss=ticket.stop_loss, take_profit=ticket.take_profit,
            signal_id=ticket.signal_id, idempotency_key=f"{ticket.signal_id}:{ticket.symbol}",
            ts=ts or utc_now(),
        )

    def manual_intent(self, symbol: str, side: OrderSide, volume: float, *,
                      order_type: OrderType = OrderType.MARKET, price: float | None = None,
                      sl: float | None = None, tp: float | None = None,
                      caller: str = "api") -> OrderIntent:
        self.assert_caller(caller)
        self.handed_off += 1
        return OrderIntent(
            intent_id=new_id("ord"), symbol=symbol, side=side, order_type=order_type,
            volume=volume, price=price, stop_loss=sl, take_profit=tp,
            signal_id=None, idempotency_key=new_id("idem"), ts=utc_now(),
        )
