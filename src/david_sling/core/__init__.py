"""L0 - Constitutional Shared Kernel."""
from __future__ import annotations

from . import errors, laws, schemas, utils
from .contracts import ALL_STAGES, ParameterLifecycleStage
from .errors import DavidSlingError, UntrackedParameterError
from .three_core_confluence_gatekeeper import (
    ThreeCoreConfluenceGatekeeper,
    ThreeCoreScore,
)

__all__ = [
    "errors", "laws", "schemas", "utils", "DavidSlingError", "UntrackedParameterError",
    "ThreeCoreConfluenceGatekeeper", "ThreeCoreScore", "ALL_STAGES", "ParameterLifecycleStage",
]


# Constitutional self-check at import time (blueprint: operating_principles.py /
# architecture_integrity_check.py): the 15-layer chain must be acyclic and
# strictly ordered, and the downstream firewall domains must sit strictly above
# every technical layer.
def _import_time_constitution_check() -> None:
    from david_sling.core.dependency_graph import DependencyGraph
    from david_sling.core.laws import (
        COMPOSITION_ROOT_DOMAINS,
        DOWNSTREAM_FIREWALL_DOMAINS,
        LAYER_NAMES,
        layer_of,
    )

    g = DependencyGraph()
    for i in range(1, len(LAYER_NAMES)):
        g.add_edge(LAYER_NAMES[i], LAYER_NAMES[i - 1])
    g.verify()
    for dom in DOWNSTREAM_FIREWALL_DOMAINS:
        assert layer_of(dom) > 9, f"firewall domain {dom} must live above L9"
        assert dom not in COMPOSITION_ROOT_DOMAINS


_import_time_constitution_check()
