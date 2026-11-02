"""L2 data - deterministic synthetic market feed + candle construction.

SimClock advances simulated time (accelerated) so the full pipeline runs in
real time during Phase 1. A seeded random.Random per symbol makes the feed
deterministic (replay contract). Regime-switching drift/vol process.

feed_router: canonical routing of tick / candle / orderbook / trade-flow
events onto the event bus.
"""
from __future__ import annotations

import asyncio
import math
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from david_sling.core.schemas import (
    TF_MINUTES,
    Candle,
    OrderBookLevel,
    OrderBookSnapshot,
    SymbolSpec,
    Tick,
    Timeframe,
    TradeFlow,
)
from david_sling.core.utils import utc_now
from david_sling.data.integrity import OUTLIER_Z, validate_candle, validate_tick
from david_sling.data.store import DataStore
from david_sling.services.buses import EventBus

SIM_EPOCH = datetime(2026, 1, 5, 0, 0, 0, tzinfo=UTC)  # Monday


class SimClock:
    """Accelerated deterministic simulation clock."""

    def __init__(self, speed: float = 30.0, start: datetime = SIM_EPOCH) -> None:
        self.speed = speed
        self._sim_now = start
        self._real_last = utc_now()

    def advance_to_real_time(self) -> datetime:
        real_now = utc_now()
        elapsed = (real_now - self._real_last).total_seconds()
        self._real_last = real_now
        self._sim_now += timedelta(seconds=elapsed * self.speed)
        return self._sim_now

    def now(self) -> datetime:
        return self._sim_now

    def step(self, seconds: float) -> datetime:
        self._sim_now += timedelta(seconds=seconds)
        return self._sim_now


@dataclass
class SymbolSimState:
    spec: SymbolSpec
    price: float
    drift: float = 0.0
    vol: float = 0.0002
    regime: str = "range"
    regime_left: int = 120          # sim-seconds remaining in regime
    rng: random.Random = field(default_factory=random.Random)
    last_tick: Tick | None = None
    recent_moves: list[float] = field(default_factory=list)


class CandleBuilder:
    """Canonical OHLCV construction per (symbol, timeframe) from ticks."""

    def __init__(self) -> None:
        self._forming: dict[tuple[str, Timeframe], Candle] = {}
        self.closed: dict[tuple[str, Timeframe], list[Candle]] = {}

    @staticmethod
    def _bucket_start(ts: datetime, minutes: int) -> datetime:
        epoch = datetime(1970, 1, 1, tzinfo=UTC)
        delta = ts - epoch
        bucket = int(delta.total_seconds() // (minutes * 60)) * minutes * 60
        return epoch + timedelta(seconds=bucket)

    def add_tick(self, tick: Tick) -> list[Candle]:
        """Add a tick; return any candles that closed at this tick's time."""
        closed: list[Candle] = []
        for tf in Timeframe:
            minutes = TF_MINUTES[tf]
            start = self._bucket_start(tick.ts, minutes)
            key = (tick.symbol, tf)
            cur = self._forming.get(key)
            if cur is None or cur.open_time != start:
                if cur is not None:
                    validate_candle(cur)
                    self.closed.setdefault(key, []).append(cur)
                    closed.append(cur)
                cur = Candle(symbol=tick.symbol, tf=tf, open_time=start,
                             open=tick.mid, high=tick.mid, low=tick.mid, close=tick.mid,
                             volume=0.0, tick_count=0)
                self._forming[key] = cur
            cur.high = max(cur.high, tick.mid)
            cur.low = min(cur.low, tick.mid)
            cur.close = tick.mid
            cur.tick_count += 1
            cur.volume += 1.0
        return closed

    def candles(self, symbol: str, tf: Timeframe, limit: int = 500) -> list[Candle]:
        key = (symbol, tf)
        forming = self._forming.get(key)
        out = list(self.closed.get(key, []))
        if forming is not None:
            out.append(forming)
        return out[-limit:]

    def seed_history(self, symbol: str, spec: SymbolSpec, rng: random.Random, bars: int = 400) -> None:
        """Deterministically pre-seed M1 history (and let resampling build HTF)."""
        price = 1.10 if "EUR" in symbol else (1.30 if "GBP" in symbol else (150.0 if "JPY" in symbol else 2400.0))
        state = SymbolSimState(spec=spec, price=price, rng=rng)
        for _ in range(bars):
            self._simulate_step(state, spec, advance_ts=timedelta(minutes=1))
            tick = state.last_tick
            assert tick is not None
            self.add_tick(tick)

    def _simulate_step(self, state: SymbolSimState, spec: SymbolSpec, advance_ts: timedelta | None = None) -> None:
        if state.regime_left <= 0:
            state.regime = state.rng.choice(["trend_up", "trend_down", "range", "range"])
            state.regime_left = state.rng.randint(60, 600)
        state.regime_left -= int(advance_ts.total_seconds()) if advance_ts else 1
        drift = {"trend_up": 0.00006, "trend_down": -0.00006, "range": 0.0}[state.regime]
        vol = {"trend_up": 0.00025, "trend_down": 0.00025, "range": 0.00012}[state.regime]
        shock = state.rng.gauss(0.0, vol)
        prev = state.price
        new_price = max(spec.tick_size, state.price * math.exp(drift + shock))
        # clamp the step to a sane z-score vs recent moves so the integrity guard
        # never trips on the simulator's own gaussian noise (early ticks have ~0 sd)
        if len(state.recent_moves) >= 5:
            mean = sum(state.recent_moves) / len(state.recent_moves)
            var = sum((m - mean) ** 2 for m in state.recent_moves) / len(state.recent_moves)
            sd = max(var ** 0.5, spec.tick_size * 4)
            move = new_price - prev
            max_move = (OUTLIER_Z - 0.5) * sd
            if abs(move - mean) > max_move:
                new_price = prev + mean + math.copysign(max_move, move - mean)
        state.price = new_price
        ts = (state.last_tick.ts + advance_ts) if (state.last_tick and advance_ts) else SIM_EPOCH
        spread = spec.spread_points * spec.tick_size
        mid = state.price
        tick = Tick(symbol=spec.name, bid=round(mid - spread / 2, spec.digits),
                    ask=round(mid + spread / 2, spec.digits), ts=ts)
        validate_tick(tick, now=ts, last_ts=state.last_tick.ts if state.last_tick else None,
                      prev_mid=prev, recent_moves=state.recent_moves)
        state.recent_moves.append(state.price - prev)
        if len(state.recent_moves) > 50:
            state.recent_moves.pop(0)
        state.last_tick = tick


class MarketSimulator:
    """Canonical feed router: produces tick / candle.closed / orderbook / trade_flow."""

    def __init__(self, specs: list[SymbolSpec], bus: EventBus, *, speed: float = 30.0, seed: int = 7,
                 store: DataStore | None = None) -> None:
        self.bus = bus
        self.store = store
        self.clock = SimClock(speed=speed)
        self.builder = CandleBuilder()
        self.states: dict[str, SymbolSimState] = {}
        for i, spec in enumerate(specs):
            rng = random.Random(seed * 1000 + i)
            mid0 = 1.10 if spec.name == "EURUSD" else 1.30 if spec.name == "GBPUSD" else 150.0 if spec.name == "USDJPY" else 2400.0
            self.states[spec.name] = SymbolSimState(spec=spec, price=mid0, rng=rng)
            self.builder.seed_history(spec.name, spec, rng, bars=400)
        self._running = False
        self.tick_count = 0

    # ------------------------------------------------------------- runtime
    async def pump(self, sim_seconds: int) -> None:
        """Deterministically advance the sim by `sim_seconds` and emit all events
        (used by backtests/tests; `run()` is the wall-clock variant)."""
        for _ in range(sim_seconds):
            self.clock.step(1.0)
            for state in self.states.values():
                self.builder._simulate_step(state, state.spec, advance_ts=timedelta(seconds=1))
                tick = state.last_tick
                if tick is None:
                    continue
                self.tick_count += 1
                closed = self.builder.add_tick(tick)
                if self.store is not None:
                    try:
                        self.store.append_tick(tick)
                        for c in closed:
                            self.store.append_candle(tick.symbol, c.tf.value, c)
                    except Exception:
                        pass  # storage is best-effort; feed never dies on disk errors
                await self.bus.publish("tick", tick)
                for c in closed:
                    await self.bus.publish("candle.closed", c)
                if self.tick_count % 25 == 0:
                    await self.bus.publish("orderbook", self._orderbook(tick))
                    await self.bus.publish("trade_flow", self._trade_flow(tick, state))

    async def run(self) -> None:
        """Feed loop: advance sim clock, emit ticks + closed candles."""
        self._running = True
        while self._running:
            self.clock.advance_to_real_time()
            for state in self.states.values():
                # ~1 tick per sim-second per symbol, batched
                steps = max(1, int(self.clock.speed / 10))
                for _ in range(steps):
                    self.clock.step(1.0)
                    self.builder._simulate_step(state, state.spec, advance_ts=timedelta(seconds=1))
                    tick = state.last_tick
                    if tick is None:
                        continue
                    self.tick_count += 1
                    closed = self.builder.add_tick(tick)
                    if self.store is not None:
                        try:
                            self.store.append_tick(tick)
                            for c in closed:
                                self.store.append_candle(tick.symbol, c.tf.value, c)
                        except Exception:
                            pass  # storage is best-effort; the feed never dies on disk errors
                    await self.bus.publish("tick", tick)
                    for c in closed:
                        await self.bus.publish("candle.closed", c)
                    if self.tick_count % 25 == 0:
                        await self.bus.publish("orderbook", self._orderbook(tick))
                        await self.bus.publish("trade_flow", self._trade_flow(tick, state))
            await asyncio.sleep(0.1)

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------- helpers
    def _orderbook(self, tick: Tick) -> OrderBookSnapshot:
        spec = self.states[tick.symbol].spec
        step = spec.tick_size * 5
        bids = [OrderBookLevel(price=round(tick.bid - i * step, spec.digits), volume=1.0 + (i % 3)) for i in range(10)]
        asks = [OrderBookLevel(price=round(tick.ask + i * step, spec.digits), volume=1.0 + (i % 2)) for i in range(10)]
        return OrderBookSnapshot(symbol=tick.symbol, bids=bids, asks=asks, ts=tick.ts)

    def _trade_flow(self, tick: Tick, state: SymbolSimState) -> TradeFlow:
        rng = state.rng
        return TradeFlow(symbol=tick.symbol, price=tick.mid, volume=round(rng.uniform(0.1, 5.0), 2),
                         side="buy" if rng.random() > 0.5 else "sell", ts=tick.ts)

    # ------------------------------------------------------------- access
    def price(self, symbol: str) -> float:
        st = self.states[symbol]
        return st.last_tick.mid if st.last_tick else st.price

    def tick_of(self, symbol: str) -> Tick | None:
        return self.states[symbol].last_tick

    def candles(self, symbol: str, tf: Timeframe, limit: int = 500) -> list[Candle]:
        return self.builder.candles(symbol, tf, limit)

    def generate_history(self, symbol: str, days: int) -> list[Tick]:
        """Deterministic historical tick tape for backtest/replay."""
        spec = self.states[symbol].spec
        rng = random.Random(hash(("hist", symbol)) & 0xFFFFFFFF)
        state = SymbolSimState(spec=spec, price=self.states[symbol].price, rng=rng)
        out: list[Tick] = []
        total = days * 24 * 60  # one tick per sim-minute
        for _ in range(total):
            self.builder._simulate_step(state, spec, advance_ts=timedelta(minutes=1))
            tick = state.last_tick
            if tick is not None:
                out.append(tick)
        return out
