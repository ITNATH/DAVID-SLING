"""L0 core/architecture_manifest - authoritative registry of domains & layers."""
from __future__ import annotations

from .laws import LAYER_INDEX, LAYER_NAMES, layer_of

DOMAIN_LAYER: dict[str, int] = {name.split("_", 1)[1] if "_" in name else name: idx
                                for name, idx in LAYER_INDEX.items()}


def register_module(module_path: str, domain: str) -> None:
    """Runtime registry hook used by the architecture audit script."""
    layer_of(domain)  # validates
    _MODULES.setdefault(domain, []).append(module_path)


_MODULES: dict[str, list[str]] = {}


def manifest() -> dict[str, int]:
    return dict(LAYER_INDEX)


def modules() -> dict[str, list[str]]:
    return {k: list(v) for k, v in _MODULES.items()}


__all__ = ["LAYER_NAMES", "manifest", "register_module", "modules"]
