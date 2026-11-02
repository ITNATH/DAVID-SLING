"""L3 intelligence/intelligence_engine - executes the technical-intelligence
graph and builds the evidence packet consumed by fusion/validation."""
from __future__ import annotations

from datetime import datetime

from david_sling.core.schemas import Candle, Timeframe
from david_sling.intelligence.features import FeatureSet, compute_features


class IntelligenceEngine:
    """Executes the complete technical-intelligence graph for one symbol."""

    FAMILIES = (
        "price_action", "candles", "structure", "liquidity", "orderflow",
        "volume", "volatility", "momentum", "indicators", "geometry",
        "levels", "zones", "fibonacci", "harmonics", "patterns", "sentiment",
    )

    def __init__(self) -> None:
        self.last_features: dict[str, FeatureSet] = {}

    def analyze(self, symbol: str, ts: datetime, price: float, spread_points: float, session: str,
                candles_by_tf: dict[Timeframe, list[Candle]],
                deltas: list[float] | None = None, news_repricing: bool = False) -> FeatureSet:
        fs = compute_features(symbol, ts, price, spread_points, session, candles_by_tf, deltas, news_repricing)
        # evidence packet: one observation per contributing family
        fs.observations = self._evidence_packet(fs)
        self.last_features[symbol] = fs
        return fs

    def _evidence_packet(self, fs: FeatureSet) -> list[dict]:
        obs: list[dict] = []
        def add(family: str, name: str, value: float, note: str = "") -> None:
            obs.append({"family": family, "name": name, "value": round(float(value), 6), "note": note})
        add("indicators", "rsi_m1", fs.rsi_m1)
        add("indicators", "macd_hist_m1", fs.macd_hist_m1)
        add("indicators", "bb_pos_m1", fs.bb_pos_m1)
        add("indicators", "ema_cross_m1", 1 if fs.ema20_m1 > fs.ema50_m1 else -1)
        add("structure", "trend_h1", fs.trend_h1)
        add("structure", "trend_h4", fs.trend_h4)
        add("structure", "bos_up_h1", float(fs.bos_up_h1))
        add("structure", "bos_dn_h1", float(fs.bos_dn_h1))
        add("structure", "choch_up_h1", float(fs.choch_up_h1))
        add("structure", "choch_dn_h1", float(fs.choch_dn_h1))
        add("liquidity", "sweep_up_m5", float(fs.sweep_up_m5))
        add("liquidity", "sweep_dn_m5", float(fs.sweep_dn_m5))
        add("liquidity", "eqh", float(fs.eqh))
        add("liquidity", "eql", float(fs.eql))
        add("zones", "fvg_up_m5", float(fs.fvg_up_m5))
        add("zones", "fvg_dn_m5", float(fs.fvg_dn_m5))
        add("price_action", "displacement_up", float(fs.displacement_up))
        add("price_action", "displacement_dn", float(fs.displacement_dn))
        add("price_action", "rejection_up", float(fs.rejection_up))
        add("price_action", "rejection_dn", float(fs.rejection_dn))
        add("volatility", "atr_m1", fs.atr_m1)
        add("volatility", "atr_pct_h1", fs.atr_pct_h1)
        add("momentum", "roc_m1", fs.roc_m1)
        add("momentum", "macd_hist_m1", fs.macd_hist_m1)
        add("volume", "volume_z_m1", fs.volume_z_m1)
        add("orderflow", "delta_m1", fs.delta_m1)
        return obs
