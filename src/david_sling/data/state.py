"""L2 data/market_reconstruction - chart morphology reconstruction.

Maintains current / previous / forming state per symbol and a deterministic
reconstruction fingerprint (hash of recent closes per timeframe).
"""
from __future__ import annotations

from dataclasses import dataclass

from david_sling.core.schemas import Candle, Timeframe
from david_sling.core.utils import canonical_json, sha256_hex


@dataclass
class SymbolMarketState:
    symbol: str
    last_price: float = 0.0
    prev_price: float = 0.0
    last_candle: Candle | None = None
    forming_candle: Candle | None = None

    def update(self, price: float, candle: Candle | None) -> None:
        self.prev_price = self.last_price
        self.last_price = price
        if candle is not None:
            self.last_candle = candle


class MarketReconstruction:
    def __init__(self) -> None:
        self._states: dict[str, SymbolMarketState] = {}

    def state(self, symbol: str) -> SymbolMarketState:
        return self._states.setdefault(symbol, SymbolMarketState(symbol=symbol))

    def update_tick(self, symbol: str, price: float) -> SymbolMarketState:
        st = self.state(symbol)
        st.update(price, None)
        return st

    def update_candle(self, candle: Candle) -> SymbolMarketState:
        st = self.state(candle.symbol)
        st.update(candle.close, candle)
        st.forming_candle = candle
        return st

    def fingerprint(self, candles_by_tf: dict[Timeframe, list[Candle]], symbol: str) -> str:
        payload = {
            "symbol": symbol,
            "tfs": {tf.value: [round(c.close, 8) for c in cs[-20:]] for tf, cs in candles_by_tf.items()},
        }
        return sha256_hex(canonical_json(payload))
