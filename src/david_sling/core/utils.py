"""L0 core/utilities - time, decimal, id, hashing, result, concurrency, math.

Consolidated utility surface (blueprint: utilities/{time,decimal,id,hashing,
validation,immutable,collection,result,concurrency,math}_utils.py).
Price/lot arithmetic uses exact decimal.Decimal - never binary floats.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_DOWN, Decimal
from typing import Any, Generic, TypeVar


# ---------------------------------------------------------------- time utils
def utc_now() -> datetime:
    return datetime.now(UTC)


def epoch_ms(dt: datetime | None = None) -> int:
    dt = dt or utc_now()
    return int(dt.timestamp() * 1000)


def epoch_s(dt: datetime | None = None) -> float:
    dt = dt or utc_now()
    return dt.timestamp()


# ------------------------------------------------------------ decimal utils
TWO = Decimal("0.01")


def to_decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def quantize_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def price_quantize(price: Decimal, digits: int) -> Decimal:
    return price.quantize(Decimal(1).scaleb(-digits))


# ------------------------------------------------------------------ id utils
DAVID_NAMESPACE = uuid.UUID("d41d5511-51a7-5510-9a11-1e5f00d5cafe")


def deterministic_id(*parts: Any) -> str:
    return str(uuid.uuid5(DAVID_NAMESPACE, ":".join(str(p) for p in parts)))


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:16]}"


# -------------------------------------------------------------- hashing utils
def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hex(data: str | bytes) -> str:
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def sha3_256_hex(data: str | bytes) -> str:
    return hashlib.sha3_256(data.encode() if isinstance(data, str) else data).hexdigest()


def blake2b_hex(data: str | bytes) -> str:
    return hashlib.blake2b(data.encode() if isinstance(data, str) else data, digest_size=32).hexdigest()


def hash_record(payload: dict[str, Any], prev_hash: str) -> str:
    """Hash-chain link: SHA3-256(prev_hash || canonical(payload))."""
    return sha3_256_hex(prev_hash + canonical_json(payload))


# --------------------------------------------------------------- result utils
T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def unwrap(self) -> T:
        return self.value


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def unwrap(self) -> Any:
        raise self.error if isinstance(self.error, Exception) else RuntimeError(str(self.error))


Result = Ok[T] | Err[E]


# ---------------------------------------------------------- concurrency utils
async def call_maybe_async(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    out = fn(*args, **kwargs)
    if isinstance(out, Awaitable):
        return await out
    return out


class NonBlockingLock:
    """Async lock that never blocks the event loop for more than one yield."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> NonBlockingLock:
        await self._lock.acquire()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        self._lock.release()


# ------------------------------------------------------------------ math utils
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return float((sum((v - m) ** 2 for v in values) / (len(values) - 1)) ** 0.5)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def now_ms() -> int:
    return time.perf_counter_ns() // 1_000_000
