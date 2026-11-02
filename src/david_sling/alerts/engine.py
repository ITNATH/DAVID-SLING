"""L13 alert_engine - alert orchestration with rate limiting & dispatch audit.

Channels: websocket (live UI), mission_control, telegram, email, whatsapp,
webhook. External channels are delivered by the alert-gateway service; here we
render, throttle, audit and fan out to the telemetry bus.
"""
from __future__ import annotations

import asyncio
import time
from collections import deque

from david_sling.core.schemas import AlertEvent, AlertLevel
from david_sling.core.utils import new_id, utc_now
from david_sling.services.buses import EventBus
from david_sling.services.telemetry_service import TelemetryService


class AlertEngine:
    def __init__(self, bus: EventBus, telemetry: TelemetryService, *, throttle_per_minute: int = 30,
                 channels: dict | None = None) -> None:
        self.bus = bus
        self.telemetry = telemetry
        self.throttle_per_minute = throttle_per_minute
        self.channels: dict = channels or {}
        self.outbox: list[dict] = []  # external deliveries awaiting/failed transport
        self.alerts: list[AlertEvent] = []
        self._sent_times: deque[float] = deque()
        self._lock = asyncio.Lock()
        bus.subscribe("signal.routed", self._on_signal)
        bus.subscribe("order.filled", self._on_order)
        bus.subscribe("risk.veto", self._on_risk)
        bus.subscribe("position.closed", self._on_close)
        bus.subscribe("rescan", self._on_rescan)

    async def emit(self, level: AlertLevel, message: str, *, channel: str = "mission_control") -> AlertEvent:
        now = time.time()
        async with self._lock:
            while self._sent_times and now - self._sent_times[0] > 60:
                self._sent_times.popleft()
            throttled = len(self._sent_times) >= self.throttle_per_minute
            self._sent_times.append(now)
        event = AlertEvent(alert_id=new_id("alr"), level=level, channel=channel,
                           message=message, ts=utc_now())
        self.alerts.append(event)
        if len(self.alerts) > 500:
            self.alerts = self.alerts[-500:]
        if not throttled:
            await self.telemetry.emit("alert", event.model_dump(mode="json"))
        await self.bus.publish("alert.dispatched", event.model_dump(mode="json"))
        await self._deliver_external(event)
        return event

    async def _deliver_external(self, event) -> None:
        """Alert gateway: routes to enabled external channels from
        config/alerts/alert_channels.yaml. Transport failures are isolated and
        recorded in the outbox - they never break the alert path."""
        import os

        ch = self.channels.get(event.channel)
        if not ch or not ch.get("enabled"):
            return
        payload = {"alert_id": event.alert_id, "level": event.level.value, "message": event.message,
                   "ts": event.ts.isoformat()}
        try:
            if event.channel == "webhook":
                url = os.environ.get("DAVID_SLING_WEBHOOK_URL")
                if url:
                    import httpx

                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(url, json=payload)
            elif event.channel == "telegram":
                token = os.environ.get("DAVID_SLING_TELEGRAM_TOKEN")
                chat = os.environ.get("DAVID_SLING_TELEGRAM_CHAT_ID")
                if token and chat:
                    import httpx

                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                          json={"chat_id": chat, "text": event.message})
            else:  # email / whatsapp: queued in outbox for the ops mailer
                self.outbox.append({"channel": event.channel, **payload})
        except Exception as exc:
            self.outbox.append({"channel": event.channel, "error": str(exc), **payload})
            await self.bus.publish("alert.delivery_failed", {"channel": event.channel, "error": str(exc)})

    # ------------------------------------------------------- event handlers
    async def _on_signal(self, ticket: dict) -> None:
        await self.emit(AlertLevel.INFO,
                        f"SIGNAL {ticket['signal_id']} {ticket['symbol']} {ticket['direction']} "
                        f"via Engine {ticket['engine']} strategy {ticket['strategy_id']} "
                        f"tier {ticket['precision']['tier']}")

    async def _on_order(self, payload: dict) -> None:
        await self.emit(AlertLevel.INFO,
                        f"FILLED {payload.get('symbol')} {payload.get('side')} {payload.get('volume')} "
                        f"@ {payload.get('fill_price')}")

    async def _on_risk(self, payload: dict) -> None:
        await self.emit(AlertLevel.WARNING, f"RISK VETO: {payload.get('reasons')}")

    async def _on_close(self, payload: dict) -> None:
        pnl = payload.get("pnl", 0.0)
        level = AlertLevel.INFO if pnl >= 0 else AlertLevel.WARNING
        await self.emit(level, f"CLOSED {payload.get('symbol')} pnl={pnl:.2f} reason={payload.get('reason')}")

    async def _on_rescan(self, event: dict) -> None:
        await self.emit(AlertLevel.INFO, f"RESCAN {event.get('symbol')} ({event.get('reason')}) {event.get('duration_ms')}ms")

    def recent(self, limit: int = 50) -> list[AlertEvent]:
        return self.alerts[-limit:]
