"""L0 core/errors - complete David Sling error taxonomy (19 public classes).

Every domain failure raises a typed error from this module so the audit
pipeline can classify it. `UntrackedParameterError` is the zero-silent-drop
tripwire: any parameter that bypasses the mandatory lifecycle halts execution.
"""
from __future__ import annotations


class DavidSlingError(Exception):
    """Root David Sling error type."""

    def __init__(self, message: str, *, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class ArchitectureError(DavidSlingError):
    """Architecture manifest / dependency violations."""


class BoundaryViolation(DavidSlingError):
    """Cross-domain firewall violation (e.g. technical core touching L11/L12)."""


class ValidationError(DavidSlingError):
    """Schema or semantic validation failure."""


class ConfigurationError(DavidSlingError):
    """Invalid or unauthorized configuration."""


class BootError(DavidSlingError):
    """Boot sequence failure."""


class SecurityError(DavidSlingError):
    """Authentication / authorization failure."""


class LicenseError(DavidSlingError):
    """License validation failure."""


class EvidenceError(DavidSlingError):
    """Evidence chain / ledger failure."""


class ParameterError(DavidSlingError):
    """Parameter lifecycle failure."""


class UntrackedParameterError(ParameterError):
    """Raised when a parameter bypasses the mandatory lifecycle (zero silent drops)."""


class ScenarioError(DavidSlingError):
    """Scenario classification failure."""


class FusionError(DavidSlingError):
    """Fusion coordination failure."""


class RoutingError(DavidSlingError):
    """Engine routing failure."""


class EngineError(DavidSlingError):
    """Engine qualification failure."""


class PrecisionError(DavidSlingError):
    """Precision evaluation failure."""


class SignalError(DavidSlingError):
    """Signal construction failure."""


class ExecutionError(DavidSlingError):
    """Downstream handoff failure."""


class MultiTradeError(ExecutionError):
    """Batch / cross-pair execution failure."""


class DataError(DavidSlingError):
    """Ingestion / integrity failure."""


class AlertError(DavidSlingError):
    """Alert dispatch failure."""


__all__ = [
    "DavidSlingError", "ArchitectureError", "BoundaryViolation", "ValidationError",
    "ConfigurationError", "BootError", "SecurityError", "LicenseError", "EvidenceError",
    "ParameterError", "UntrackedParameterError", "ScenarioError", "FusionError",
    "RoutingError", "EngineError", "PrecisionError", "SignalError", "ExecutionError",
    "MultiTradeError", "DataError", "AlertError",
]
