"""api/routers - API endpoint routers (30 routes consolidated into groups)."""
from __future__ import annotations

from . import analysis, audit, core, market, mission_control, trade_execution

__all__ = ["analysis", "audit", "core", "market", "mission_control", "trade_execution"]
