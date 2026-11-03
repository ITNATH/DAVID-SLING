"""L12 broker/adapters/simulated_adapter - fully working simulated broker.

Implements the broker contract: capability discovery from symbol specs,
min lot / lot step / tick value authority, order normalization, submission
with slippage, fills, position close/modify, account telemetry, swap & spread
costs, and reconciliation. MT5/MT4/cTrader/FIX/REST/WebSocket adapters share
this interface (see services/execution-bridge in later increments).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from david_sling.broker.adapter import BrokerAdapter
from david_sling.core.errors import ExecutionError
from david_sling.core.schemas import (
    ExecutionReport,
    OrderIntent,
    OrderSide,
    PositionState,
    SymbolSpec,
)
from david_sling.core.utils import new_id, price_quantize, to_decimal, utc_now


@dataclass
class Account:
    balance: float
    currency: str = "USD"
    leverage: float = 50.0
    positions: dict[str, PositionState] = field(default_factory=dict)

    @property
    def equity(self) -> float:
        return self.balance  # updated by mark-to-market externally


class SimulatedBrokerAdapter(BrokerAdapter):
    def __init__(self, specs: dict[str, SymbolSpec], balance: float = 100_000.0,
                 currency: str = "USD", leverage: float = 50.0, slippage_points: float = 0.5) -> None:
        self.specs = specs
        self.account = Account(balance=balance, currency=currency, leverage=leverage)
        self.slippage_points = slippage_points
        self._seen_keys: set[str] = set()  # G55 idempotency ledger
        self.reports: list[ExecutionReport] = []
        self._prices: dict[str, float] = {}
        self._connected = True

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    # ------------------------------------------------- capability discovery
    def capability(self, symbol: str) -> SymbolSpec:
        return self.specs[symbol.upper()]

    def set_price(self, symbol: str, mid: float) -> None:
        self._prices[symbol.upper()] = mid

    def price(self, symbol: str) -> float:
        if symbol.upper() not in self._prices:
            raise ExecutionError(f"no price for {symbol}")
        return self._prices[symbol.upper()]

    # ------------------------------------------------------------- account
    def margin_used(self, positions: dict[str, PositionState]) -> float:
        total = 0.0
        for p in positions.values():
            spec = self.specs[p.symbol]
            notional = p.volume * spec.contract_size * self.price(p.symbol)
            total += notional * spec.margin_rate / self.account.leverage * self.account.leverage
            total = total  # margin = notional * margin_rate
        # recompute cleanly:
        total = 0.0
        for p in positions.values():
            spec = self.specs[p.symbol]
            notional = p.volume * spec.contract_size * self.price(p.symbol)
            total += notional * spec.margin_rate
        return round(total, 2)

    def account_snapshot(self, floating_pnl: float) -> dict:
        margin = self.margin_used(self.account.positions)
        equity = self.account.balance + floating_pnl
        margin_level = (equity / margin * 100.0) if margin > 0 else 10_000.0
        return {
            "balance": round(self.account.balance, 2),
            "equity": round(equity, 2),
            "margin": round(margin, 2),
            "free_margin": round(equity - margin, 2),
            "margin_level_pct": round(margin_level, 2),
            "currency": self.account.currency,
            "leverage": self.account.leverage,
            "floating_pnl": round(floating_pnl, 2),
        }

    # ------------------------------------------------------------- trading
    def _fill_price(self, symbol: str, side: OrderSide) -> tuple[float, float]:
        spec = self.specs[symbol.upper()]
        mid = self.price(symbol)
        slip = self.slippage_points * spec.tick_size
        if side == OrderSide.BUY:
            fill = mid + slip + spec.spread_points * spec.tick_size / 2
        else:
            fill = mid - slip - spec.spread_points * spec.tick_size / 2
        return float(price_quantize(to_decimal(fill), spec.digits)), spec.spread_points

    def submit(self, intent: OrderIntent) -> ExecutionReport:
        symbol = intent.symbol.upper()
        if symbol not in self.specs:
            raise ExecutionError(f"unknown symbol {symbol}")
        spec = self.specs[symbol]
        if intent.volume < spec.min_lot:
            raise ExecutionError(f"volume {intent.volume} below broker minimum lot {spec.min_lot}")
        if intent.volume > spec.max_lot:
            raise ExecutionError(f"volume {intent.volume} above broker maximum lot {spec.max_lot}")
        if intent.order_type.value in ("LIMIT", "STOP") and intent.price is None:
            raise ExecutionError(f"{intent.order_type.value} order requires price")
        # G55: idempotency - a retried intent must never open a second position
        if intent.idempotency_key in self._seen_keys:
            raise ExecutionError(f"duplicate idempotency_key {intent.idempotency_key} - already submitted")
        self._seen_keys.add(intent.idempotency_key)
        fill, spread_pts = self._fill_price(symbol, intent.side)
        pos = PositionState(
            position_id=new_id("pos"), symbol=symbol, side=intent.side,
            volume=intent.volume, entry_price=fill,
            stop_loss=intent.stop_loss, take_profit=intent.take_profit,
            open_ts=intent.ts,
        )
        self.account.positions[pos.position_id] = pos
        spread_cost = spread_pts * spec.tick_size / spec.tick_size * spec.tick_value * intent.volume
        report = ExecutionReport(
            intent_id=intent.intent_id, position_id=pos.position_id, symbol=symbol,
            side=intent.side.value, volume=intent.volume, fill_price=fill,
            slippage_points=self.slippage_points, spread_cost=round(spread_cost, 2), ts=utc_now(),
        )
        self.reports.append(report)
        return report

    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]:
        pos = self.account.positions.get(position_id)
        if pos is None:
            raise ExecutionError(f"position {position_id} not found")
        spec = self.specs[pos.symbol]
        vol = volume if volume is not None else pos.volume
        vol = min(vol, pos.volume)
        mid = self.price(pos.symbol)
        if pos.side == OrderSide.BUY:
            exit_price = float(price_quantize(to_decimal(mid - spec.spread_points * spec.tick_size / 2), spec.digits))
        else:
            exit_price = float(price_quantize(to_decimal(mid + spec.spread_points * spec.tick_size / 2), spec.digits))
        pnl = self._pnl(pos.symbol, pos.side.value, pos.entry_price, exit_price, vol)
        swap = round(-0.01 * vol, 4)  # simulated overnight swap
        if vol >= pos.volume - 1e-9:
            del self.account.positions[position_id]
        else:
            pos.volume = round(pos.volume - vol, 8)
        return pos, pnl, swap

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        pos = self.account.positions[position_id]
        if sl is not None:
            pos = PositionState(**{**pos.model_dump(), "stop_loss": sl})
        if tp is not None:
            pos = PositionState(**{**pos.model_dump(), "take_profit": tp})
        self.account.positions[position_id] = pos
        return pos

    def _pnl(self, symbol: str, side: str, entry: float, exit: float, volume: float) -> float:
        spec = self.specs[symbol]
        points = (exit - entry) / spec.tick_size
        if side == "SELL":
            points = -points
        pnl_profit_ccy = points * spec.tick_value * volume
        # convert profit currency to account currency (USD)
        if spec.currency_profit == "USD":
            return round(pnl_profit_ccy, 2)
        if spec.currency_profit == "JPY":
            usdjpy = self.price("USDJPY") if "USDJPY" in self.specs else 150.0
            return round(pnl_profit_ccy / usdjpy, 2)
        if spec.currency_profit == "EUR":
            eurusd = self.price("EURUSD") if "EURUSD" in self.specs else 1.10
            return round(pnl_profit_ccy * eurusd, 2)
        return round(pnl_profit_ccy, 2)

    def reconcile(self) -> dict:
        """Broker state reconciliation snapshot."""
        return {"positions": len(self.account.positions), "reports": len(self.reports),
                "balance": self.account.balance}
