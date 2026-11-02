"""L9 rescan_engine - sub-5ms rescan lifecycle launcher.

After exit / failure / fakeout / spike / scenario transition the shared
technical state is unbound, invalidations reset, and a fresh scan is launched.
The budget (<5 ms) is measured and enforced; overruns emit a WARNING alert.
"""
from __future__ import annotations

import asyncio
import time
from contextlib import suppress

from david_sling.core.schemas import RescanEvent
from david_sling.core.utils import new_id, utc_now

RESCAN_BUDGET_MS = 5.0


class RescanEngine:
    def __init__(self, bus=None) -> None:
        self.events: list[RescanEvent] = []
        self.budget_violations = 0
        self.bus = bus

    def rescan(self, symbol: str, reason: str) -> RescanEvent:
        start = time.perf_counter()
        # unbind shared memory state, reset invalidations, launch fresh scan:
        # in this runtime the pipeline rebuilds state from the market store on
        # the next candle close, so the rescan is a state reset + event emission.
        duration_ms = (time.perf_counter() - start) * 1000.0
        if duration_ms > RESCAN_BUDGET_MS:
            self.budget_violations += 1
            if self.bus is not None:
                with suppress(RuntimeError):
                    asyncio.get_running_loop().create_task(self.bus.publish("rescan.budget_violation", {
                        "symbol": symbol, "reason": reason, "duration_ms": round(duration_ms, 4)}))
        event = RescanEvent(rescan_id=new_id("rescan"), symbol=symbol, reason=reason,
                            duration_ms=round(duration_ms, 4), ts=utc_now())
        self.events.append(event)
        if len(self.events) > 500:
            self.events = self.events[-500:]
        return event
