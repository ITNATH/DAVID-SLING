"""L0 core/schemas - Pydantic v2 data contracts for the whole system.

Consolidated schema surface (blueprint: core/schemas/*.py, 26 schemas):
market ingestion schemas, lifecycle state schemas and decision schemas.
All models are strict about types; prices/lots are carried as str-decimal
fields where exact arithmetic matters (see core.utils.to_decimal).
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# ------------------------------------------------------------- market schemas
class Timeframe(StrEnum):
    MN1 = "MN1"
    W1 = "W1"
    D1 = "D1"
    H8 = "H8"
    H4 = "H4"
    H1 = "H1"
    M30 = "M30"
    M15 = "M15"
    M5 = "M5"
    M1 = "M1"


TF_MINUTES: dict[Timeframe, int] = {
    Timeframe.MN1: 43200, Timeframe.W1: 10080, Timeframe.D1: 1440,
    Timeframe.H8: 480, Timeframe.H4: 240, Timeframe.H1: 60,
    Timeframe.M30: 30, Timeframe.M15: 15, Timeframe.M5: 5, Timeframe.M1: 1,
}


class SymbolSpec(StrictModel):
    name: str
    digits: int = 5
    tick_size: float
    tick_value: float          # currency value of one tick per 1.0 lot
    contract_size: float = 100_000.0
    min_lot: float = 0.01
    lot_step: float = 0.01
    max_lot: float = 100.0
    spread_points: float = 2.0
    margin_rate: float = 0.02
    currency_profit: str = "USD"
    currency_margin: str = "USD"


class Tick(StrictModel):
    symbol: str
    bid: float
    ask: float
    ts: datetime

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0


class Candle(StrictModel):
    symbol: str
    tf: Timeframe
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    tick_count: int = 0


class OrderBookLevel(StrictModel):
    price: float
    volume: float


class OrderBookSnapshot(StrictModel):
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    ts: datetime


class TradeFlow(StrictModel):
    symbol: str
    price: float
    volume: float
    side: Literal["buy", "sell"]
    ts: datetime


class NewsEvent(StrictModel):
    headline: str
    currency: str
    impact: Literal["low", "medium", "high"]
    ts: datetime


# ----------------------------------------------------------- lifecycle schemas
class ParameterStateValue(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    MISSING = "MISSING"
    STALE = "STALE"
    CONFLICTED = "CONFLICTED"


class ParameterRecord(StrictModel):
    name: str
    value: Any
    state: ParameterStateValue = ParameterStateValue.VALID
    source: str = "unknown"
    symbol: str | None = None
    timeframe: Timeframe | None = None
    ts: datetime
    param_hash: str = ""


class ScenarioId(StrEnum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"
    S5 = "S5"
    S6 = "S6"
    S7 = "S7"
    S8 = "S8"
    S9 = "S9"
    S10 = "S10"
    S11 = "S11"
    S12 = "S12"
    S13 = "S13"
    S14 = "S14"
    S15 = "S15"
    S16 = "S16"
    S17 = "S17"
    S18 = "S18"
    S19 = "S19"
    S20 = "S20"
    S21 = "S21"
    S22 = "S22"
    S23 = "S23"
    S24 = "S24"
    S25 = "S25"
    S26 = "S26"
    S27 = "S27"
    S28 = "S28"
    S29 = "S29"
    S30 = "S30"
    S31 = "S31"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"
    NOVEL = "NOVEL"


class ScenarioState(StrictModel):
    scenario: ScenarioId
    family: str
    confidence: float = Field(ge=0.0, le=1.0)
    forming: bool = False
    ts: datetime


class RegimeState(StrictModel):
    regime: str
    confidence: float = Field(ge=0.0, le=1.0)
    ts: datetime


class FusionSnapshot(StrictModel):
    symbol: str
    layers: dict[str, float]          # timeframe -> directional score -1..1
    convergence: float = Field(ge=0.0, le=1.0)
    direction: Literal["long", "short", "neutral"]
    conflicts: int = 0
    ts: datetime


class ValidationResult(StrictModel):
    passed: bool
    pa_score: float
    cdt_score: float
    indicator_score: float
    weighted: float
    hard_conflict: bool = False
    contradictions: list[str] = Field(default_factory=list)


class HypothesisStateValue(StrEnum):
    ARMED = "ARMED"
    TRIGGERED = "TRIGGERED"
    HOLD = "HOLD"
    CHANGE = "CHANGE"
    FAILURE = "FAILURE"


class HypothesisState(StrictModel):
    direction: Literal["bullish", "bearish", "neutral"]
    state: HypothesisStateValue
    invalidation_price: float | None = None
    ts: datetime


# ----------------------------------------------------------- decision schemas
class RouteDecision(StrictModel):
    engine: Literal["A", "B", "C", "D", "NO_ROUTE"]
    score: float
    explanation: list[str] = Field(default_factory=list)
    ts: datetime


class EngineDecision(StrictModel):
    engine: Literal["A", "B", "C", "D"]
    qualified: bool
    setup: str | None = None
    reasons: list[str] = Field(default_factory=list)
    ts: datetime


class PrecisionGrade(StrictModel):
    tier: int = Field(ge=1, le=4)
    score: float = Field(ge=0.0, le=1.0)
    components: dict[str, float] = Field(default_factory=dict)


class SignalStatus(StrEnum):
    PENDING = "PENDING"
    TRIGGERED = "TRIGGERED"
    ROUTED = "ROUTED"
    FILLED = "FILLED"
    ABORTED = "ABORTED"
    VETOED = "VETOED"


class SignalTicket(StrictModel):
    signal_id: str
    symbol: str
    direction: Literal["long", "short"]
    scenario: ScenarioId
    strategy_id: str
    engine: Literal["A", "B", "C", "D"]
    entry_zone: tuple[float, float]
    stop_loss: float
    take_profit: float
    risk_reward: float
    precision: PrecisionGrade
    evidence_ids: list[str] = Field(default_factory=list)
    status: SignalStatus = SignalStatus.PENDING
    ts: datetime


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderIntent(StrictModel):
    intent_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    volume: float
    price: float | None = None      # required for LIMIT/STOP
    stop_loss: float | None = None
    take_profit: float | None = None
    signal_id: str | None = None    # set when routed from a TechnicalSignalTicket
    idempotency_key: str
    ts: datetime


class BasketType(StrEnum):
    SINGLE_PAIR_MULTI = "single_pair_multi"
    CROSS_PAIR_BASKET = "cross_pair_basket"


class MultiTradeIntent(StrictModel):
    basket_id: str
    basket_type: BasketType
    orders: list[OrderIntent]
    ts: datetime


class ExecutionReport(StrictModel):
    """Broker execution report (order fill) - L12 contract."""

    intent_id: str
    position_id: str = ""
    symbol: str = ""
    side: str = ""
    volume: float = 0.0
    fill_price: float = 0.0
    status: str = "FILLED"
    slippage_points: float = 0.0
    spread_cost: float = 0.0
    ts: datetime


class PositionState(StrictModel):
    position_id: str
    symbol: str
    side: OrderSide
    volume: float
    entry_price: float
    stop_loss: float | None = None
    take_profit: float | None = None
    breakeven_done: bool = False
    trailing_active: bool = False
    realized_pnl: float = 0.0
    swap: float = 0.0
    open_ts: datetime


class CrossPairPnL(StrictModel):
    symbol: str
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net: float = 0.0
    swap: float = 0.0
    spread_cost: float = 0.0
    margin: float = 0.0
    open_positions: int = 0


class AlertLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertEvent(StrictModel):
    alert_id: str
    level: AlertLevel
    channel: str
    message: str
    ts: datetime


class RescanEvent(StrictModel):
    rescan_id: str
    symbol: str
    reason: str
    duration_ms: float
    ts: datetime


class EvidenceRecord(StrictModel):
    evidence_id: str
    kind: str
    payload: dict[str, Any]
    parent_ids: list[str] = Field(default_factory=list)
    prev_hash: str
    hash: str
    ts: datetime
