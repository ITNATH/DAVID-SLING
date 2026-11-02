"""L12 broker/adapter - BrokerAdapter contract + registry.

Every broker adapter implements the same surface the L12 order/position
managers and the L11 risk/sizing layers talk to:
connect/disconnect, submit, close, modify, set_price, account_snapshot,
reconcile. The registry selects the adapter from config/broker/accounts.yaml
(`broker.default` account `type`: simulated | mt5 | mt4 | ctrader | fix).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from david_sling.core.errors import ExecutionError
from david_sling.core.schemas import (
    ExecutionReport,
    OrderIntent,
    PositionState,
    SymbolSpec,
)


class BrokerAdapter(ABC):
    """Uniform broker contract. Live adapters must raise SecurityError /
    ExecutionError on any transport or credential failure - never silently
    drop an order."""

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def submit(self, intent: OrderIntent) -> ExecutionReport: ...

    @abstractmethod
    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]: ...

    @abstractmethod
    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState: ...

    @abstractmethod
    def set_price(self, symbol: str, price: float) -> None: ...

    @abstractmethod
    def account_snapshot(self, floating_pnl: float) -> dict: ...

    @abstractmethod
    def reconcile(self) -> dict: ...


class BrokerRegistry:
    """Capability discovery: builds the configured adapter."""

    @staticmethod
    def create(account_cfg: dict, specs: dict[str, SymbolSpec]):
        from david_sling.broker.ctrader_adapter import CTraderAdapter
        from david_sling.broker.fix_adapter import FixAdapter
        from david_sling.broker.mt4_adapter import Mt4Adapter
        from david_sling.broker.mt5_adapter import Mt5Adapter
        from david_sling.broker.simulated import SimulatedBrokerAdapter

        kind = str(account_cfg.get("type", "simulated")).lower()
        balance = float(account_cfg.get("balance", 100_000.0))
        currency = str(account_cfg.get("currency", "USD"))
        leverage = float(account_cfg.get("leverage", 50.0))
        if kind == "simulated":
            return SimulatedBrokerAdapter(specs, balance=balance, currency=currency, leverage=leverage)
        if kind == "mt5":
            return Mt5Adapter(specs, account_cfg)
        if kind == "mt4":
            return Mt4Adapter(specs, account_cfg)
        if kind == "ctrader":
            return CTraderAdapter(specs, account_cfg)
        if kind == "fix":
            return FixAdapter(specs, account_cfg)
        raise ExecutionError(f"unknown broker adapter type: {kind}")
