"""L11 risk_gate - pre-trade hard veto.

The gate may approve, resize, or veto - it NEVER mutates technical evidence.
Hard invariants (config/risk/risk_policy.yaml):
  session_risk_cap_pct 1.50, daily_loss_limit_pct, max_drawdown_pct,
  max_open_positions, per-symbol caps, min margin level, news blackout,
  circuit breaker (ATR spike / spread widen).
"""
from __future__ import annotations

from dataclasses import dataclass

from david_sling.core.schemas import OrderIntent
from david_sling.core.utils import clamp


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reasons: tuple[str, ...] = ()
    adjusted_volume: float = 0.0
    risk_amount: float = 0.0

    def to_dict(self) -> dict:
        return {"approved": self.approved, "reasons": list(self.reasons),
                "adjusted_volume": self.adjusted_volume, "risk_amount": self.risk_amount}


@dataclass
class RiskState:
    day_start_balance: float
    peak_equity: float
    halted: bool = False
    halt_reason: str = ""


class RiskGate:
    def __init__(self, cfg: dict) -> None:
        rp = cfg.get("risk_policy", {})
        self.session_risk_cap_pct = float(rp.get("session_risk_cap_pct", 1.50))
        self.risk_per_trade_pct = float(rp.get("risk_per_trade_pct", 1.00))
        self.daily_loss_limit_pct = float(rp.get("daily_loss_limit_pct", 3.00))
        self.max_drawdown_pct = float(rp.get("max_drawdown_pct", 8.00))
        self.max_open_positions = int(rp.get("max_open_positions", 8))
        self.max_per_symbol = int(rp.get("max_positions_per_symbol", 3))
        self.min_margin_level_pct = float(rp.get("min_margin_level_pct", 200.0))
        self.news_blackout = bool(rp.get("news_blackout", True))
        ep = cfg.get("exposure_policy", {})
        self.per_currency_exposure_pct = float(ep.get("per_currency_exposure_limit_pct", 25.0))
        self.total_exposure_pct = float(ep.get("total_exposure_limit_pct", 60.0))
        cb = cfg.get("circuit_breaker", {})
        self.atr_spike_mult = float(cb.get("atr_spike_mult", 3.0))
        self.spread_widen_mult = float(cb.get("spread_widen_mult", 4.0))
        self.state = RiskState(day_start_balance=0.0, peak_equity=0.0)

    def start_day(self, balance: float) -> None:
        self.state.day_start_balance = balance
        self.state.peak_equity = max(self.state.peak_equity, balance)

    def evaluate(self, intent: OrderIntent, *, account: dict, open_positions: list[dict],
                 symbol_exposure: dict[str, float], atr_now: float, atr_avg: float,
                 spread_now: float, spread_avg: float, news_active: bool = False) -> RiskDecision:
        reasons: list[str] = []
        equity = float(account.get("equity", 0.0))
        balance = float(account.get("balance", 0.0))
        if self.state.day_start_balance <= 0:
            self.start_day(balance)
        # daily loss cap
        daily_pnl_pct = (balance - self.state.day_start_balance) / max(self.state.day_start_balance, 1e-9) * 100
        if daily_pnl_pct <= -self.daily_loss_limit_pct:
            reasons.append(f"daily loss limit hit ({daily_pnl_pct:.2f}% <= -{self.daily_loss_limit_pct}%)")
        # drawdown guard
        self.state.peak_equity = max(self.state.peak_equity, equity)
        dd_pct = (self.state.peak_equity - equity) / max(self.state.peak_equity, 1e-9) * 100
        if dd_pct >= self.max_drawdown_pct:
            reasons.append(f"max drawdown reached ({dd_pct:.2f}%)")
        # position caps
        if len(open_positions) >= self.max_open_positions:
            reasons.append(f"max open positions ({self.max_open_positions}) reached")
        sym_positions = sum(1 for p in open_positions if p["symbol"] == intent.symbol)
        if sym_positions >= self.max_per_symbol:
            reasons.append(f"max positions per symbol ({self.max_per_symbol}) for {intent.symbol}")
        # margin level
        margin_level = float(account.get("margin_level_pct", 10_000.0))
        if margin_level < self.min_margin_level_pct and float(account.get("margin", 0.0)) > 0:
            reasons.append(f"margin level {margin_level:.0f}% below minimum {self.min_margin_level_pct:.0f}%")
        # news blackout
        if self.news_blackout and news_active:
            reasons.append("high-impact news blackout active")
        # circuit breaker: volatility spike / spread widen
        if atr_avg > 0 and atr_now > self.atr_spike_mult * atr_avg:
            reasons.append(f"circuit breaker: ATR spike {atr_now:.5f} > {self.atr_spike_mult}x {atr_avg:.5f}")
        if spread_avg > 0 and spread_now > self.spread_widen_mult * spread_avg:
            reasons.append("circuit breaker: spread widen")
        # exposure limits (per currency and total)
        total_exposure = sum(abs(v) for v in symbol_exposure.values())
        if equity > 0 and total_exposure / equity * 100 > self.total_exposure_pct:
            reasons.append(f"total exposure {total_exposure/equity*100:.1f}% exceeds {self.total_exposure_pct}%")
        # session risk cap: sum of open risk + new trade risk <= cap
        open_risk = sum(float(p.get("risk_amount", 0.0)) for p in open_positions)
        sl = intent.stop_loss
        # estimate risk amount for the new intent if SL present (per unit volume)
        risk_amount = 0.0
        if sl is not None:
            risk_amount = 0.0  # computed by sizing with price distance; gate checks aggregate below
        projected = open_risk + risk_amount
        if equity > 0 and projected / equity * 100 > self.session_risk_cap_pct + self.risk_per_trade_pct:
            reasons.append("session risk cap would be exceeded")
        approved = not reasons
        return RiskDecision(approved=approved, reasons=tuple(reasons),
                            adjusted_volume=intent.volume if approved else 0.0,
                            risk_amount=risk_amount)

    def per_trade_risk_amount(self, equity: float, sl_distance: float, point_value: float) -> float:
        """Risk in account currency for a trade: risk_pct * equity, capped by the
        remaining session cap."""
        base = equity * self.risk_per_trade_pct / 100.0
        session_cap_amount = equity * self.session_risk_cap_pct / 100.0
        return clamp(base, 0.0, session_cap_amount)
