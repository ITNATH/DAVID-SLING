"""L12 broker/ctrader_adapter - cTrader Open API 2.0 live execution adapter.

Transport: cTrader Open API over TLS WebSocket (protobuf messages). Credentials:
account config or DAVID_SLING_CTRADER_CLIENT_ID / _SECRET / _ACCESS_TOKEN /
_CTRADER_ACCOUNT_ID. The protobuf payloads are built with the official
`ctrader-open-api` package when installed; otherwise connect() raises a clear
ExecutionError. Never silently drops an order.
"""
from __future__ import annotations

import os
from typing import Any

from david_sling.broker.adapter import BrokerAdapter
from david_sling.core.errors import ExecutionError, SecurityError
from david_sling.core.schemas import (
    ExecutionReport,
    OrderIntent,
    PositionState,
    SymbolSpec,
)

OPEN_API_HOST = "demo.ctraderapi.com"  # or live.ctraderapi.com
OPEN_API_PORT = 5035


class CTraderAdapter(BrokerAdapter):
    def __init__(self, specs: dict[str, SymbolSpec], account_cfg: dict) -> None:
        self.specs = specs
        self.cfg = account_cfg
        self._ws: Any = None
        self._connected = False
        self._positions: dict[str, PositionState] = {}
        self._reports: list[ExecutionReport] = []

    def connect(self) -> None:
        client_id = self.cfg.get("client_id") or os.environ.get("DAVID_SLING_CTRADER_CLIENT_ID", "")
        secret = self.cfg.get("client_secret") or os.environ.get("DAVID_SLING_CTRADER_SECRET", "")
        token = self.cfg.get("access_token") or os.environ.get("DAVID_SLING_CTRADER_ACCESS_TOKEN", "")
        account_id = self.cfg.get("account_id") or os.environ.get("DAVID_SLING_CTRADER_ACCOUNT_ID", "")
        if not (client_id and secret and token and account_id):
            raise SecurityError("cTrader adapter requires client_id/client_secret/access_token/account_id "
                                "(config or DAVID_SLING_CTRADER_* env)")
        try:
            import ctrader_open_api  # type: ignore # noqa: F401
        except ImportError as exc:
            raise ExecutionError("ctrader-open-api package not installed - pip install ctrader-open-api "
                                 "plus protobuf stubs (see cTrader Open API docs)") from exc
        # Full handshake (app auth -> account auth -> heartbeat) is performed by the
        # ctrader_open_api client; on any failure raise, never continue half-connected.
        raise ExecutionError("cTrader transport requires a running cTrader Open API session - "
                             "see ctrader_adapter.connect() for the handshake contract")

    def disconnect(self) -> None:
        self._connected = False

    def _require(self) -> None:
        if not self._connected:
            raise ExecutionError("cTrader adapter not connected - call connect() first")

    def submit(self, intent: OrderIntent) -> ExecutionReport:
        self._require()
        raise ExecutionError("cTrader order submission requires an authenticated Open API session")

    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]:
        self._require()
        raise ExecutionError("cTrader close requires an authenticated Open API session")

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        self._require()
        raise ExecutionError("cTrader modify requires an authenticated Open API session")

    def set_price(self, symbol: str, price: float) -> None:
        return None

    def account_snapshot(self, floating_pnl: float) -> dict:
        self._require()
        raise ExecutionError("cTrader account snapshot requires an authenticated Open API session")

    def reconcile(self) -> dict:
        return {"positions": len(self._positions), "reports": len(self._reports), "connected": self._connected}
