"""L12 broker/mt5_adapter - MetaTrader 5 live execution adapter.

Transport: the official `MetaTrader5` Python package (pip install MetaTrader5,
only served for win32; requires a running MT5 terminal). Connection requires
credentials from the account config or env DAVID_SLING_MT5_LOGIN / _PASSWORD /
_SERVER. Any missing dependency or credential raises SecurityError /
ExecutionError at connect() - orders are never silently dropped.

Thread-safety: every terminal call is serialized behind a re-entrant lock so
the GUI worker thread and the runtime loops can share the adapter safely.
Tickets: MT5 position tickets (result.order) are tracked per position_id and
used for close/modify - never a hardcoded 0.
"""
from __future__ import annotations

import os
import threading
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
        self._lock = threading.RLock()
        self._positions: dict[str, PositionState] = {}
        self._tickets: dict[str, int] = {}  # position_id -> MT5 position ticket
        self._reports: list[ExecutionReport] = []

    # ------------------------------------------------------------ lifecycle
    @property
    def is_connected(self) -> bool:
        return self._connected and self._mt5 is not None

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
        with self._lock:
            if not mt5.initialize(login=login, password=password, server=server):
                raise ExecutionError(f"MT5 initialize failed: {mt5.last_error()}")
            for sym in self.specs:
                mt5.symbol_select(sym, True)  # make symbol visible in Market Watch
            self._mt5 = mt5
            self._connected = True

    def disconnect(self) -> None:
        with self._lock:
            if self._mt5 is not None:
                self._mt5.shutdown()
            self._connected = False

    def _require(self) -> None:
        if not self.is_connected:
            raise ExecutionError("MT5 adapter not connected - call connect() first")

    def _send(self, request: dict) -> Any:
        """Serialized order_send with retcode validation - never silent."""
        mt5 = self._mt5
        result = mt5.order_send(request)
        if result is None:
            raise ExecutionError(f"MT5 order_send returned None: {mt5.last_error()}")
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise ExecutionError(f"MT5 order_send rejected: retcode={result.retcode} {mt5.last_error()}")
        return result

    # ------------------------------------------------------------ execution
    def submit(self, intent: OrderIntent) -> ExecutionReport:
        with self._lock:
            self._require()
            mt5 = self._mt5
            info = mt5.symbol_info(intent.symbol)
            if info is None:
                raise ExecutionError(f"symbol {intent.symbol} not found on broker")
            if not info.visible:
                mt5.symbol_select(intent.symbol, True)
            tick = mt5.symbol_info_tick(intent.symbol)
            if tick is None:
                raise ExecutionError(f"no tick for {intent.symbol} - stale terminal data")
            price = tick.ask if intent.side == OrderSide.BUY else tick.bid
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": intent.symbol,
                "volume": float(intent.volume),
                "type": mt5.ORDER_TYPE_BUY if intent.side == OrderSide.BUY else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": float(intent.stop_loss or 0.0),
                "tp": float(intent.take_profit or 0.0),
                "deviation": 20,
                "magic": 0,
                "comment": "DAVID-SLING",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = self._send(request)
            pos = PositionState(
                position_id=new_id("pos"), symbol=intent.symbol, side=intent.side,
                volume=float(result.volume), entry_price=float(result.price),
                stop_loss=intent.stop_loss, take_profit=intent.take_profit, open_ts=utc_now(),
            )
            self._positions[pos.position_id] = pos
            self._tickets[pos.position_id] = int(result.order)  # real MT5 ticket
            rep = ExecutionReport(intent_id=intent.intent_id, status="FILLED", fill_price=float(result.price),
                                  volume=float(result.volume), position_id=pos.position_id,
                                  symbol=intent.symbol, side=intent.side.value, ts=utc_now())
            self._reports.append(rep)
            return rep

    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]:
        with self._lock:
            self._require()
            pos = self._positions.get(position_id)
            if pos is None:
                raise ExecutionError(f"position {position_id} not found")
            ticket = self._tickets.get(position_id)
            if not ticket:
                raise ExecutionError(f"no MT5 ticket for position {position_id}")
            mt5 = self._mt5
            tick = mt5.symbol_info_tick(pos.symbol)
            if tick is None:
                raise ExecutionError(f"no tick for {pos.symbol} - stale terminal data")
            price = tick.bid if pos.side == OrderSide.BUY else tick.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": pos.symbol,
                "volume": float(volume or pos.volume),
                "type": mt5.ORDER_TYPE_SELL if pos.side == OrderSide.BUY else mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": 20,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = self._send(request)
            pnl = float(result.profit)
            del self._positions[position_id]
            self._tickets.pop(position_id, None)
            return pos, pnl, 0.0

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        with self._lock:
            self._require()
            pos = self._positions.get(position_id)
            if pos is None:
                raise ExecutionError(f"position {position_id} not found")
            ticket = self._tickets.get(position_id)
            if not ticket:
                raise ExecutionError(f"no MT5 ticket for position {position_id}")
            request = {
                "action": self._mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": pos.symbol,
                "sl": float(sl if sl is not None else (pos.stop_loss or 0.0)),
                "tp": float(tp if tp is not None else (pos.take_profit or 0.0)),
            }
            self._send(request)
            if sl is not None:
                pos.stop_loss = sl
            if tp is not None:
                pos.take_profit = tp
            return pos

    def cancel_pending(self) -> int:
        """Cancel ALL pending orders on the terminal (PANIC FLATTEN support)."""
        with self._lock:
            self._require()
            mt5 = self._mt5
            orders = mt5.orders_get() or []
            n = 0
            for o in orders:
                result = mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
                if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                    n += 1
            return n

    def set_price(self, symbol: str, price: float) -> None:
        return None  # live adapter: prices stream from the terminal

    # ------------------------------------------------------------ state
    def account_snapshot(self, floating_pnl: float) -> dict:
        with self._lock:
            self._require()
            info = self._mt5.account_info()
            if info is None:
                raise ExecutionError(f"account_info unavailable: {self._mt5.last_error()}")
            return {"balance": float(info.balance), "equity": float(info.equity),
                    "margin": float(info.margin), "free_margin": float(info.margin_free),
                    "margin_level_pct": float(info.margin_level), "currency": info.currency,
                    "leverage": float(info.leverage), "floating_pnl": floating_pnl}

    def reconcile(self) -> dict:
        """Live sync: pull terminal positions/pending orders and mirror them."""
        with self._lock:
            self._require()
            mt5 = self._mt5
            positions = []
            for p in (mt5.positions_get() or []):
                positions.append({"ticket": p.ticket, "symbol": p.symbol, "type": p.type,
                                  "volume": float(p.volume), "price_open": float(p.price_open),
                                  "sl": float(p.sl), "tp": float(p.tp), "profit": float(p.profit)})
            pending = len(mt5.orders_get() or [])
            return {"positions": positions, "pending_orders": pending, "reports": len(self._reports),
                    "connected": True, "login": self._mt5.account_info().login if self._mt5.account_info() else None}
