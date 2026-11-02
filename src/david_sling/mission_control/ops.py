"""mission_control/multi_trade_operations_engine - Omni-Trade operations.

  single trade          : one OrderIntent through boundary -> risk -> broker
  single-pair multi     : tranche ladder on one symbol (scale-in), batch close
  cross-pair basket     : simultaneous multi-symbol basket with correlation
                          guard + aggregate PnL + panic flatten
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from david_sling.core.errors import MultiTradeError
from david_sling.core.schemas import (
    BasketType,
    MultiTradeIntent,
    OrderIntent,
    OrderSide,
    OrderType,
)
from david_sling.core.utils import new_id, utc_now
from david_sling.execution_boundary.firewall import ExecutionBoundary
from david_sling.portfolio.exposure import PortfolioExposure
from david_sling.risk.gate import RiskGate
from david_sling.sizing.engine import SizingEngine


@dataclass
class OpResult:
    ok: bool
    orders: list[dict[str, Any]]
    vetoed: list[dict[str, Any]]
    message: str


class MultiTradeOperationsEngine:
    def __init__(self, boundary: ExecutionBoundary, risk: RiskGate, sizing: SizingEngine,
                 portfolio: PortfolioExposure, order_submit, specs: dict, price_fn) -> None:
        self.boundary = boundary
        self.risk = risk
        self.sizing = sizing
        self.portfolio = portfolio
        self._submit = order_submit          # callable(intent, risk_decision) -> ManagedOrder
        self.specs = specs
        self._price = price_fn

    # ------------------------------------------------------------- helpers
    def _risk_check(self, intent: OrderIntent, account: dict, positions: list,
                    atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active: bool) -> Any:
        """Per-leg risk check with per-symbol ATR/spread (never cross-symbol)."""
        exposure = self.portfolio.net_exposure(positions, self.specs)
        open_dicts = [p.model_dump() if hasattr(p, "model_dump") else p for p in positions]
        decision = self.risk.evaluate(intent, account=account, open_positions=open_dicts,
                                      symbol_exposure=exposure, atr_now=atr_now_fn(intent.symbol),
                                      atr_avg=atr_avg_fn(intent.symbol),
                                      spread_now=spread_now_fn(intent.symbol), spread_avg=spread_avg_fn(intent.symbol),
                                      news_active=news_active)
        if decision.approved:
            from david_sling.risk.gate import RiskDecision

            ok, probs = self.portfolio.concentration_ok(exposure, float(account.get("equity", 0.0)))
            if not ok:
                decision = RiskDecision(approved=False, reasons=tuple(decision.reasons) + tuple(probs),
                                        adjusted_volume=0.0, risk_amount=decision.risk_amount)
        return decision

    # ------------------------------------------------------------- single
    def single_trade(self, *, symbol: str, side: OrderSide, volume: float | None,
                     order_type: OrderType, price: float | None, sl: float | None, tp: float | None,
                     risk_pct: float | None, account: dict, positions: list,
                     atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active: bool = False) -> OpResult:
        spec = self.specs[symbol]
        intent = self.boundary.manual_intent(symbol, side, volume or spec.min_lot, order_type=order_type,
                                             price=price, sl=sl, tp=tp, caller="mission_control")
        # sizing: risk-based lot from SL distance if risk_pct given
        if risk_pct is not None and sl is not None:
            risk_amount = account["equity"] * risk_pct / 100.0
            sl_dist = abs((price or self._price(symbol)) - sl)
            lot = self.sizing.lots_for_risk(spec, risk_amount, sl_dist)
            if lot > 0:
                intent = intent.model_copy(update={"volume": lot})
        decision = self._risk_check(intent, account, positions, atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active)
        if not decision.approved:
            return OpResult(False, [], [{"symbol": symbol, "reasons": list(decision.reasons)}],
                            "risk veto: " + "; ".join(decision.reasons))
        order = self._submit(intent, decision)
        return OpResult(True, [{"intent_id": order.intent.intent_id, "status": order.status.value,
                                "position_id": order.report.position_id if order.report else None,
                                "fill": order.report.fill_price if order.report else None}],
                        [], "filled")

    # --------------------------------------------------- single-pair multi
    def single_pair_multi(self, *, symbol: str, side: OrderSide, tranches: int, lots_per_tranche: float,
                          sl: float | None, tp: float | None, account: dict, positions: list,
                          atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active: bool = False) -> OpResult:
        if tranches < 1 or tranches > 10:
            raise MultiTradeError("tranches must be 1..10")
        basket = MultiTradeIntent(
            basket_id=new_id("bsk"), basket_type=BasketType.SINGLE_PAIR_MULTI,
            orders=[self.boundary.manual_intent(symbol, side, lots_per_tranche, sl=sl, tp=tp,
                                                 caller="mission_control") for _ in range(tranches)],
            ts=utc_now(),
        )
        return self._execute_basket(basket, account, positions, atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active)

    # ----------------------------------------------------- cross-pair basket
    def cross_pair_basket(self, *, symbols: list[str], side: OrderSide, lots: float,
                          sl_atr_mult: float, tp_rr: float, account: dict, positions: list,
                          atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active: bool = False) -> OpResult:
        if not symbols:
            raise MultiTradeError("basket requires at least one symbol")
        direction = "long" if side == OrderSide.BUY else "short"
        ok, problems = self.portfolio.basket_correlation_risk(symbols, direction)
        if not ok:
            return OpResult(False, [], [{"symbols": symbols, "reasons": problems}],
                            "correlation guard: " + "; ".join(problems))
        orders: list[OrderIntent] = []
        for symbol in symbols:
            price = self._price(symbol)
            atr = atr_now_fn(symbol) or price * 0.001
            if side == OrderSide.BUY:
                sl = price - sl_atr_mult * atr
                tp = price + tp_rr * sl_atr_mult * atr
            else:
                sl = price + sl_atr_mult * atr
                tp = price - tp_rr * sl_atr_mult * atr
            orders.append(self.boundary.manual_intent(symbol, side, lots, sl=sl, tp=tp, caller="mission_control"))
        basket = MultiTradeIntent(basket_id=new_id("bsk"), basket_type=BasketType.CROSS_PAIR_BASKET,
                                  orders=orders, ts=utc_now())
        return self._execute_basket(basket, account, positions, atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active)

    def _execute_basket(self, basket: MultiTradeIntent, account: dict, positions: list,
                        atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active: bool) -> OpResult:
        results_ok: list[dict] = []
        vetoed: list[dict] = []
        for intent in basket.orders:
            decision = self._risk_check(intent, account, positions, atr_now_fn, atr_avg_fn, spread_now_fn, spread_avg_fn, news_active)
            if not decision.approved:
                vetoed.append({"symbol": intent.symbol, "reasons": list(decision.reasons)})
                continue
            order = self._submit(intent, decision)
            results_ok.append({"intent_id": order.intent.intent_id, "symbol": intent.symbol,
                               "status": order.status.value,
                               "position_id": order.report.position_id if order.report else None,
                               "fill": order.report.fill_price if order.report else None})
        ok = not vetoed
        return OpResult(ok, results_ok, vetoed,
                        "basket filled" if ok else "basket partially/fully vetoed: " + str(vetoed))
