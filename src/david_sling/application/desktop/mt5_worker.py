"""L14 application/desktop/mt5_worker - MT5 execution worker thread.

Owns the live MT5 terminal lifecycle when the runtime runs on the MT5 broker
(mode=live, broker=Mt5Adapter): connect with retry/backoff, heartbeat
reconcile, and serializes every execution command onto this worker thread so
the GUI never blocks (low-latency order path, immediate thread execution for
PANIC / HALT / RESUME).

In sim mode (or when the MetaTrader5 package / terminal is unavailable) the
worker stays in SIMULATED provenance and simply executes facade commands on
the worker thread - the app never crashes on a missing terminal.

All terminal errors are caught and emitted as `error(str)` signals - orders
are never silently dropped.
"""
from __future__ import annotations

import asyncio
import inspect
import queue
import threading
import time
import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QThread, Signal


class Mt5Worker(QThread):
    """Background thread: MT5 link management + serialized command execution."""

    connected = Signal(bool, str)      # (ok, provenance/host info)
    error = Signal(str)                # human-readable error, never fatal
    result = Signal(str, object)       # (command tag, result dict)
    tick = Signal(object)              # heartbeat reconcile payload

    def __init__(self, facade, parent=None, loop: asyncio.AbstractEventLoop | None = None) -> None:
        super().__init__(parent)
        self.facade = facade
        self._loop = loop  # persistent runtime loop when provided (production)
        self._jobs: queue.Queue[tuple[str, Callable[[], Any]]] = queue.Queue()
        self._stop = threading.Event()
        self._broker = getattr(facade.rt, "broker", None)
        self._mt5_link = False
        self._provenance = "SIMULATED FEED"

    # ------------------------------------------------------------- API (GUI thread)
    def enqueue(self, tag: str, fn: Callable[[], Any]) -> None:
        """Queue a command for execution on the worker thread."""
        self._jobs.put((tag, fn))

    def request_stop(self) -> None:
        self._stop.set()

    @property
    def provenance(self) -> str:
        return self._provenance

    # ------------------------------------------------------------- thread loop
    def run(self) -> None:  # noqa: D401
        self._link_mt5()
        while not self._stop.is_set():
            try:
                tag, fn = self._jobs.get(timeout=0.25)
                try:
                    res = self._exec(fn)
                    self.result.emit(tag, res)
                except Exception as exc:  # bulletproof: report, never die
                    self.error.emit(f"{tag}: {type(exc).__name__}: {exc}")
                    self.result.emit(tag, {"ok": False, "error": str(exc)})
            except queue.Empty:
                pass
            if self._mt5_link and int(time.time()) % 5 == 0:
                time.sleep(0.9)  # crude 5s heartbeat slot
                try:
                    self.tick.emit(self._broker.reconcile())
                except Exception as exc:
                    self.error.emit(f"reconcile: {exc}")
                    self._mt5_link = False
                    self.connected.emit(False, "MT5 link lost - SIMULATED FEED")
        try:
            if self._mt5_link and hasattr(self._broker, "disconnect"):
                self._broker.disconnect()
        except Exception:
            pass

    def _exec(self, fn: Callable[[], Any]) -> Any:
        """Run a facade command with a live event loop (runtime internals use
        asyncio.get_running_loop()). On the persistent runtime loop when given,
        otherwise a fresh per-job loop (tests / sim fallback)."""
        async def runner():
            r = fn()
            if inspect.isawaitable(r):
                r = await r
            await asyncio.sleep(0.05)  # let fire-and-forget bus publishes flush
            return r
        if self._loop is not None and self._loop.is_running():
            return asyncio.run_coroutine_threadsafe(runner(), self._loop).result(timeout=30)
        return asyncio.run(runner())

    def _link_mt5(self) -> None:
        """Establish the live MT5 connection when the runtime uses Mt5Adapter."""
        broker = self._broker
        if broker is None or type(broker).__name__ != "Mt5Adapter":
            self._provenance = "SIMULATED FEED"
            self.connected.emit(True, self._provenance)
            return
        try:
            broker.connect()
            self._mt5_link = True
            rec = broker.reconcile()
            self._provenance = f"MT5 LIVE login={rec.get('login')}"
            self.connected.emit(True, self._provenance)
        except Exception as exc:
            self._mt5_link = False
            self._provenance = "SIMULATED FEED (MT5 unavailable)"
            self.error.emit(f"MT5 connect failed, falling back to sim: {exc}")
            self.connected.emit(False, self._provenance)

    # ------------------------------------------------------------- high-priority overrides
    def panic(self) -> None:
        """PANIC FLATTEN on the worker thread: close all + cancel pending (MT5)."""
        def job():
            res = self.facade.panic_flatten()
            cancelled = 0
            if type(self._broker).__name__ == "Mt5Adapter" and getattr(self._broker, "is_connected", False):
                try:
                    cancelled = self._broker.cancel_pending()
                except Exception as exc:
                    self.error.emit(f"cancel_pending: {exc}")
            res["pending_cancelled"] = cancelled
            return res
        self.enqueue("panic", job)

    def halt(self, reason: str) -> None:
        self.enqueue("halt", lambda: self.facade.halt_trading(reason))

    def resume(self) -> None:
        def job():
            if type(self._broker).__name__ == "Mt5Adapter" and not getattr(self._broker, "is_connected", False):
                self._link_mt5()  # re-verify MT5 connection before resuming
            return self.facade.resume_trading()
        self.enqueue("resume", job)


def format_error(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=4)}"
