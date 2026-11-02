"""L11 exposure_engine - net currency exposure, correlation & concentration.

FX exposure attribution: EURUSD buy -> +EUR, -USD. Correlation guard uses
config/portfolio/correlation_matrix.yaml; a basket adding highly correlated
same-direction exposure is flagged.
"""
from __future__ import annotations

from david_sling.core.schemas import PositionState, SymbolSpec


def currency_exposure(symbol: str, side: str, volume: float, contract_size: float) -> dict[str, float]:
    base, quote = symbol[:3], symbol[3:6]
    notional = volume * contract_size
    sign = 1.0 if side == "BUY" else -1.0
    return {base: sign * notional, quote: -sign * notional}


class PortfolioExposure:
    def __init__(self, correlation_matrix: dict[str, dict[str, float]] | None = None,
                 per_currency_pct: float = 25.0, total_pct: float = 60.0) -> None:
        self.corr = correlation_matrix or {}
        self.per_currency_pct = per_currency_pct
        self.total_pct = total_pct

    def net_exposure(self, positions: list[PositionState], specs: dict[str, SymbolSpec]) -> dict[str, float]:
        out: dict[str, float] = {}
        for p in positions:
            spec = specs.get(p.symbol)
            if spec is None:
                continue
            for ccy, amt in currency_exposure(p.symbol, p.side.value, p.volume, spec.contract_size).items():
                out[ccy] = out.get(ccy, 0.0) + amt
        return out

    def concentration_ok(self, exposure: dict[str, float], equity: float) -> tuple[bool, list[str]]:
        problems: list[str] = []
        if equity <= 0:
            return True, []
        for ccy, amt in exposure.items():
            if abs(amt) / equity * 100 > self.per_currency_pct:
                problems.append(f"{ccy} exposure {abs(amt)/equity*100:.1f}% > {self.per_currency_pct}%")
        total = sum(abs(v) for v in exposure.values())
        if total / equity * 100 > self.total_pct:
            problems.append(f"total exposure {total/equity*100:.1f}% > {self.total_pct}%")
        return not problems, problems

    def basket_correlation_risk(self, symbols: list[str], direction: str) -> tuple[bool, list[str]]:
        """Flag baskets whose legs are highly correlated in the same direction."""
        problems: list[str] = []
        for i, a in enumerate(symbols):
            for b in symbols[i + 1:]:
                corr = abs(self.corr.get(a, {}).get(b, 0.0))
                if corr >= 0.8:
                    problems.append(f"{a}/{b} correlation {corr:.2f} - unhedged concentration")
        return not problems, problems
