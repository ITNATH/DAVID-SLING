"""L11 sizing_engine - resolves the effective lot.

Broker minimum lot is the authority: effective_lot = clamp(normalize(risk_based
or requested), broker.min_lot, max_lot). Exact decimal arithmetic, lot_step
quantization down. Kelly fraction is capped at config (kelly_fraction_cap).
"""
from __future__ import annotations

from david_sling.core.schemas import SymbolSpec
from david_sling.core.utils import quantize_down, to_decimal


class SizingEngine:
    def __init__(self, cfg: dict | None = None) -> None:
        lp = (cfg or {}).get("lot_policy", {})
        self.mode = lp.get("mode", "risk_based")
        self.kelly_cap = float(lp.get("kelly_fraction_cap", 0.25))
        self.max_lot_cap = float(lp.get("max_lot_cap", 20.0))
        self.enforce_min_lot = bool(lp.get("enforce_broker_min_lot", True))

    def risk_based_lot(self, spec: SymbolSpec, risk_amount: float, sl_distance: float) -> float:
        """lots = risk_amount / (sl_distance_points * tick_value)."""
        if sl_distance <= 0 or spec.tick_value <= 0:
            return 0.0
        sl_points = sl_distance / spec.tick_size
        denom = sl_points * spec.tick_value
        if denom <= 0:
            return 0.0
        return risk_amount / denom

    def normalize(self, spec: SymbolSpec, lots: float) -> float:
        d = quantize_down(to_decimal(lots), to_decimal(spec.lot_step))
        return float(d)

    def effective_lot(self, spec: SymbolSpec, requested_lot: float, risk_based_lot: float) -> float:
        """Resolve effective lot. Broker minimum lot is the authority."""
        raw = risk_based_lot if self.mode == "risk_based" else requested_lot
        if self.mode == "kelly_capped":
            raw = min(requested_lot, risk_based_lot / max(self.kelly_cap, 1e-9) * self.kelly_cap)
        raw = max(raw, requested_lot) if self.mode == "fixed" else raw
        lot = self.normalize(spec, raw)
        if self.enforce_min_lot:
            lot = max(lot, spec.min_lot) if lot > 0 else 0.0
        lot = min(lot, min(spec.max_lot, self.max_lot_cap))
        if 0 < lot < spec.min_lot:
            lot = 0.0
        return round(lot, 8)

    def lots_for_risk(self, spec: SymbolSpec, risk_amount: float, sl_distance: float,
                      requested_lot: float | None = None) -> float:
        rb = self.risk_based_lot(spec, risk_amount, sl_distance)
        if requested_lot is not None and self.mode != "risk_based":
            return self.effective_lot(spec, requested_lot, rb)
        lot = self.effective_lot(spec, requested_lot or rb, rb)
        return lot
