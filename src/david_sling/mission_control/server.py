"""mission_control/mission_control_server - high-speed telemetry aggregator.

Builds the Global Overview snapshot consumed by the API, WebSocket stream and
(desktop, Phase 2) GUI: account telemetry, 15-domain health matrix, awareness,
scenario, fusion, engines, signals, positions, cross-pair PnL, alerts, ledger.
"""
from __future__ import annotations

from typing import Any

from david_sling.core.schemas import Timeframe
from david_sling.core.session_epoch_manager import epoch_at, primary_phase
from david_sling.core.utils import utc_now

DOMAIN_HEALTH: list[tuple[str, int]] = [
    ("core", 0), ("platform", 1), ("data_parameter", 2), ("perception", 3),
    ("scenario_thesis", 4), ("fusion", 5), ("validation", 6), ("routing", 7),
    ("engines", 8), ("precision_signal", 9), ("execution_boundary", 10),
    ("risk_sizing_portfolio", 11), ("broker_orders_positions", 12),
    ("audit_learning", 13), ("application_api", 14),
]


class MissionControl:
    def __init__(self, runtime: Any) -> None:
        self.rt = runtime

    def health_matrix(self) -> list[dict]:
        rt = self.rt
        ledger_ok = rt.ledger.verify_chain()
        params_ok = not rt.params.audit_no_silent_drops()
        feed_ok = rt.sim is not None and rt.sim.tick_count > 0 and rt.feed_health()["healthy"]
        rows = [{"domain": "feed_watchdog", "layer": "L2", "status": "OK" if rt.feed_health()["healthy"] else "DEGRADED",
                 "healthy": rt.feed_health()["healthy"], "detail": rt.feed_health()}]
        for domain, layer in DOMAIN_HEALTH:
            ok = True
            if domain == "data_parameter":
                ok = feed_ok and params_ok
            elif domain == "audit_learning":
                ok = ledger_ok
            rows.append({"domain": domain, "layer": f"L{layer}", "status": "OK" if ok else "DEGRADED",
                         "healthy": ok})
        return rows

    def overview(self) -> dict:
        rt = self.rt
        account = rt.account_snapshot()
        positions = list(rt.broker.account.positions.values())
        pnl_rows = rt.pnl_calculator.compute(rt.broker.account.positions)
        floating = rt.pnl_calculator.total_net(pnl_rows)
        account["floating_pnl"] = floating
        account["equity"] = round(account["balance"] + floating, 2)
        return {
            "brand": "DAVID SLING",
            "ts": utc_now().isoformat(),
            "mode": rt.mode,
            "session_epoch": epoch_at(rt.clock_now()).value,
            "session_phase": primary_phase(rt.clock_now()),
            "account": account,
            "health": self.health_matrix(),
            "awareness": {s: snap.to_dict() for s, snap in rt.awareness.all().items()},
            "scenarios": {s: st.model_dump(mode="json") for s, st in rt.scenario_engine.current.items()},
            "fusion": {s: f.model_dump(mode="json") for s, f in rt.fusion.last.items()},
            "engines": rt.supervisor.health(),
            "signals": [t.model_dump(mode="json") for t in rt.signal_engine.recent(20)],
            "positions": [p.model_dump(mode="json") for p in positions],
            "pnl_matrix": [r.model_dump(mode="json") for r in pnl_rows],
            "alerts": [a.model_dump(mode="json") for a in rt.alerts.recent(10)],
            "ledger": {"entries": len(rt.ledger), "chain_ok": rt.ledger.verify_chain(),
                       "head": rt.ledger.head.hash[:16] if rt.ledger.head else None},
            "rescans": [e.model_dump(mode="json") for e in rt.rescan.events[-10:]],
            "monitoring": rt.monitoring.summary(),
            "feed_ticks": rt.sim.tick_count if rt.sim else 0,
        }

    def market_view(self, symbol: str | None = None) -> dict:
        rt = self.rt
        symbols = [symbol.upper()] if symbol else rt.symbols.symbols()
        out = {}
        for s in symbols:
            snap = rt.awareness.snapshot(s)
            tick = rt.sim.tick_of(s) if rt.sim else None
            candles = {tf.value: len(rt.sim.candles(s, tf)) for tf in Timeframe} if rt.sim else {}
            out[s] = {
                "price": tick.mid if tick else rt.sim.price(s),
                "bid": tick.bid if tick else None, "ask": tick.ask if tick else None,
                "awareness": snap.to_dict() if snap else None,
                "scenario": rt.scenario_engine.current.get(s).model_dump(mode="json") if rt.scenario_engine.current.get(s) else None,
                "fusion": rt.fusion.get(s).model_dump(mode="json") if rt.fusion.get(s) else None,
                "candle_counts": candles,
            }
        return out
