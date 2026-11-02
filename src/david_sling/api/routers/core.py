"""api routers: health, system, security, configuration, control panel."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from david_sling import __version__
from david_sling.api.dependencies import get_runtime, require_token
from david_sling.core.schemas import StrictModel

router = APIRouter(prefix="/api", tags=["core"], dependencies=[Depends(require_token)])


class ConfigChange(StrictModel):
    key: str
    value: object
    actor: str = "operator"


@router.get("/health")
async def health(request: Request):
    rt = get_runtime(request)
    return {"status": "ok", "brand": "DAVID SLING", "version": __version__,
            "mode": rt.mode, "feed_ticks": rt.sim.tick_count if rt.sim else 0,
            "ledger_chain_ok": rt.ledger.verify_chain()}


@router.get("/system")
async def system(request: Request):
    rt = get_runtime(request)
    return {"brand": "DAVID SLING", "version": __version__, "mode": rt.mode,
            "status": rt.status_summary(), "boot_state": "READY",
            "ws_subscribers": rt.telemetry.subscribers}


@router.get("/security")
async def security(request: Request):
    return {"license": {"status": "ACTIVE", "type": "simulated-institutional",
                        "entitlements": ["engines ABCD", "strategy_vault_52", "evidence_ledger", "multi_trade_ops"]},
            "session": {"authenticated": True, "role": "master_admin"},
            "token_required": bool(__import__("os").environ.get("DAVID_SLING_API_TOKEN"))}


@router.get("/configuration")
async def configuration(request: Request):
    rt = get_runtime(request)
    return {"version": rt.cfg.version, "config": rt.cfg.raw}


@router.post("/control-panel/change")
async def control_panel_change(payload: ConfigChange, request: Request):
    rt = get_runtime(request)
    result = rt.facade.submit_config_change(payload.model_dump())
    await rt.telemetry.emit("config.changed", result)
    return result
