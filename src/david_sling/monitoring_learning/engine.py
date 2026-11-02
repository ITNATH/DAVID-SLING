"""L13 monitoring_engine - performance & edge-decay monitoring.

STRICTLY non-mutating: learning may propose drift changes, never apply them to
the live configuration (immutable learning boundary). Proposals require the
control-panel authorization path.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from david_sling.position_management.tms import ClosedTrade


@dataclass
class StrategyStats:
    trades: int = 0
    wins: int = 0
    pnl: float = 0.0
    edge: float = 0.0          # mean pnl per trade - edge decay when <= 0


@dataclass
class MonitoringEngine:
    """Tracks per-strategy outcomes; emits drift *proposals* only."""

    stats: dict[str, StrategyStats] = field(default_factory=dict)
    proposals: list[dict] = field(default_factory=list)

    def record_outcome(self, strategy_id: str | None, trade: ClosedTrade) -> None:
        sid = strategy_id or "manual"
        s = self.stats.setdefault(sid, StrategyStats())
        s.trades += 1
        s.pnl += trade.pnl
        if trade.pnl > 0:
            s.wins += 1
        s.edge = s.pnl / s.trades
        if s.trades >= 10 and s.edge <= 0:
            self.proposals.append({
                "type": "edge_decay", "strategy": sid, "trades": s.trades,
                "edge": round(s.edge, 4), "action": "propose_disable_pending_review",
                "note": "non-mutating: requires control-panel authorization to apply",
            })

    def summary(self) -> dict:
        return {sid: {"trades": s.trades, "win_rate": round(s.wins / s.trades, 3) if s.trades else 0.0,
                      "pnl": round(s.pnl, 2), "edge": round(s.edge, 4)}
                for sid, s in self.stats.items()}
