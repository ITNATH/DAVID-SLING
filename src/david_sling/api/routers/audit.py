"""api routers: evidence ledger, alerts, journal, monitoring, rescan."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from david_sling.api.dependencies import get_runtime, require_token
from david_sling.core.schemas import StrictModel

router = APIRouter(prefix="/api", tags=["audit"], dependencies=[Depends(require_token)])


class RescanRequest(StrictModel):
    symbol: str
    reason: str = "manual"


@router.get("/evidence")
async def evidence(request: Request, limit: int = 50):
    return {"evidence": get_runtime(request).facade.evidence(limit)}


@router.get("/evidence/status")
async def evidence_status(request: Request):
    return get_runtime(request).facade.ledger_status()


@router.get("/alerts")
async def alerts(request: Request, limit: int = 50):
    return {"alerts": get_runtime(request).facade.alerts(limit)}


@router.get("/monitoring")
async def monitoring(request: Request):
    rt = get_runtime(request)
    return {"stats": rt.facade.monitoring(), "proposals": rt.monitoring.proposals[-20:]}


@router.post("/rescan")
async def rescan(payload: RescanRequest, request: Request):
    return get_runtime(request).facade.initiate_rescan(payload.model_dump())
