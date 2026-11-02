"""L12 broker/mt5_adapter - MetaTrader 5 live execution adapter.

Transport: the official `MetaTrader5` Python package (pip install MetaTrader5,
Windows/Linux with MT5 terminal installed). Connection requires credentials
from the account config or env DAVID_SLING_MT5_LOGIN / _PASSWORD / _SERVER.
Any missing dependency or credential raises SecurityError/ExecutionError at
connect() - orders are never silently dropped.
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


class Mt5Adapter(BrokerAdapter):
    def __init__(self, specs: dict[str, SymbolSpec], account_cfg: dict) -> None:
        self.specs = specs
        self.cfg = account_cfg
        self._mt5: Any = None
        self._connected = False
        self._positions: dict[str, PositionState] = {}
        self._reports: list[ExecutionReport] = []

    def connect(self) -> None:
        try:
            import MetaTrader5 as mt5  # type: ignore
        except ImportError as exc:
            raise ExecutionError(
                "MetaTrader5 package not available - install MetaTrader5 and run on a host with the MT5 terminal"
            ) from exc
        login = int(self.cfg.get("login") or os.environ.get("DAVID_SLING_MT5_LOGIN", "0"))
        password = self.cfg.get("password") or os.environ.get("DAVID_SLING_MT5_PASSWORD", "")
        server = self.cfg.get("server") or os.environ.get("DAVID_SLING_MT5_SERVER", "")
        if not login or not password or not server:
            raise SecurityError("MT5 adapter requires login/password/server (config or DAVID_SLING_MT5_* env)")
        if not mt5.initialize(login=login, password=password, server=server):
            raise ExecutionError(f"MT5 initialize failed: {mt5.last_error()}")
        self._mt5 = mt5
        self._connected = True

    def disconnect(self) -> None:
        if self._mt5 is not None:
            self._mt5.shutdown()
        self._connected = False

    def _require(self) -> None:
        if not self._connected or self._mt5 is None:
            raise ExecutionError("MT5 adapter not connected - call connect() first")

    def submit(self, intent: OrderIntent) -> ExecutionReport:
        self._require()
        mt5 = self._mt5
        tick = mt5.symbol_info_tick(intent.symbol)
        if tick is None:
            raise ExecutionError(f"symbol {intent.symbol} not found on broker")
        price = tick.ask if intent.side == OrderSide.BUY else tick.bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": intent.symbol,
            "volume": intent.volume,
            "type": mt5.ORDER_TYPE_BUY if intent.side == OrderSide.BUY else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": intent.stop_loss or 0.0,
            "tp": intent.take_profit or 0.0,
            "deviation": 20,
            "magic": 0,
            "comment": "DAVID-SLING",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT5 order_send rejected: {result.retcode if result else 'no result'} "
                                 f"{mt5.last_error()}")
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
        mt5 = self._mt5
        tick = mt5.symbol_info_tick(pos.symbol)
        price = tick.bid if pos.side == OrderSide.BUY else tick.ask
        request = {"action": mt5.TRADE_ACTION_DEAL, "position": int(position_id.split("-")[-1], 36) if False else 0,
                   "symbol": pos.symbol, "volume": volume or pos.volume,
                   "type": mt5.ORDER_TYPE_SELL if pos.side == OrderSide.BUY else mt5.ORDER_TYPE_BUY,
                   "price": price, "deviation": 20, "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC}
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT5 close rejected: {result.retcode if result else 'no result'}")
        pnl = result.profit
        del self._positions[position_id]
        return pos, pnl, 0.0

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        self._require()
        pos = self._positions[position_id]
        request = {"action": self._mt5.TRADE_ACTION_SLTP, "position": 0, "symbol": pos.symbol,
                   "sl": sl if sl is not None else pos.stop_loss or 0.0,
                   "tp": tp if tp is not None else pos.take_profit or 0.0}
        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT5 modify rejected: {result.retcode if result else 'no result'}")
        if sl is not None:
            pos.stop_loss = sl
        if tp is not None:
            pos.take_profit = tp
        return pos

    def set_price(self, symbol: str, price: float) -> None:
        return None  # live adapter: prices stream from the terminal

    def account_snapshot(self, floating_pnl: float) -> dict:
        self._require()
        info = self._mt5.account_info()
        return {"balance": info.balance, "equity": info.equity, "margin": info.margin,
                "free_margin": info.margin_free, "margin_level_pct": info.margin_level,
                "currency": info.currency, "leverage": info.leverage, "floating_pnl": floating_pnl}

    def reconcile(self) -> dict:
        self._require()
        return {"positions": len(self._mt5.positions_get() or []), "reports": len(self._reports)}
