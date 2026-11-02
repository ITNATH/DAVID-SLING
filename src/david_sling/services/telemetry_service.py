"""L1 services/telemetry_service - telemetry emission + websocket fan-out."""
from __future__ import annotations

import asyncio
from typing import Any

from david_sling.core.schemas import StrictModel


class TelemetryService:
    def __init__(self) -> None:
        self._queues: set[asyncio.Queue[dict[str, Any]]] = set()
        self._lock = asyncio.Lock()
        self.emitted: int = 0

    async def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=512)
        async with self._lock:
            self._queues.add(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue[dict[str, Any]]) -> None:
        async with self._lock:
            self._queues.discard(q)

    async def emit(self, topic: str, payload: dict[str, Any]) -> None:
        self.emitted += 1
        msg = {"topic": topic, **payload}
        async with self._lock:
            queues = list(self._queues)
        for q in queues:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                pass  # slow consumer: drop oldest
                try:
                    q.get_nowait()
                    q.put_nowait(msg)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass

    @property
    def subscribers(self) -> int:
        return len(self._queues)


def model_dump(model: StrictModel | Any) -> dict[str, Any]:
    if isinstance(model, StrictModel):
        return model.model_dump(mode="json")
    return dict(model)
