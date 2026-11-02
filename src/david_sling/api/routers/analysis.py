"""api routers: awareness, intelligence, regime, scenario pool, fusion,
validation, routing, strategy vault, engines, precision, signals."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from david_sling.api.dependencies import get_runtime, require_token

router = APIRouter(prefix="/api", tags=["analysis"], dependencies=[Depends(require_token)])


@router.get("/signals")
async def signals(request: Request, limit: int = 50):
    return {"signals": get_runtime(request).facade.signals(limit)}


@router.get("/engines")
async def engines(request: Request):
    rt = get_runtime(request)
    return {"engines": rt.supervisor.health()}


@router.get("/strategies")
async def strategies(request: Request):
    rt = get_runtime(request)
    return {"count": len(rt.vault.all()),
            "strategies": [{"id": s.sid, "name": s.name, "family": s.family, "engines": list(s.engines)}
                           for s in rt.vault.all()]}


@router.get("/analysis/{symbol}")
async def analysis_symbol(symbol: str, request: Request):
    rt = get_runtime(request)
    symbol = symbol.upper()
    fs = rt.intelligence.last_features.get(symbol)
    return {
        "symbol": symbol,
        "awareness": rt.awareness.snapshot(symbol).to_dict() if rt.awareness.snapshot(symbol) else None,
        "scenario": rt.scenario_engine.current.get(symbol).model_dump(mode="json") if rt.scenario_engine.current.get(symbol) else None,
        "fusion": rt.fusion.get(symbol).model_dump(mode="json") if rt.fusion.get(symbol) else None,
        "hypothesis": rt.hypothesis.get(symbol).model_dump(mode="json") if rt.hypothesis.get(symbol) else None,
        "grammar": rt.grammar.get(symbol).__dict__ if rt.grammar.get(symbol) else None,
        "features": {k: v for k, v in fs.__dict__.items() if k != "observations"} if fs else None,
        "observations": fs.observations if fs else [],
    }


@router.get("/routing/matrix")
async def routing_matrix(request: Request):
    return {"matrix": get_runtime(request).router.matrix}
