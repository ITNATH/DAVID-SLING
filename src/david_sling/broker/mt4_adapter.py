"""L12 broker/mt4_adapter - MetaTrader 4 live execution adapter.

Transport: MT4 terminal via the `MetaTrader4` Python package or an MT4 bridge
(FIX/EA). Credentials: account config or DAVID_SLING_MT4_* env. Missing
transport/credentials raise at connect() - never silently.
"""
from __future__ import annotations

import os
from typing import Any

from david_sling.broker.adapter import BrokerAdapter
from david_sling.core.errors import ExecutionError, SecurityError
from david_sling.core.schemas import (
    ExecutionReport,
    OrderIntent,
    OrderSide,
    PositionState,
    SymbolSpec,
)
from david_sling.core.utils import new_id, utc_now


class Mt4Adapter(BrokerAdapter):
    def __init__(self, specs: dict[str, SymbolSpec], account_cfg: dict) -> None:
        self.specs = specs
        self.cfg = account_cfg
        self._mt4: Any = None
        self._connected = False
        self._positions: dict[str, PositionState] = {}
        self._reports: list[ExecutionReport] = []

    def connect(self) -> None:
        try:
            import MetaTrader4 as mt4  # type: ignore
        except ImportError as exc:
            raise ExecutionError(
                "MetaTrader4 package/bridge not available - install MetaTrader4 or an MT4 FIX bridge"
            ) from exc
        login = int(self.cfg.get("login") or os.environ.get("DAVID_SLING_MT4_LOGIN", "0"))
        password = self.cfg.get("password") or os.environ.get("DAVID_SLING_MT4_PASSWORD", "")
        server = self.cfg.get("server") or os.environ.get("DAVID_SLING_MT4_SERVER", "")
        if not login or not password or not server:
            raise SecurityError("MT4 adapter requires login/password/server (config or DAVID_SLING_MT4_* env)")
        if not mt4.initialize(login=login, password=password, server=server):
            raise ExecutionError(f"MT4 initialize failed: {mt4.last_error()}")
        self._mt4 = mt4
        self._connected = True

    def disconnect(self) -> None:
        if self._mt4 is not None:
            self._mt4.shutdown()
        self._connected = False

    def _require(self) -> None:
        if not self._connected or self._mt4 is None:
            raise ExecutionError("MT4 adapter not connected - call connect() first")

    def submit(self, intent: OrderIntent) -> ExecutionReport:
        self._require()
        mt4 = self._mt4
        tick = mt4.symbol_info_tick(intent.symbol)
        if tick is None:
            raise ExecutionError(f"symbol {intent.symbol} not found on broker")
        price = tick.ask if intent.side == OrderSide.BUY else tick.bid
        order_type = mt4.ORDER_TYPE_BUY if intent.side == OrderSide.BUY else mt4.ORDER_TYPE_SELL
        request = {"action": mt4.TRADE_ACTION_DEAL, "symbol": intent.symbol, "volume": intent.volume,
                   "type": order_type, "price": price, "sl": intent.stop_loss or 0.0,
                   "tp": intent.take_profit or 0.0, "deviation": 20, "comment": "DAVID-SLING",
                   "type_time": mt4.ORDER_TIME_GTC, "type_filling": mt4.ORDER_FILLING_IOC}
        result = mt4.order_send(request)
        if result is None or result.retcode != mt4.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT4 order_send rejected: {result.retcode if result else 'no result'}")
        pos = PositionState(position_id=new_id("pos"), symbol=intent.symbol, side=intent.side,
                            volume=result.volume, entry_price=result.price, open_ts=utc_now())
        self._positions[pos.position_id] = pos
        rep = ExecutionReport(intent_id=intent.intent_id, status="FILLED", fill_price=result.price,
                              volume=result.volume, position_id=pos.position_id, ts=utc_now())
        self._reports.append(rep)
        return rep

    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]:
        self._require()
        pos = self._positions.get(position_id)
        if pos is None:
            raise ExecutionError(f"position {position_id} not found")
        mt4 = self._mt4
        tick = mt4.symbol_info_tick(pos.symbol)
        price = tick.bid if pos.side == OrderSide.BUY else tick.ask
        result = mt4.order_send({"action": mt4.TRADE_ACTION_DEAL, "symbol": pos.symbol,
                                 "volume": volume or pos.volume,
                                 "type": mt4.ORDER_TYPE_SELL if pos.side == OrderSide.BUY else mt4.ORDER_TYPE_BUY,
                                 "price": price, "deviation": 20, "type_time": mt4.ORDER_TIME_GTC,
                                 "type_filling": mt4.ORDER_FILLING_IOC})
        if result is None or result.retcode != mt4.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT4 close rejected: {result.retcode if result else 'no result'}")
        del self._positions[position_id]
        return pos, result.profit, 0.0

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        self._require()
        pos = self._positions[position_id]
        result = self._mt4.order_send({"action": self._mt4.TRADE_ACTION_SLTP, "symbol": pos.symbol,
                                       "sl": sl if sl is not None else pos.stop_loss or 0.0,
                                       "tp": tp if tp is not None else pos.take_profit or 0.0})
        if result is None or result.retcode != self._mt4.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT4 modify rejected: {result.retcode if result else 'no result'}")
        if sl is not None:
            pos.stop_loss = sl
        if tp is not None:
            pos.take_profit = tp
        return pos

    def set_price(self, symbol: str, price: float) -> None:
        return None

    def account_snapshot(self, floating_pnl: float) -> dict:
        self._require()
        info = self._mt4.account_info()
        return {"balance": info.balance, "equity": info.equity, "margin": info.margin,
                "free_margin": info.margin_free, "margin_level_pct": info.margin_level,
                "currency": info.currency, "leverage": info.leverage, "floating_pnl": floating_pnl}

    def reconcile(self) -> dict:
        self._require()
        return {"positions": len(self._mt4.positions_get() or []), "reports": len(self._reports)}
