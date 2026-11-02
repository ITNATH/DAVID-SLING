"""L1 services/symbol_registry - canonical instrument registry from config."""
from __future__ import annotations

from david_sling.core.schemas import SymbolSpec


class SymbolRegistry:
    def __init__(self, specs: dict[str, SymbolSpec]) -> None:
        self._specs = specs

    def get(self, symbol: str) -> SymbolSpec:
        return self._specs[symbol.upper()]

    def has(self, symbol: str) -> bool:
        return symbol.upper() in self._specs

    def all(self) -> list[SymbolSpec]:
        return list(self._specs.values())

    def symbols(self) -> list[str]:
        return sorted(self._specs)
