"""L1 services/cache_service - low-latency in-process cache."""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any


class CacheService:
    def __init__(self, max_size: int = 4096) -> None:
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._max = max_size

    def get(self, key: str, ttl_s: float | None = None) -> Any | None:
        item = self._store.get(key)
        if item is None:
            return None
        ts, value = item
        if ttl_s is not None and time.time() - ts > ttl_s:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)
        self._store.move_to_end(key)
        while len(self._store) > self._max:
            self._store.popitem(last=False)
