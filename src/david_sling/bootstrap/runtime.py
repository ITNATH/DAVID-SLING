"""L1 bootstrap/runtime - the assembled David OS runtime + decision pipeline.

DecisionPipeline (tick -> signal -> order):
  awareness -> intelligence features -> regime -> scenario pool (S1-S31 /
  terminal) -> hypothesis -> grammar -> 9-layer fusion -> three-core validation
  -> 52-strategy vault -> router -> peer engine -> precision tier ->
  TechnicalSignalTicket -> L10 boundary -> L11 risk veto -> sizing -> broker
"""
from __future__ import annotations

import asyncio
import os
import random
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING

from david_sling.alerts.engine import AlertEngine
from david_sling.awareness.engine import AwarenessEngine
from david_sling.broker.simulated import SimulatedBrokerAdapter
from david_sling.configuration.configuration_engine import ConfigurationEngine
from david_sling.core.schemas import SignalStatus, Timeframe
from david_sling.core.utils import utc_now
from david_sling.data.market import MarketSimulator
from david_sling.data.state import MarketReconstruction
from david_sling.engines.supervisor import EngineSupervisor
from david_sling.evidence_ledger.ledger import EvidenceLedger
from david_sling.execution_boundary.firewall import ExecutionBoundary
from david_sling.fusion.brain import NineLayerFusionBrain
from david_sling.grammar.engine import GrammarEngine
from david_sling.hypothesis.engine import HypothesisEngine
from david_sling.intelligence.engine import IntelligenceEngine
from david_sling.journal.engine import JournalEngine
from david_sling.mission_control.ops import MultiTradeOperationsEngine
from david_sling.mission_control.pnl import CrossPairPnLCalculator
from david_sling.mission_control.server import MissionControl
from david_sling.monitoring_learning.engine import MonitoringEngine
from david_sling.order_management.manager import OrderManager
from david_sling.parameter.lifecycle import ParameterLifecycleManager
from david_sling.parameter.registry import ParameterRegistry
from david_sling.portfolio.exposure import PortfolioExposure

if TYPE_CHECKING:
    from david_sling.core.schemas import OrderIntent
    from david_sling.order_management.manager import ManagedOrder
    from david_sling.risk.gate import RiskDecision
from david_sling.position_management.tms import TradeManagementLifecycle
from david_sling.precision.engine import PrecisionEngine
from david_sling.regime.classifier import RegimeClassifier
from david_sling.rescan.engine import RescanEngine
from david_sling.risk.gate import RiskGate
from david_sling.routing.router import Router
from david_sling.scenario_pool.engine import ScenarioPoolEngine
from david_sling.services.buses import CommandBus, EventBus
from david_sling.services.symbol_registry import SymbolRegistry
from david_sling.services.telemetry_service import TelemetryService
from david_sling.services.time_service import TimeService
from david_sling.signal.engine import SignalEngine
from david_sling.sizing.engine import SizingEngine
from david_sling.strategies.vault import STRATEGY_VAULT
from david_sling.validation.engine import ValidationEngine

CORE_PARAMETERS = (
    "atr.m1", "atr.h1", "ema20.m1", "ema50.m1", "rsi.m1", "macd.hist.m1",
    "bb.pos.m1", "trend.h1", "trend.h4", "bos.h1", "sweep.m5", "fvg.m5",
    "displacement.m1", "volume.z.m1", "delta.m1", "session.epoch", "regime",
)


class Runtime:
    def __init__(self, mode: str = "sim") -> None:
        self.mode = mode
        self.config_engine = ConfigurationEngine()
        self.cfg = self.config_engine.load()
        self.bus = EventBus()
        self.commands = CommandBus(self.bus)
        self.time = TimeService()
        self.telemetry = TelemetryService()
        self.symbols = SymbolRegistry(self._load_symbols())
        ledger_path = os.environ.get("DAVID_SLING_LEDGER_PATH") or str(self.cfg.get("environment.ledger_path", "storage/audit/evidence_ledger.jsonl"))
        self.ledger = EvidenceLedger(ledger_path)
        self.journal = JournalEngine(self.ledger)
        self.alerts = AlertEngine(self.bus, self.telemetry)
        self.monitoring = MonitoringEngine()
        self.params_registry = ParameterRegistry()
        for p in CORE_PARAMETERS:
            self.params_registry.register(p, domain="intelligence", source="intelligence_engine")
        self.params = ParameterLifecycleManager(self.params_registry)
        self.reconstruction = MarketReconstruction()
        self.sim: MarketSimulator | None = None
        self.awareness = AwarenessEngine()
        self.intelligence = IntelligenceEngine()
        self.regime = RegimeClassifier()
        self.scenario_engine = ScenarioPoolEngine()
        self.hypothesis = HypothesisEngine()
        self.grammar = GrammarEngine()
        self.fusion = NineLayerFusionBrain(
            conflict_threshold=float(self.cfg.get("fusion.conflict_threshold", 0.6)),
            convergence_threshold=float(self.cfg.get("fusion.convergence_threshold", 0.55)))
        self.validation = ValidationEngine(threshold=float(self.cfg.get("confluence_weights.gate_threshold", 0.55)))
        self.vault = STRATEGY_VAULT
        self.supervisor = EngineSupervisor(self.cfg.get("engines", {}))
        matrix = {k: v for k, v in (self.cfg.get("routing.scenario_engine_matrix", {}) or {}).items()}
        self.router = Router(self.supervisor, matrix, min_score=float(self.cfg.get("routing.min_route_score", 0.45)))
        self.precision = PrecisionEngine(self.cfg.get("precision_thresholds", {}),
                                         min_routed=float(self.cfg.get("precision_thresholds.min_routed_score", 0.55)))
        self.signal_engine = SignalEngine()
        self.rescan = RescanEngine()
        self.boundary = ExecutionBoundary()
        self.risk = RiskGate(self.cfg.get("risk", {}))
        self.sizing = SizingEngine(self.cfg.get("sizing", {}))
        self.portfolio = PortfolioExposure(
            self.cfg.get("portfolio.correlation_matrix", {}),
            per_currency_pct=float(self.cfg.get("risk.exposure_policy.per_currency_exposure_limit_pct", 25.0)),
            total_pct=float(self.cfg.get("risk.exposure_policy.total_exposure_limit_pct", 60.0)))
        balance = float(os.environ.get("DAVID_SLING_ACCOUNT_BALANCE", self.cfg.get("broker.accounts.simulated.balance", 100000.0)))
        self.broker = SimulatedBrokerAdapter({s.name: s for s in self.symbols.all()}, balance=balance)
        self.risk.start_day(balance)
        self.order_manager = OrderManager(self.broker)
        self.tms = TradeManagementLifecycle(self.broker, {s.name: s for s in self.symbols.all()})
        self.pnl_calculator = CrossPairPnLCalculator(self.broker)
        self.ops = MultiTradeOperationsEngine(self.boundary, self.risk, self.sizing, self.portfolio,
                                              self._submit_order, {s.name: s for s in self.symbols.all()},
                                              self._price)
        self.mission_control = MissionControl(self)
        self.pipeline = DecisionPipeline(self)
        from david_sling.application.facade import ServiceFacade

        self.facade = ServiceFacade(self)
        self.deltas: dict[str, deque[float]] = {s: deque(maxlen=200) for s in self.symbols.symbols()}
        self.news_active = False
        self._news_until: datetime | None = None
        self._tasks: list[asyncio.Task] = []
        self._running = False

    # ------------------------------------------------------------ helpers
    def _load_symbols(self) -> dict:
        from david_sling.core.schemas import SymbolSpec

        raw = self.cfg.get("symbols", {})
        return {name: SymbolSpec(name=name, **spec) for name, spec in raw.items()}

    def _price(self, symbol: str) -> float:
        if self.sim is not None:
            return self.sim.price(symbol)
        return self.broker.price(symbol)

    def clock_now(self) -> datetime:
        return self.sim.clock.now() if self.sim else utc_now()

    def atr_now(self, symbol: str) -> float:
        fs = self.intelligence.last_features.get(symbol)
        return fs.atr_m1 if fs else 0.0

    def atr_avg(self, symbol: str) -> float:
        fs = self.intelligence.last_features.get(symbol)
        return fs.atr_h1 if fs else 0.0

    def spread_now(self, symbol: str) -> float:
        tick = self.sim.tick_of(symbol) if self.sim else None
        if tick:
            return (tick.ask - tick.bid) / self.symbols.get(symbol).tick_size
        return self.symbols.get(symbol).spread_points

    @property
    def spread_avg(self) -> float:
        return 2.5

    def account_snapshot(self) -> dict:
        rows = self.pnl_calculator.compute(self.broker.account.positions)
        floating = self.pnl_calculator.total_net(rows)
        snap = self.broker.account_snapshot(floating)
        return snap

    def _submit_order(self, intent: OrderIntent, decision: RiskDecision) -> ManagedOrder:
        order = self.order_manager.submit(intent, risk_approved=decision.approved,
                                          risk_reasons=decision.reasons,
                                          adjusted_volume=decision.adjusted_volume or None)
        if order.report is not None:
            asyncio.get_event_loop().create_task(self.bus.publish("order.filled", {
                "symbol": intent.symbol, "side": intent.side.value, "volume": order.intent.volume,
                "fill_price": order.report.fill_price}))
            self.journal.execution(intent.model_dump(mode="json"),
                                   order.report.__dict__ if order.report else None,
                                   decision.to_dict())
            self.ledger.append("order.filled", {"intent": intent.intent_id, "fill": order.report.fill_price})
        else:
            asyncio.get_event_loop().create_task(self.bus.publish("risk.veto", {"reasons": decision.reasons}))
        return order

    # ------------------------------------------------------------- loops
    def start_feed(self) -> None:
        """Create the market feed (no background tasks) - used by backtests/tests."""
        if self.sim is None:
            self.sim = MarketSimulator(self.symbols.all(), self.bus,
                                       speed=float(self.cfg.get("system.feed_hz", 10)) * 3)
            self.bus.subscribe("trade_flow", self._on_trade_flow)

    async def start(self, feed: bool = True, loops: bool = True) -> None:
        self._running = True
        if feed:
            self.start_feed()
            if loops:
                sim = self.sim
                assert sim is not None
                self._tasks.append(asyncio.create_task(sim.run()))
        if loops:
            self._tasks.append(asyncio.create_task(self._tms_loop()))
            self._tasks.append(asyncio.create_task(self._telemetry_loop()))
            self._tasks.append(asyncio.create_task(self._pipeline_loop()))
            self._tasks.append(asyncio.create_task(self._news_loop()))

    async def stop(self) -> None:
        self._running = False
        if self.sim:
            self.sim.stop()
        for t in self._tasks:
            t.cancel()

    def _on_trade_flow(self, tf) -> None:
        d = self.deltas.setdefault(tf.symbol, deque(maxlen=200))
        d.append(tf.volume if tf.side == "buy" else -tf.volume)

    async def _tms_loop(self) -> None:
        while self._running:
            if self.sim is not None:
                for symbol in self.symbols.symbols():
                    tick = self.sim.tick_of(symbol)
                    if tick is None:
                        continue
                    self.broker.set_price(symbol, tick.mid)
                    self.reconstruction.update_tick(symbol, tick.mid)
                    atr_now = self.atr_now(symbol)
                    atr_avg = self.atr_avg(symbol) or atr_now
                    res = self.tms.on_tick(symbol, tick.bid, tick.ask, atr_now, atr_avg)
                    for trade in res.closed:
                        self.journal.exit(trade.__dict__)
                        self.ledger.append("position.closed", trade.__dict__)
                        asyncio.get_event_loop().create_task(self.bus.publish("position.closed", trade.__dict__))
                        asyncio.get_event_loop().create_task(self.alerts.emit(
                            __import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.INFO
                            if trade.pnl >= 0 else
                            __import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.WARNING,
                            f"CLOSED {trade.symbol} pnl={trade.pnl:.2f} reason={trade.reason}"))
                        self.monitoring.record_outcome(None, trade)
                        self.rescan.rescan(symbol, f"post_exit:{trade.reason}")
            await asyncio.sleep(0.25)

    async def _telemetry_loop(self) -> None:
        while self._running:
            try:
                snap = self.mission_control.overview()
                await self.telemetry.emit("overview", snap)
            except Exception as exc:  # telemetry must never kill the loop
                await self.alerts.emit(__import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.WARNING,
                                       f"telemetry error: {exc}")
            await asyncio.sleep(0.5)

    async def _pipeline_loop(self) -> None:
        """Run the full decision pipeline on every M1 candle close."""
        seen: set[tuple[str, datetime]] = set()
        while self._running:
            if self.sim is not None:
                for symbol in self.symbols.symbols():
                    m1 = self.sim.candles(symbol, Timeframe.M1, limit=3)
                    if not m1:
                        continue
                    last = m1[-1]
                    if last.tick_count == 0 and last.open_time in seen:
                        continue
                    key = (symbol, last.open_time)
                    if key in seen and last.close == m1[-2].close if len(m1) > 1 else False:
                        continue
                    if key in seen:
                        continue
                    seen.add(key)
                    if len(seen) > 4096:
                        seen.clear()
                    try:
                        await self.pipeline.run_symbol(symbol)
                    except Exception as exc:
                        await self.alerts.emit(__import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.WARNING,
                                               f"pipeline error {symbol}: {exc}")
            await asyncio.sleep(0.2)

    async def _news_loop(self) -> None:
        rng = random.Random(42)
        while self._running:
            await asyncio.sleep(5)
            now = self.clock_now()
            if self._news_until and now > self._news_until:
                self.news_active = False
                self._news_until = None
                await self.alerts.emit(__import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.INFO, "news blackout ended")
            if not self.news_active and rng.random() < 0.02:
                from datetime import timedelta
                self.news_active = True
                self._news_until = now + timedelta(minutes=30)
                await self.alerts.emit(__import__("david_sling.core.schemas", fromlist=["AlertLevel"]).AlertLevel.CRITICAL,
                                       "HIGH-IMPACT NEWS BLACKOUT ACTIVE (30 sim-min)")

    # ------------------------------------------------------------- status
    def status_summary(self) -> str:
        return (f"mode={self.mode} symbols={self.symbols.symbols()} "
                f"ledger_entries={len(self.ledger)} chain_ok={self.ledger.verify_chain()} "
                f"engines={list(self.supervisor.profiles)} strategies={len(self.vault.all())}")

    def scan_report(self) -> str:
        lines = ["DAVID SLING - initial scan report (bot-on / pre-market):"]
        for symbol in self.symbols.symbols():
            fs = self.pipeline.features_only(symbol)
            sc = self.scenario_engine.classify(fs) if fs else None
            lines.append(f"  {symbol}: price={self._price(symbol):.5f} scenario={sc.scenario.value if sc else 'UNKNOWN'} "
                         f"atr_m1={fs.atr_m1:.6f}" if fs else f"  {symbol}: insufficient data -> UNKNOWN/WAIT")
        return "\n".join(lines)


class DecisionPipeline:
    """tick/candle -> TechnicalSignalTicket -> L10 boundary -> L11 risk -> L12 broker."""

    def __init__(self, rt: Runtime) -> None:
        self.rt = rt

    def candles_by_tf(self, symbol: str) -> dict:
        return {tf: self.rt.sim.candles(symbol, tf, limit=300) for tf in Timeframe} if self.rt.sim else {}

    def features_only(self, symbol: str):
        rt = self.rt
        if rt.sim is None:
            return None
        tick = rt.sim.tick_of(symbol)
        if tick is None:
            return None
        from david_sling.core.session_epoch_manager import primary_phase
        cb = self.candles_by_tf(symbol)
        fs = rt.intelligence.analyze(
            symbol, tick.ts, tick.mid, rt.spread_now(symbol), primary_phase(tick.ts), cb,
            deltas=list(rt.deltas.get(symbol, [])), news_repricing=rt.news_active)
        # parameter lifecycle: register features as tracked parameters (zero silent drops)
        from david_sling.core.contracts import ALL_STAGES

        for name, value in (("atr.m1", fs.atr_m1), ("rsi.m1", fs.rsi_m1), ("trend.h1", fs.trend_h1),
                            ("session.epoch", fs.session), ("volume.z.m1", fs.volume_z_m1)):
            if rt.params_registry.is_registered(name):
                rt.params.ingest(name, value, symbol=symbol, source="intelligence_engine")
                for stage in list(ALL_STAGES)[1:]:
                    rt.params.advance(name, stage)
        return fs

    async def run_symbol(self, symbol: str) -> dict | None:
        rt = self.rt
        fs = self.features_only(symbol)
        if fs is None:
            return None
        regime = rt.regime.classify(fs)
        rt.awareness.update(fs, regime, rt.spread_now(symbol))
        scenario = rt.scenario_engine.classify(fs)
        hypothesis = rt.hypothesis.build(fs, scenario)
        grammar = rt.grammar.validate(fs, scenario)
        assert hypothesis.state is not None and grammar.valid is not None  # pipeline invariant
        fusion = rt.fusion.fuse(fs, self.candles_by_tf(symbol))
        validation = rt.validation.evaluate(fs, scenario, fusion)
        rt.params.assert_no_silent_drops()
        ev = rt.ledger.append("decision.context", {
            "symbol": symbol, "scenario": scenario.scenario.value, "regime": regime.regime,
            "fusion_direction": fusion.direction, "convergence": fusion.convergence,
            "validation": validation.model_dump(mode="json"),
        })
        candidates = rt.vault.evaluate(fs) if validation.passed else []
        signal = None
        for cand in candidates[:5]:
            route, engine_decision = rt.router.route(scenario, cand, validation, fusion)
            if route.engine == "NO_ROUTE" or engine_decision is None:
                continue
            precision = rt.precision.grade(fs, validation, fusion)
            if not rt.precision.routable(precision):
                continue
            ticket = rt.signal_engine.build(symbol, scenario, cand, route, engine_decision, precision,
                                            evidence_ids=[ev.evidence_id])
            rt.journal.signal(ticket.model_dump(mode="json"))
            await rt.bus.publish("signal.routed", ticket.model_dump(mode="json"))
            # L10 boundary -> L11 risk -> sizing -> L12 broker
            spec = rt.symbols.get(symbol)
            sl_dist = abs(ticket.entry_zone[0] - ticket.stop_loss)
            risk_amount = rt.risk.per_trade_risk_amount(rt.account_snapshot()["equity"], sl_dist, spec.tick_value)
            lot = rt.sizing.lots_for_risk(spec, risk_amount, sl_dist, requested_lot=0.01)
            if lot <= 0:
                lot = spec.min_lot
            intent = rt.boundary.to_order_intent(ticket, volume=lot, caller="signal")
            acct = rt.account_snapshot()
            positions = list(rt.broker.account.positions.values())
            exposure = rt.portfolio.net_exposure(positions, {s.name: s for s in rt.symbols.all()})
            decision = rt.risk.evaluate(intent, account=acct, open_positions=[p.model_dump() for p in positions],
                                        symbol_exposure=exposure, atr_now=fs.atr_m1, atr_avg=fs.atr_h1,
                                        spread_now=rt.spread_now(symbol), spread_avg=rt.spread_avg,
                                        news_active=rt.news_active)
            if not decision.approved:
                rt.signal_engine.set_status(ticket.signal_id, SignalStatus.VETOED)
                await rt.bus.publish("risk.veto", {"signal": ticket.signal_id, "reasons": list(decision.reasons)})
                rt.ledger.append("risk.veto", {"signal": ticket.signal_id, "reasons": list(decision.reasons)})
                continue
            order = rt._submit_order(intent, decision)
            if order.report is not None:
                rt.signal_engine.set_status(ticket.signal_id, SignalStatus.FILLED)
                rt.tms.risk_amounts[order.report.position_id] = risk_amount
                rt.ledger.append("signal.filled", {"signal": ticket.signal_id, "position": order.report.position_id})
            signal = ticket
            break
        return {"symbol": symbol, "scenario": scenario.scenario.value, "regime": regime.regime,
                "validation": validation.model_dump(mode="json"), "fusion": fusion.model_dump(mode="json"),
                "candidates": len(candidates), "signal": signal.signal_id if signal else None}
