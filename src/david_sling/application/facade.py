"""L14 application/service_facade - controlled entry point for all use cases.

Use cases: boot, query system/market/scenario/fusion/engines/signals/orders/
positions/evidence, execute single / single-pair-multi / cross-pair basket,
batch close, panic flatten, control-panel config change, audit export, rescan.
Commands arrive via the command bus (authorized + audited).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from david_sling.core.schemas import OrderSide, OrderType
from david_sling.mission_control.ops import MultiTradeOperationsEngine

if TYPE_CHECKING:
    from david_sling.bootstrap.runtime import Runtime


class ServiceFacade:
    def __init__(self, runtime: Runtime) -> None:
        self.rt = runtime

    # ------------------------------------------------------------- queries
    def overview(self) -> dict:
        return dict(self.rt.mission_control.overview())

    def market(self, symbol: str | None = None) -> dict:
        return dict(self.rt.mission_control.market_view(symbol))

    def signals(self, limit: int = 50) -> list[dict]:
        return [t.model_dump(mode="json") for t in self.rt.signal_engine.recent(limit)]

    def positions(self) -> list[dict]:
        return [p.model_dump(mode="json") for p in self.rt.broker.account.positions.values()]

    def orders(self) -> list[dict]:
        return [{"intent_id": o.intent.intent_id, "symbol": o.intent.symbol,
                 "status": o.status.value, "fill": o.report.fill_price if o.report else None}
                for o in self.rt.order_manager.all()]

    def pnl_matrix(self) -> list[dict]:
        return [r.model_dump(mode="json") for r in self.rt.pnl_calculator.compute(self.rt.broker.account.positions)]

    def evidence(self, limit: int = 50) -> list[dict]:
        return [r.model_dump(mode="json") for r in self.rt.ledger.all()[-limit:]]

    def ledger_status(self) -> dict:
        return {"entries": len(self.rt.ledger), "head": self.rt.ledger.head.hash if self.rt.ledger.head else None,
                "chain_ok": self.rt.ledger.verify_chain(), "merkle_root": self.rt.ledger.merkle_root()}

    def alerts(self, limit: int = 50) -> list[dict]:
        return [a.model_dump(mode="json") for a in self.rt.alerts.recent(limit)]

    def monitoring(self) -> dict:
        return dict(self.rt.monitoring.summary())

    def health(self) -> list[dict]:
        return list(self.rt.mission_control.health_matrix())

    def config(self) -> dict:
        return dict(self.rt.config_engine.effective.raw)

    # ------------------------------------------------------------ commands
    def execute_single_trade(self, payload: dict) -> dict:
        ops: MultiTradeOperationsEngine = self.rt.ops
        acct = self.rt.account_snapshot()
        positions = list(self.rt.broker.account.positions.values())
        res = ops.single_trade(
            symbol=payload["symbol"].upper(), side=OrderSide(payload["side"].upper()),
            volume=payload.get("volume"), order_type=OrderType(payload.get("order_type", "MARKET").upper()),
            price=payload.get("price"), sl=payload.get("sl"), tp=payload.get("tp"),
            risk_pct=payload.get("risk_pct"), account=acct, positions=positions,
            atr_now_fn=self.rt.atr_now, atr_avg_fn=self.rt.atr_avg,
            spread_now_fn=self.rt.spread_now, spread_avg_fn=self.rt.spread_avg,
            news_active=self.rt.news_active,
        )
        return {"ok": res.ok, "orders": res.orders, "vetoed": res.vetoed, "message": res.message}

    def close_position(self, position_id: str, pct: float | None = None) -> dict:
        if pct:
            trade = self.rt.tms.partial_close(position_id, pct)
        else:
            trade = self.rt.tms.close_position(position_id)
        return {"closed": trade is not None,
                "trade": trade.__dict__ if trade else None}

    def execute_single_pair_multi(self, payload: dict) -> dict:
        ops = self.rt.ops
        acct = self.rt.account_snapshot()
        positions = list(self.rt.broker.account.positions.values())
        res = ops.single_pair_multi(
            symbol=payload["symbol"].upper(), side=OrderSide(payload["side"].upper()),
            tranches=int(payload.get("tranches", 1)), lots_per_tranche=float(payload.get("lots", 0.01)),
            sl=payload.get("sl"), tp=payload.get("tp"), account=acct, positions=positions,
            atr_now_fn=self.rt.atr_now, atr_avg_fn=self.rt.atr_avg,
            spread_now_fn=self.rt.spread_now, spread_avg_fn=lambda s: self.rt.symbols.get(s).spread_points,
            news_active=self.rt.news_active,
        )
        return {"ok": res.ok, "orders": res.orders, "vetoed": res.vetoed, "message": res.message}

    def execute_cross_pair_basket(self, payload: dict) -> dict:
        ops = self.rt.ops
        acct = self.rt.account_snapshot()
        positions = list(self.rt.broker.account.positions.values())
        res = ops.cross_pair_basket(
            symbols=[s.upper() for s in payload["symbols"]], side=OrderSide(payload["side"].upper()),
            lots=float(payload.get("lots", 0.01)), sl_atr_mult=float(payload.get("sl_atr_mult", 1.5)),
            tp_rr=float(payload.get("tp_rr", 2.0)), account=acct, positions=positions,
            atr_now_fn=self.rt.atr_now, atr_avg_fn=self.rt.atr_avg,
            spread_now_fn=self.rt.spread_now, spread_avg_fn=lambda s: self.rt.symbols.get(s).spread_points,
            news_active=self.rt.news_active,
        )
        return {"ok": res.ok, "orders": res.orders, "vetoed": res.vetoed, "message": res.message}

    def batch_close(self, payload: dict) -> dict:
        trades = self.rt.tms.batch_close(
            symbol=(payload.get("symbol") or "").upper() or None,
            side=(payload.get("side") or "").upper() or None,
            only_profitable=bool(payload.get("only_profitable", False)),
            only_losing=bool(payload.get("only_losing", False)),
        )
        return {"closed": len(trades), "trades": [t.__dict__ for t in trades]}

    def panic_flatten(self) -> dict:
        trades = self.rt.tms.panic_flatten()
        return {"flattened": len(trades), "trades": [t.__dict__ for t in trades]}

    def breakeven_all(self) -> dict:
        return {"breakeven_set": self.rt.tms.breakeven_all()}

    def submit_config_change(self, payload: dict) -> dict:
        return self.rt.control_panel.change(payload["key"], payload["value"],
                                            actor=payload.get("actor", "operator"))

    def engines_status(self) -> dict:
        return {"engines": self.rt.supervisor.health(),
                "config_version": self.rt.cfg.version,
                "mutations": [e.payload for e in self.rt.ledger.by_kind("engine.toggled")[-20:]]}

    def set_engine(self, engine_id: str, enabled: bool, *, actor: str = "operator") -> dict:
        return self.rt.set_engine_enabled(engine_id, enabled, actor=actor)

    def halt_trading(self, reason: str = "operator emergency halt") -> dict:
        self.rt.risk.halt(reason)
        self.rt.ledger.append("risk.halt", {"reason": reason})
        return {"halted": True, "reason": reason}

    def resume_trading(self) -> dict:
        self.rt.risk.resume()
        self.rt.ledger.append("risk.resume", {})
        return {"halted": False}

    def initiate_rescan(self, payload: dict) -> dict:
        ev = self.rt.rescan.rescan(payload["symbol"].upper(), payload.get("reason", "manual"))
        return dict(ev.model_dump(mode="json"))
