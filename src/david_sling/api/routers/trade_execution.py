"""api routers: trade execution - single, single-pair multi, cross-pair basket,
batch close, panic flatten, break-even all. All commands route through the
L10 boundary -> L11 risk gate -> L12 broker."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from david_sling.api.dependencies import get_runtime, require_token
from david_sling.core.schemas import StrictModel

router = APIRouter(prefix="/api/trade", tags=["trade-execution"], dependencies=[Depends(require_token)])


class SingleTrade(StrictModel):
    symbol: str
    side: str            # BUY | SELL
    order_type: str = "MARKET"
    volume: float | None = None
    price: float | None = None
    sl: float | None = None
    tp: float | None = None
    risk_pct: float | None = None


class CloseRequest(StrictModel):
    position_id: str
    pct: float | None = None     # 0.25 / 0.5 / 0.75 partial close


class SinglePairMulti(StrictModel):
    symbol: str
    side: str
    tranches: int = 1
    lots: float = 0.01
    sl: float | None = None
    tp: float | None = None


class CrossPairBasket(StrictModel):
    symbols: list[str]
    side: str
    lots: float = 0.01
    sl_atr_mult: float = 1.5
    tp_rr: float = 2.0


class BatchClose(StrictModel):
    symbol: str | None = None
    side: str | None = None
    only_profitable: bool = False
    only_losing: bool = False


@router.post("/single")
async def trade_single(payload: SingleTrade, request: Request):
    rt = get_runtime(request)
    result = rt.facade.execute_single_trade(payload.model_dump())
    await rt.telemetry.emit("trade.result", {"op": "single", **result})
    return result


@router.post("/close")
async def trade_close(payload: CloseRequest, request: Request):
    rt = get_runtime(request)
    result = rt.facade.close_position(payload.position_id, payload.pct)
    await rt.telemetry.emit("trade.result", {"op": "close", **result})
    return result


@router.post("/single-pair-multi")
async def trade_single_pair_multi(payload: SinglePairMulti, request: Request):
    rt = get_runtime(request)
    result = rt.facade.execute_single_pair_multi(payload.model_dump())
    await rt.telemetry.emit("trade.result", {"op": "single_pair_multi", **result})
    return result


@router.post("/cross-pair-basket")
async def trade_cross_pair_basket(payload: CrossPairBasket, request: Request):
    rt = get_runtime(request)
    result = rt.facade.execute_cross_pair_basket(payload.model_dump())
    await rt.telemetry.emit("trade.result", {"op": "cross_pair_basket", **result})
    return result


@router.post("/batch-close")
async def trade_batch_close(payload: BatchClose, request: Request):
    rt = get_runtime(request)
    result = rt.facade.batch_close(payload.model_dump())
    await rt.telemetry.emit("trade.result", {"op": "batch_close", "closed": result["closed"]})
    return result


@router.post("/panic-flatten")
async def trade_panic_flatten(request: Request):
    rt = get_runtime(request)
    result = rt.facade.panic_flatten()
    await rt.telemetry.emit("trade.result", {"op": "PANIC_FLATTEN", "flattened": result["flattened"]})
    return result


@router.post("/breakeven-all")
async def trade_breakeven_all(request: Request):
    return get_runtime(request).facade.breakeven_all()


@router.get("/positions")
async def trade_positions(request: Request):
    return {"positions": get_runtime(request).facade.positions()}


@router.get("/orders")
async def trade_orders(request: Request):
    return {"orders": get_runtime(request).facade.orders()}
