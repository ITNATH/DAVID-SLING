"""L1 configuration/configuration_engine - loads the config/ YAML tree.

Precedence (no silent overrides): defaults < config/*.yaml < environment
variables (DAVID_SLING_*). The effective configuration is an immutable
snapshot; mutations go through the control panel command path only.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from david_sling.core.errors import ConfigurationError, ValidationError

CONFIG_ROOT = Path(__file__).resolve().parents[3] / "config"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@dataclass(frozen=True)
class EffectiveConfiguration:
    """Immutable effective configuration snapshot."""

    raw: dict[str, Any]
    version: int = 1
    source_files: tuple[str, ...] = field(default_factory=tuple)

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.raw
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def require(self, dotted: str) -> Any:
        value = self.get(dotted)
        if value is None:
            raise ConfigurationError(f"missing required configuration key: {dotted}")
        return value


class ConfigurationEngine:
    """Supreme configuration coordinator."""

    def __init__(self, config_root: Path | None = None) -> None:
        self.root = config_root or CONFIG_ROOT
        self._effective: EffectiveConfiguration | None = None
        self._versions: list[EffectiveConfiguration] = []

    # ------------------------------------------------------------- loading
    def load(self) -> EffectiveConfiguration:
        merged: dict[str, Any] = {}
        files: list[str] = []
        for path in sorted(self.root.rglob("*.yaml")):
            rel = str(path.relative_to(self.root))
            merged = _deep_merge(merged, _load_yaml(path))
            files.append(rel)
        # environment overrides (explicit, never silent)
        env_overrides: dict[str, Any] = {}
        for key, value in os.environ.items():
            if key.startswith("DAVID_SLING_"):
                env_overrides[key[len("DAVID_SLING_"):].lower()] = value
        if env_overrides:
            merged = _deep_merge(merged, {"env": env_overrides})
        self._effective = EffectiveConfiguration(raw=merged, source_files=tuple(files))
        self._versions.append(self._effective)
        self._validate(self._effective)
        return self._effective

    @property
    def effective(self) -> EffectiveConfiguration:
        if self._effective is None:
            return self.load()
        return self._effective

    # ---------------------------------------------------------- validation
    @staticmethod
    def _validate(cfg: EffectiveConfiguration) -> None:
        # constitutional: max_hold_time must be null
        mht = cfg.get("boot_state.max_hold_time", None)
        if mht is not None:
            raise ValidationError("boot_state.max_hold_time must be null (no_time_expiry_policy)")
        # risk sanity
        session_cap = float(cfg.get("risk.risk_policy.session_risk_cap_pct", 1.50))
        if not 0 < session_cap <= 10:
            raise ValidationError("risk.session_risk_cap_pct out of range (0, 10]")
        # confluence weights must sum to 1.0
        w = cfg.get("confluence_weights", {})
        total = float(w.get("price_action", 0.40)) + float(w.get("candle_cdt", 0.35)) + float(w.get("indicators", 0.25))
        if abs(total - 1.0) > 1e-9:
            raise ValidationError(f"confluence_weights must sum to 1.0, got {total}")

    # ------------------------------------------------------- control panel
    def apply_change(self, dotted: str, value: Any, *, actor: str = "operator") -> EffectiveConfiguration:
        """Versioned, audited configuration mutation (control panel path)."""
        import copy

        new_raw = copy.deepcopy(self.effective.raw)
        node = new_raw
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise ConfigurationError(f"cannot set {dotted}: {part} is not a mapping")
        node[parts[-1]] = value
        candidate = EffectiveConfiguration(raw=new_raw, version=self.effective.version + 1,
                                           source_files=self.effective.source_files)
        self._validate(candidate)
        self._effective = candidate
        self._versions.append(candidate)
        return candidate

    def history(self) -> list[EffectiveConfiguration]:
        return list(self._versions)

    def rollback(self) -> EffectiveConfiguration:
        if len(self._versions) < 2:
            raise ConfigurationError("no previous configuration version to roll back to")
        self._versions.pop()
        self._effective = self._versions[-1]
        return self._effective
