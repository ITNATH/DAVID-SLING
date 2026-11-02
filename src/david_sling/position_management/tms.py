"""L12 TMS - active position lifecycle.

  breakeven   : at +1.5 ATR move -> SL to entry
  trailing    : at +2.0R -> trail SL by 1 ATR behind price
  spike defense: ATR > 3x recent -> tighten / close
  TP/SL       : broker-side levels checked per tick
  partials    : 25% / 50% / 75% closes
  batch close : per-pair / cross-pair filters; panic flatten
Global policy: max_hold_time = null (no time stop).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from david_sling.broker.simulated import SimulatedBrokerAdapter
from david_sling.core.schemas import OrderSide, PositionState, SymbolSpec
from david_sling.core.utils import utc_now

BREAKEVEN_ATR_MULT = 1.5
TRAILING_R = 2.0
SPIKE_DEFENSE_MULT = 3.0


@dataclass
class ClosedTrade:
    position_id: str
    symbol: str
    side: str
    volume: float
    entry: float
    exit: float
    pnl: float
    swap: float
    reason: str
    open_ts: datetime
    close_ts: datetime


@dataclass
class TMSResult:
    closed: list[ClosedTrade] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)


class TradeManagementLifecycle:
    def __init__(self, broker: SimulatedBrokerAdapter, specs: dict[str, SymbolSpec]) -> None:
        self.broker = broker
        self.specs = specs
        self.closed_history: list[ClosedTrade] = []
        self.risk_amounts: dict[str, float] = {}   # position_id -> risk at entry

    # ------------------------------------------------------------- per tick
    def on_tick(self, symbol: str, bid: float, ask: float, atr_now: float, atr_avg: float) -> TMSResult:
        result = TMSResult()
        price = (bid + ask) / 2
        for pos_id, pos in list(self.broker.account.positions.items()):
            if pos.symbol != symbol:
                continue
            spec = self.specs[symbol]
            # spike defense
            if atr_avg > 0 and atr_now > SPIKE_DEFENSE_MULT * atr_avg:
                self._close(pos_id, "spike_defense", result)
                continue
            # TP/SL
            if pos.side == OrderSide.BUY:
                if pos.stop_loss is not None and bid <= pos.stop_loss:
                    self._close(pos_id, "stop_loss", result)
                    continue
                if pos.take_profit is not None and bid >= pos.take_profit:
                    self._close(pos_id, "take_profit", result)
                    continue
                favorable = price - pos.entry_price
            else:
                if pos.stop_loss is not None and ask >= pos.stop_loss:
                    self._close(pos_id, "stop_loss", result)
                    continue
                if pos.take_profit is not None and ask <= pos.take_profit:
                    self._close(pos_id, "take_profit", result)
                    continue
                favorable = pos.entry_price - price
            # breakeven at +1.5 ATR
            if not pos.breakeven_done and atr_now > 0 and favorable >= BREAKEVEN_ATR_MULT * atr_now:
                self.broker.modify(pos_id, sl=pos.entry_price)
                p = self.broker.account.positions[pos_id]
                self.broker.account.positions[pos_id] = PositionState(
                    **{**p.model_dump(), "breakeven_done": True})
                result.modified.append(pos_id)
                pos = self.broker.account.positions[pos_id]
            # trailing at +2.0R
            sl_dist = abs(pos.entry_price - (pos.stop_loss or pos.entry_price))
            if sl_dist > 0 and favorable >= TRAILING_R * sl_dist:
                new_sl = price - atr_now if pos.side == OrderSide.BUY else price + atr_now
                if pos.side == OrderSide.BUY and (pos.stop_loss is None or new_sl > pos.stop_loss) or pos.side == OrderSide.SELL and (pos.stop_loss is None or new_sl < pos.stop_loss):
                    self.broker.modify(pos_id, sl=round(new_sl, spec.digits))
                    p = self.broker.account.positions[pos_id]
                    self.broker.account.positions[pos_id] = PositionState(
                        **{**p.model_dump(), "trailing_active": True})
                    result.modified.append(pos_id)
        return result

    # ------------------------------------------------------------- closes
    def _close(self, position_id: str, reason: str, result: TMSResult) -> None:
        pos, pnl, swap = self.broker.close(position_id)
        trade = ClosedTrade(position_id=position_id, symbol=pos.symbol, side=pos.side.value,
                            volume=pos.volume, entry=pos.entry_price, exit=pos.entry_price,
                            pnl=pnl, swap=swap, reason=reason, open_ts=pos.open_ts, close_ts=utc_now())
        # exit price recompute for record
        self.closed_history.append(trade)
        self.broker.account.balance += pnl + swap
        result.closed.append(trade)
        self.risk_amounts.pop(position_id, None)

    def partial_close(self, position_id: str, pct: float) -> ClosedTrade | None:
        pos = self.broker.account.positions.get(position_id)
        if pos is None:
            return None
        vol = round(pos.volume * pct, 8)
        if 0 < pos.volume - vol < self.specs[pos.symbol].min_lot:
            vol = pos.volume  # never leave a sub-min-lot dust residual
        if vol <= 0:
            return None
        _, pnl, swap = self.broker.close(position_id, volume=vol)
        self.broker.account.balance += pnl + swap
        trade = ClosedTrade(position_id=position_id, symbol=pos.symbol, side=pos.side.value,
                            volume=vol, entry=pos.entry_price, exit=pos.entry_price, pnl=pnl, swap=swap,
                            reason=f"partial_{int(pct*100)}pct", open_ts=pos.open_ts, close_ts=utc_now())
        self.closed_history.append(trade)
        return trade

    def close_position(self, position_id: str, reason: str = "manual") -> ClosedTrade | None:
        if position_id not in self.broker.account.positions:
            return None
        result = TMSResult()
        self._close(position_id, reason, result)
        return result.closed[0] if result.closed else None

    def batch_close(self, *, symbol: str | None = None, side: str | None = None,
                    only_profitable: bool = False, only_losing: bool = False) -> list[ClosedTrade]:
        out: list[ClosedTrade] = []
        for pos_id, pos in list(self.broker.account.positions.items()):
            if symbol and pos.symbol != symbol:
                continue
            if side and pos.side.value != side:
                continue
            mid = self.broker.price(pos.symbol)
            pnl = self.broker._pnl(pos.symbol, pos.side.value, pos.entry_price, mid, pos.volume)
            if only_profitable and pnl <= 0:
                continue
            if only_losing and pnl >= 0:
                continue
            trade = self.close_position(pos_id, reason="batch_close")
            if trade:
                out.append(trade)
        return out

    def panic_flatten(self) -> list[ClosedTrade]:
        return self.batch_close()

    def breakeven_all(self) -> list[str]:
        out: list[str] = []
        for pos_id, pos in list(self.broker.account.positions.items()):
            self.broker.modify(pos_id, sl=pos.entry_price)
            p = self.broker.account.positions[pos_id]
            self.broker.account.positions[pos_id] = PositionState(**{**p.model_dump(), "breakeven_done": True})
            out.append(pos_id)
        return out
