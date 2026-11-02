"""L2 data/replay - deterministic replay engine for backtesting.

Replays a generated historical tape through the decision pipeline
synchronously and reports signal/execution statistics. Determinism is
guaranteed by the seeded synthetic feed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ReplayEngine:
    def __init__(self, days: int = 30, symbols: tuple[str, ...] = ("EURUSD", "GBPUSD")) -> None:
        self.days = days
        self.symbols = symbols

    async def run(self, runtime_factory: Any = None) -> ReplayResult:
        # injected by the launcher (composition root) to avoid L2 -> L1 import
        if runtime_factory is None:
            raise RuntimeError("ReplayEngine.run requires a runtime_factory (composition root)")
        runtime = await runtime_factory(mode="backtest")
        sim = runtime.sim
        assert sim is not None
        ticks_processed = 0
        candles_closed = 0
        for symbol in self.symbols:
            tape = sim.generate_history(symbol, self.days)
            for tick in tape:
                ticks_processed += 1
                closed = sim.builder.add_tick(tick)
                candles_closed += len(closed)
                if closed:
                    await runtime.pipeline.run_symbol(symbol)
        result = ReplayResult(
            days=self.days, symbols=list(self.symbols), ticks=ticks_processed,
            candles=candles_closed, signals=len(runtime.signal_engine.tickets),
            orders=len(runtime.order_manager.orders),
            positions_closed=len(runtime.tms.closed_history),
            ledger_entries=len(runtime.ledger),
            chain_ok=runtime.ledger.verify_chain(),
        )
        return result


@dataclass
class ReplayResult:
    days: int
    symbols: list[str]
    ticks: int
    candles: int
    signals: int
    orders: int
    positions_closed: int
    ledger_entries: int
    chain_ok: bool
    extra: dict = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"DAVID SLING backtest: {self.days}d over {self.symbols} | "
            f"ticks={self.ticks} candles={self.candles} signals={self.signals} "
            f"orders={self.orders} closed_positions={self.positions_closed} "
            f"ledger_entries={self.ledger_entries} hash_chain_ok={self.chain_ok}"
        )
