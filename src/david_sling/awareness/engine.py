"""L3 awareness_engine - continuous awareness supervisor.

Produces an immutable awareness snapshot: price, volatility, session epoch,
regime, liquidity state, spread.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

from david_sling.core.schemas import RegimeState
from david_sling.core.session_epoch_manager import epoch_at, primary_phase
from david_sling.intelligence.features import FeatureSet


@dataclass(frozen=True)
class AwarenessSnapshot:
    symbol: str
    price: float
    atr_m1: float
    atr_pct_h1: float
    spread_points: float
    session_epoch: str
    session_phase: str
    regime: str
    regime_confidence: float
    ts: datetime

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ts"] = self.ts.isoformat()
        return d


class AwarenessEngine:
    def __init__(self) -> None:
        self._snapshots: dict[str, AwarenessSnapshot] = {}

    def update(self, fs: FeatureSet, regime: RegimeState, spread_points: float) -> AwarenessSnapshot:
        snap = AwarenessSnapshot(
            symbol=fs.symbol, price=fs.price, atr_m1=fs.atr_m1, atr_pct_h1=fs.atr_pct_h1,
            spread_points=spread_points, session_epoch=epoch_at(fs.ts).value,
            session_phase=primary_phase(fs.ts), regime=regime.regime,
            regime_confidence=regime.confidence, ts=fs.ts,
        )
        self._snapshots[fs.symbol] = snap
        return snap

    def snapshot(self, symbol: str) -> AwarenessSnapshot | None:
        return self._snapshots.get(symbol)

    def all(self) -> dict[str, AwarenessSnapshot]:
        return dict(self._snapshots)
