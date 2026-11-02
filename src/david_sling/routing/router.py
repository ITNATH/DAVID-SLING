"""L7 routing/router - routes a validated setup to Engines A/B/C/D or NO_ROUTE.

Eligibility comes from config/routing.yaml scenario_engine_matrix intersected
with the strategy's engine affinity; the router then asks each peer engine to
qualify the candidate. Terminal scenarios always produce NO_ROUTE/abstain.
"""
from __future__ import annotations

from typing import Any, Literal, cast

from david_sling.core.schemas import (
    EngineDecision,
    FusionSnapshot,
    RouteDecision,
    ScenarioState,
    ValidationResult,
)
from david_sling.core.utils import utc_now
from david_sling.scenario_pool.engine import TERMINAL_IDS
from david_sling.strategies.vault import SetupCandidate


class Router:
    """L7 router. The engine supervisor (L8) is injected by the composition
    root - L7 never imports L8 (strict unidirectional layer law)."""

    def __init__(self, supervisor: Any, matrix: dict[str, list[str]], min_score: float = 0.45) -> None:
        self.supervisor = supervisor
        self.matrix = matrix
        self.min_score = min_score

    def route(self, scenario: ScenarioState, candidate: SetupCandidate | None,
              validation: ValidationResult, fusion: FusionSnapshot) -> tuple[RouteDecision, EngineDecision | None]:
        ts = utc_now()
        if scenario.scenario in TERMINAL_IDS or candidate is None or not validation.passed:
            return RouteDecision(engine="NO_ROUTE", score=0.0,
                                 explanation=["abstain: terminal scenario / no candidate / validation failed"], ts=ts), None
        eligible = [e for e in self.matrix.get(scenario.scenario.value, []) if e in candidate.engines]
        if not eligible:
            return RouteDecision(engine="NO_ROUTE", score=0.0,
                                 explanation=[f"scenario {scenario.scenario.value} not eligible for strategy {candidate.strategy_id} engines"], ts=ts), None
        best: tuple[str, EngineDecision, float] | None = None
        explanations: list[str] = []
        for engine_id in eligible:
            decision = self.supervisor.qualify(engine_id, candidate, scenario, validation, fusion)
            explanations.append(f"engine {engine_id}: qualified={decision.qualified} score reasons={decision.reasons}")
            if decision.qualified:
                score = candidate.confidence * fusion.convergence
                if best is None or score > best[2]:
                    best = (engine_id, decision, score)
        if best is None or best[2] < self.min_score:
            return RouteDecision(engine="NO_ROUTE", score=0.0, explanation=explanations, ts=ts), None
        engine_id, decision, score = best
        return RouteDecision(engine=cast("Literal['A', 'B', 'C', 'D', 'NO_ROUTE']", engine_id), score=round(score, 4), explanation=explanations, ts=ts), decision
