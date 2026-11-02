"""L9 precision_engine - grades WHERE & coordinate quality into Tier 1-4.

Score = evidence density + fusion convergence + location/zone quality
        - contradiction penalty. Thresholds from config/precision_thresholds.yaml.
"""
from __future__ import annotations

from david_sling.core.schemas import FusionSnapshot, PrecisionGrade, ValidationResult
from david_sling.core.utils import clamp
from david_sling.intelligence.features import FeatureSet


class PrecisionEngine:
    def __init__(self, tiers: dict[str, float] | None = None, min_routed: float = 0.55) -> None:
        self.tiers = tiers or {"tier1": 0.85, "tier2": 0.70, "tier3": 0.55, "tier4": 0.40}
        self.min_routed = min_routed

    def grade(self, fs: FeatureSet, validation: ValidationResult, fusion: FusionSnapshot) -> PrecisionGrade:
        evidence_density = clamp(len(fs.observations) / 24.0, 0.0, 1.0)
        convergence = fusion.convergence
        location = 0.0
        if fs.fvg_up_m5 or fs.fvg_dn_m5:
            location += 0.4
        if fs.rejection_up or fs.rejection_dn:
            location += 0.3
        if abs(fs.price - fs.vwap_m1) / max(fs.atr_m1, 1e-12) < 1.0:
            location += 0.3
        location = clamp(location, 0.0, 1.0)
        contradiction_penalty = 0.25 if validation.hard_conflict else 0.1 * len(validation.contradictions)
        score = clamp(0.35 * evidence_density + 0.35 * convergence + 0.30 * location - contradiction_penalty, 0.0, 1.0)
        if score >= self.tiers["tier1"]:
            tier = 1
        elif score >= self.tiers["tier2"]:
            tier = 2
        elif score >= self.tiers["tier3"]:
            tier = 3
        else:
            tier = 4
        return PrecisionGrade(tier=tier, score=round(score, 4), components={
            "evidence_density": round(evidence_density, 4),
            "convergence": round(convergence, 4),
            "location_quality": round(location, 4),
            "contradiction_penalty": round(contradiction_penalty, 4),
        })

    def routable(self, grade: PrecisionGrade) -> bool:
        return grade.score >= self.min_routed and grade.tier <= 3
