"""L2 data/store - append-only on-disk market data (ticks, OHLCV, orderbook, news).

Blueprint data tree: data/{ticks,ohlcv,orderbook,news,synthetic}/. Writes are
best-effort JSONL appends; a storage failure never kills the feed (isolated +
alerted by the caller's guard).
"""
from __future__ import annotations

import json
from pathlib import Path

from david_sling.core.schemas import Candle, Tick


class DataStore:
    def __init__(self, root: str | Path = "data") -> None:
        self.root = Path(root)
        for sub in ("ticks", "ohlcv", "orderbook", "news", "synthetic"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def _append(self, sub: str, name: str, record: dict) -> None:
        path = self.root / sub / f"{name}.jsonl"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")

    def append_tick(self, tick: Tick) -> None:
        self._append("ticks", tick.symbol, tick.model_dump(mode="json"))

    def append_candle(self, symbol: str, tf: str, candle: Candle) -> None:
        self._append("ohlcv", f"{symbol}_{tf}", candle.model_dump(mode="json"))

    def append_orderbook(self, symbol: str, snapshot: dict) -> None:
        self._append("orderbook", symbol, snapshot)

    def append_news(self, item: dict) -> None:
        self._append("news", "feed", item)

    def read_ticks(self, symbol: str, limit: int = 1000) -> list[dict]:
        path = self.root / "ticks" / f"{symbol}.jsonl"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-limit:]]

    def read_candles(self, symbol: str, tf: str, limit: int = 500) -> list[dict]:
        path = self.root / "ohlcv" / f"{symbol}_{tf}.jsonl"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-limit:]]
