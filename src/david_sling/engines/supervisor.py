"""L8 engines - engine supervisor + the four peer engines.

Peer engines never import each other (peer_dependency_guard); each consumes
only the shared immutable technical context. Profiles come from
config/engines/engine_profiles.yaml.

  A Quant Scalping      15M-30M   ctx H4/H1/M30  trigger M5/M10/M15  1-2CDT
  B Tactical Intraday   1H-4H     ctx H4/H1      trigger M15/M30     2-3CDT
  C Swing Structural    4H-8H     ctx D1/H4      trigger H1/H4       3-4CDT
  D Macro Institutional 8H-Daily  ctx W1/MN1/D1  trigger H4/H8       Multi-CDT
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from david_sling.core.errors import BoundaryViolation
from david_sling.core.schemas import (
    EngineDecision,
    FusionSnapshot,
    ScenarioState,
    ValidationResult,
)
from david_sling.core.utils import utc_now
from david_sling.strategies.vault import SetupCandidate

ENGINE_LITERAL = Literal['A', 'B', 'C', 'D']

# peer dependency guard: engine modules must never import sibling engine modules
_FORBIDDEN = {"quant_scalping", "tactical_intraday", "swing_structural", "macro_institutional"}


def peer_dependency_guard(caller_module: str) -> None:
    name = caller_module.rsplit(".", 1)[-1]
    if name in _FORBIDDEN and name != caller_module.rsplit(".", 1)[-1]:
        pass
    for forbidden in _FORBIDDEN:
        if forbidden != name and f".{forbidden}" in caller_module:
            raise BoundaryViolation(f"engine-to-engine coupling detected from {caller_module}")


@dataclass(frozen=True)
class EngineProfile:
    engine_id: str
    name: str
    horizon: str
    context_tfs: tuple[str, ...]
    trigger_tfs: tuple[str, ...]
    confirmation: tuple[str, ...]
    min_convergence: float
    max_tier: int
    enabled: bool = True


PROFILES: dict[str, EngineProfile] = {
    "A": EngineProfile("A", "Quant Scalping", "15M-30M", ("H4", "H1", "M30"), ("M5", "M10", "M15"), ("1CDT", "2CDT"), 0.45, 3),
    "B": EngineProfile("B", "Tactical Intraday", "1H-4H", ("H4", "H1"), ("M15", "M30"), ("2CDT", "3CDT"), 0.50, 3),
    "C": EngineProfile("C", "Swing Structural", "4H-8H", ("D1", "H4"), ("H1", "H4"), ("3CDT", "4CDT"), 0.55, 4),
    "D": EngineProfile("D", "Macro Institutional", "8H-Daily", ("W1", "MN1", "D1"), ("H4", "H8"), ("Multi-CDT",), 0.60, 4),
}


class EngineSupervisor:
    """Supervises the four peer engines; they share only immutable context."""

    def __init__(self, profiles: dict[str, dict] | None = None) -> None:
        self.profiles = {k: PROFILES[k] for k in PROFILES}
        if profiles:
            for eid, cfg in profiles.items():
                if eid in self.profiles and isinstance(cfg, dict):
                    p = self.profiles[eid]
                    self.profiles[eid] = EngineProfile(
                        engine_id=p.engine_id, name=str(cfg.get("name", p.name)),
                        horizon=str(cfg.get("horizon", p.horizon)),
                        context_tfs=tuple(cfg.get("context_tfs", p.context_tfs)),
                        trigger_tfs=tuple(cfg.get("trigger_tfs", p.trigger_tfs)),
                        confirmation=tuple(cfg.get("confirmation", p.confirmation)),
                        min_convergence=p.min_convergence, max_tier=p.max_tier,
                        enabled=bool(cfg.get("enabled", True)),
                    )
        self.states: dict[str, str] = {k: "ARMED" for k in self.profiles}

    def set_enabled(self, engine_id: str, enabled: bool) -> None:
        p = self.profiles[engine_id]
        self.profiles[engine_id] = EngineProfile(
            p.engine_id, p.name, p.horizon, p.context_tfs, p.trigger_tfs, p.confirmation,
            p.min_convergence, p.max_tier, enabled,
        )

    def qualify(self, engine_id: str, candidate: SetupCandidate, scenario: ScenarioState,
                validation: ValidationResult, fusion: FusionSnapshot) -> EngineDecision:
        p = self.profiles[engine_id]
        ts = utc_now()
        reasons: list[str] = []
        if not p.enabled:
            reasons.append("engine disabled")
            self.states[engine_id] = "DISABLED"
            return EngineDecision(engine=cast(ENGINE_LITERAL, engine_id), qualified=False, reasons=reasons, ts=ts)
        if fusion.convergence < p.min_convergence:
            reasons.append(f"fusion convergence {fusion.convergence:.2f} < {p.min_convergence}")
        if fusion.conflicts > 2:
            reasons.append(f"too many fusion conflicts: {fusion.conflicts}")
        direction_ok = (fusion.direction == "long" and candidate.direction == "long") or \
                       (fusion.direction == "short" and candidate.direction == "short")
        if fusion.direction != "neutral" and not direction_ok:
            reasons.append("candidate direction disagrees with fusion")
        # G35: per-engine context agreement - each engine gates on its OWN context TFs
        ctx_scores = [fusion.layers.get(tf, 0.0) for tf in p.context_tfs if tf in fusion.layers]
        if ctx_scores:
            ctx_sum = sum(ctx_scores)
            ctx_dir = 1 if ctx_sum > 0.05 else (-1 if ctx_sum < -0.05 else 0)
            if ctx_dir != 0:
                cand_dir = 1 if candidate.direction == "long" else -1
                if cand_dir != ctx_dir:
                    reasons.append(f"engine {engine_id} context {list(p.context_tfs)} disagrees with candidate")
        qualified = validation.passed and not reasons
        if qualified:
            self.states[engine_id] = "TRIGGERED"
        else:
            self.states[engine_id] = "ARMED"
        return EngineDecision(engine=cast(ENGINE_LITERAL, engine_id), qualified=qualified,
                              setup=candidate.strategy_id if qualified else None,
                              reasons=reasons or ["ok"], ts=ts)

    def health(self) -> dict[str, dict]:
        return {eid: {"name": p.name, "horizon": p.horizon, "state": self.states[eid],
                      "enabled": p.enabled, "context_tfs": list(p.context_tfs),
                      "trigger_tfs": list(p.trigger_tfs)}
                for eid, p in self.profiles.items()}
