"""mission_control/cross_pair_pnl_calculator - sub-millisecond real-time
cross-pair PnL, swap, spread and margin aggregation."""
from __future__ import annotations

import time

from david_sling.broker.simulated import SimulatedBrokerAdapter
from david_sling.core.schemas import CrossPairPnL, PositionState


class CrossPairPnLCalculator:
    def __init__(self, broker: SimulatedBrokerAdapter) -> None:
        self.broker = broker

    def compute(self, positions: dict[str, PositionState]) -> list[CrossPairPnL]:
        start = time.perf_counter()
        by_symbol: dict[str, CrossPairPnL] = {}
        for pos in positions.values():
            mid = self.broker.price(pos.symbol)
            pnl = self.broker._pnl(pos.symbol, pos.side.value, pos.entry_price, mid, pos.volume)
            entry = by_symbol.setdefault(pos.symbol, CrossPairPnL(symbol=pos.symbol))
            if pnl >= 0:
                entry.gross_profit += pnl
            else:
                entry.gross_loss += pnl
            entry.net += pnl
            entry.swap += pos.swap
            entry.open_positions += 1
        for symbol, entry in by_symbol.items():
            spec = self.broker.specs[symbol]
            notional = sum(p.volume * spec.contract_size * self.broker.price(symbol)
                           for p in positions.values() if p.symbol == symbol)
            entry.margin = round(notional * spec.margin_rate, 2)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 1.0, f"cross-pair PnL budget exceeded: {elapsed_ms:.3f}ms"
        return sorted(by_symbol.values(), key=lambda e: e.symbol)

    def total_net(self, rows: list[CrossPairPnL]) -> float:
        return round(sum(r.net for r in rows), 2)
