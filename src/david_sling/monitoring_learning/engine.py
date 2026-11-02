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
    recent: list = field(default_factory=list)  # rolling pnl window for drift detection


@dataclass
class MonitoringEngine:
    """Tracks per-strategy outcomes; emits drift *proposals* only."""

    stats: dict[str, StrategyStats] = field(default_factory=dict)
    proposals: list[dict] = field(default_factory=list)
    dispatch_count: int = 0
    dispatch_ms_total: float = 0.0
    dispatch_over_budget: int = 0

    def record_outcome(self, strategy_id: str | None, trade: ClosedTrade) -> None:
        sid = strategy_id or "manual"
        s = self.stats.setdefault(sid, StrategyStats())
        s.trades += 1
        s.pnl += trade.pnl
        if trade.pnl > 0:
            s.wins += 1
        s.edge = s.pnl / s.trades
        s.recent.append(trade.pnl)
        if len(s.recent) > 40:
            s.recent.pop(0)
        if s.trades >= 10 and s.edge <= 0:
            self.proposals.append({
                "type": "edge_decay", "strategy": sid, "trades": s.trades,
                "edge": round(s.edge, 4), "action": "propose_disable_pending_review",
                "note": "non-mutating: requires control-panel authorization to apply",
            })
        # concept drift: recent-window mean pnl regime shift vs prior window
        if len(s.recent) >= 40:
            first = s.recent[:20]
            last = s.recent[20:]
            m1 = sum(first) / 20.0
            m2 = sum(last) / 20.0
            if (m1 > 0) != (m2 > 0) or (m1 != 0 and abs(m2) < 0.5 * abs(m1)):
                self.proposals.append({
                    "type": "concept_drift", "strategy": sid, "window": 40,
                    "prior_mean": round(m1, 4), "recent_mean": round(m2, 4),
                    "action": "propose_review_pending_review",
                    "note": "non-mutating: requires control-panel authorization to apply",
                })
                s.recent.clear()
        if len(self.proposals) > 100:
            self.proposals = self.proposals[-100:]

    def record_dispatch(self, ms: float) -> None:
        """GUI/API dispatch latency budget (<1ms) tracking."""
        self.dispatch_count += 1
        self.dispatch_ms_total += ms
        if ms > 1.0:
            self.dispatch_over_budget += 1

    def summary(self) -> dict:
        return {
            "strategies": {sid: {"trades": s.trades, "win_rate": round(s.wins / s.trades, 3) if s.trades else 0.0,
                                 "pnl": round(s.pnl, 2), "edge": round(s.edge, 4)}
                           for sid, s in self.stats.items()},
            "proposals": list(self.proposals[-20:]),
            "dispatch": {"count": self.dispatch_count,
                         "avg_ms": round(self.dispatch_ms_total / self.dispatch_count, 4) if self.dispatch_count else 0.0,
                         "over_1ms": self.dispatch_over_budget},
        }
