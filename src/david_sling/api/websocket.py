"""api/websocket - real-time telemetry WebSocket endpoint manager."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    runtime = websocket.app.state.runtime
    queue = await runtime.telemetry.subscribe()
    try:
        # send an immediate snapshot so the UI renders instantly
        await websocket.send_text(json.dumps({"topic": "overview", **runtime.mission_control.overview()}, default=str))
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                await websocket.send_text(json.dumps(msg, default=str))
            except TimeoutError:
                await websocket.send_text(json.dumps({"topic": "ping", "ts": runtime.time.now().isoformat()}))
    except WebSocketDisconnect:
        pass
    finally:
        await runtime.telemetry.unsubscribe(queue)
