"""L0 core - constitutional laws & operating principles, enforced at import time.

Immutable global laws:
  1. One scenario authority (Universal Scenario Pool is the only classifier).
  2. One fusion brain (9-layer bidirectional coordinator is the only fusion path).
  3. Zero silent drops (every parameter passes the 8-stage lifecycle or halts).
  4. No time expiry (max_hold_time = null globally).
  5. Terminal states UNKNOWN / CONFLICTED / NOVEL map to WAIT / NO_ROUTE / ABSTAIN.
  6. Deterministic decisions: identical inputs -> identical outputs (replay contract).
"""
from __future__ import annotations

from enum import StrEnum


class ConstitutionalLaw(StrEnum):
    ONE_SCENARIO_AUTHORITY = "one_scenario_authority"
    ONE_FUSION_BRAIN = "one_fusion_brain"
    ZERO_SILENT_DROPS = "zero_silent_drops"
    NO_TIME_EXPIRY = "no_time_expiry"
    TERMINAL_STATE_ABSTENTION = "terminal_state_abstention"
    DETERMINISTIC_DECISIONS = "deterministic_decisions"
    TECHNICAL_FIREWALL = "technical_firewall_l10"


CONSTITUTIONAL_LAWS: tuple[ConstitutionalLaw, ...] = tuple(ConstitutionalLaw)

MAX_HOLD_TIME: None = None  # no_time_expiry_policy: globally enforced null

# 15-layer unidirectional dependency chain. Layer Li may import Lj only if j < i.
LAYER_NAMES: tuple[str, ...] = (
    "L0_core", "L1_platform", "L2_data_parameter", "L3_perception",
    "L4_scenario_thesis", "L5_fusion", "L6_validation", "L7_routing",
    "L8_engines", "L9_precision_signal", "L10_execution_boundary",
    "L11_risk_sizing_portfolio", "L12_broker_order_position",
    "L13_audit_learning", "L14_application_gui",
)
LAYER_INDEX: dict[str, int] = {name: i for i, name in enumerate(LAYER_NAMES)}

# Domains that technical layers (L0-L9) must never import directly; all access
# goes through the L10 execution boundary firewall.
DOWNSTREAM_FIREWALL_DOMAINS: frozenset[str] = frozenset(
    {"risk", "sizing", "portfolio", "broker", "order_management", "position_management"}
)

# Composition-root domains wire the layers together at boot; they may import
# any layer for assembly. Technical domains (L2-L9) remain strictly ordered.
COMPOSITION_ROOT_DOMAINS: frozenset[str] = frozenset(
    {"bootstrap", "mission_control", "application", "api", "control_panel",
     "security", "configuration", "storage", "services"}
)


def layer_of(domain: str) -> int:
    return LAYER_INDEX[domain] if domain in LAYER_INDEX else _domain_layer(domain)


def _domain_layer(domain: str) -> int:
    mapping = {
        "core": 0, "bootstrap": 1, "security": 1, "configuration": 1,
        "control_panel": 1, "mission_control": 1, "application": 1, "storage": 1,
        "services": 1, "parameter": 2, "evidence_ledger": 2, "data": 2,
        "awareness": 3, "intelligence": 3, "regime": 3,
        "scenario_pool": 4, "hypothesis": 4, "grammar": 4,
        "fusion": 5, "validation": 6, "routing": 7, "strategies": 7,
        "engines": 8, "precision": 9, "signal": 9, "rescan": 9,
        "execution_boundary": 10, "risk": 11, "sizing": 11, "portfolio": 11,
        "broker": 12, "order_management": 12, "position_management": 12,
        "alerts": 13, "journal": 13, "monitoring_learning": 13,
        "api": 14,
    }
    if domain not in mapping:
        from .errors import ArchitectureError

        raise ArchitectureError(f"unknown domain in architecture manifest: {domain}")
    return mapping[domain]


def assert_import_allowed(importer_domain: str, importee_domain: str) -> None:
    """Unidirectional law: technical importer Li may import Lj only if j < i
    (same-layer intra-package imports allowed). Composition-root domains may
    import anything for wiring. Technical layers may never import L11/L12
    downstream domains except through L10."""
    from .errors import ArchitectureError, BoundaryViolation

    li, lj = layer_of(importer_domain), layer_of(importee_domain)
    if importer_domain in COMPOSITION_ROOT_DOMAINS:
        return  # composition root wires all layers
    if lj > li:
        raise ArchitectureError(
            f"layer violation: {importer_domain} (L{li}) may not import {importee_domain} (L{lj})"
        )
    if li <= 9 and importee_domain in DOWNSTREAM_FIREWALL_DOMAINS:
        raise BoundaryViolation(
            f"technical layer L{li} ({importer_domain}) must not touch downstream "
            f"domain '{importee_domain}' - route through L10 execution_boundary"
        )
