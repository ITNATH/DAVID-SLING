"""api routers: mission control overview telemetry endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from david_sling.api.dependencies import get_runtime, require_token

router = APIRouter(prefix="/api/mission-control", tags=["mission-control"], dependencies=[Depends(require_token)])


@router.get("/overview")
async def overview(request: Request):
    return get_runtime(request).facade.overview()


@router.get("/health-matrix")
async def health_matrix(request: Request):
    return {"health": get_runtime(request).facade.health()}


@router.get("/pnl-matrix")
async def pnl_matrix(request: Request):
    return {"matrix": get_runtime(request).facade.pnl_matrix()}

