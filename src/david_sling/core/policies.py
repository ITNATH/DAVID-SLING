"""L0 core policies - no-time-expiry, terminal-state, abstention, determinism.

Consolidated policy module (the blueprint's no_time_expiry_policy.py,
terminal_state_policy.py, abstention_policy.py and
deterministic_decision_contract.py expressed as one enforced policy surface).
"""
from __future__ import annotations

from enum import StrEnum

from .laws import MAX_HOLD_TIME


class TerminalState(StrEnum):
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"
    NOVEL = "NOVEL"


class Abstention(StrEnum):
    WAIT = "WAIT"            # terminal UNKNOWN -> wait for more evidence
    NO_ROUTE = "NO_ROUTE"    # terminal CONFLICTED -> router abstains
    ABSTAIN = "ABSTAIN"      # terminal NOVEL -> no known grammar applies


TERMINAL_TO_ABSTENTION: dict[TerminalState, Abstention] = {
    TerminalState.UNKNOWN: Abstention.WAIT,
    TerminalState.CONFLICTED: Abstention.NO_ROUTE,
    TerminalState.NOVEL: Abstention.ABSTAIN,
}


def enforce_no_time_expiry(max_hold_time: object) -> None:
    """Globally enforce max_hold_time = null. Any configured time stop on a
    position lifecycle is rejected; exits are thesis/TP/SL/trailing driven."""
    if max_hold_time is not None or MAX_HOLD_TIME is not None:
        from .errors import ValidationError

        raise ValidationError("no_time_expiry_policy: max_hold_time must be null")


def abstention_for(terminal: TerminalState) -> Abstention:
    return TERMINAL_TO_ABSTENTION[terminal]


def assert_deterministic(decision_hash: str, replay_hash: str) -> None:
    """Deterministic decision contract: a replayed input must reproduce the
    identical decision hash, otherwise the replay contract is broken."""
    from .errors import ValidationError

    if decision_hash != replay_hash:
        raise ValidationError(
            "deterministic_decision_contract violated: replay hash mismatch "
            f"({decision_hash[:12]} != {replay_hash[:12]})"
        )
