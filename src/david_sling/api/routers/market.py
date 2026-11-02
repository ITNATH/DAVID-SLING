"""api routers: market data, reconstruction, candles."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from david_sling.api.dependencies import get_runtime, require_token
from david_sling.core.schemas import Timeframe

router = APIRouter(prefix="/api/market", tags=["market"], dependencies=[Depends(require_token)])


@router.get("")
async def market(request: Request, symbol: str | None = None):
    return {"market": get_runtime(request).facade.market(symbol)}


@router.get("/{symbol}")
async def market_symbol(symbol: str, request: Request):
    rt = get_runtime(request)
    view = rt.facade.market(symbol.upper())
    if symbol.upper() not in view:
        raise HTTPException(status_code=404, detail=f"unknown symbol {symbol}")
    return view[symbol.upper()]


@router.get("/{symbol}/candles")
async def market_candles(symbol: str, request: Request, tf: str = "M1", limit: int = 200):
    rt = get_runtime(request)
    symbol = symbol.upper()
    try:
        timeframe = Timeframe(tf.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"unknown timeframe {tf}") from None
    if rt.sim is None:
        raise HTTPException(status_code=503, detail="no feed running")
    candles = rt.sim.candles(symbol, timeframe, limit=min(limit, 2000))
    return {"symbol": symbol, "tf": timeframe.value,
            "candles": [c.model_dump(mode="json") for c in candles]}
