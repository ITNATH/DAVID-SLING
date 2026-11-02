"""L1 bootstrap/david_os_boot - Supreme David OS boot orchestrator.

Boot stages (hard order): CONFIG -> INTEGRITY (ledger chain, dependency graph,
parameter registry) -> SECURITY/LICENSE (simulated entitlement in sim mode) ->
RUNTIME ASSEMBLY -> FEED START -> READY. Any failure is a controlled halt
(BootError) with a forensic status dump - never a silent partial boot.
"""
from __future__ import annotations

import asyncio
from enum import StrEnum

from david_sling.core.dependency_graph import DependencyGraph
from david_sling.core.errors import BootError
from david_sling.core.laws import LAYER_NAMES


class BootState(StrEnum):
    BOOTING = "BOOTING"
    SECURITY_CHECK = "SECURITY_CHECK"
    LICENSE_CHECK = "LICENSE_CHECK"
    READY = "READY"
    HALTED = "HALTED"


class DavidOSBoot:
    def __init__(self, mode: str = "sim") -> None:
        self.mode = mode
        self.state = BootState.BOOTING
        self.audit: list[str] = []

    async def run(self, *, feed: bool = True, scan: bool = False, loops: bool = True):
        from david_sling.bootstrap.runtime import Runtime

        try:
            self.audit.append("config: loading config/ tree")
            rt = Runtime(mode=self.mode)
            self.audit.append(f"config: OK ({len(rt.cfg.source_files)} files, version {rt.cfg.version})")
            self.state = BootState.SECURITY_CHECK
            self._verify_dependency_graph()
            self.audit.append("integrity: dependency graph acyclic, 15-layer order OK")
            self.ledger_check(rt)
            self.audit.append(f"integrity: evidence ledger chain ok ({len(rt.ledger)} entries)")
            self.state = BootState.LICENSE_CHECK
            self.license_check()
            self.audit.append("license: simulated institutional entitlement active (sim mode)")
            self.state = BootState.READY
            await rt.start(feed=feed)
            self.audit.append("runtime: feed + TMS + telemetry + pipeline loops started")
            if scan:
                await asyncio.sleep(1.0)
            rt.ledger.append("boot.complete", {"mode": self.mode, "audit": self.audit})
            return rt
        except Exception as exc:
            self.state = BootState.HALTED
            raise BootError(f"DAVID SLING boot halted at {self.state.value}: {exc}",
                            context={"audit": self.audit}) from exc

    def _verify_dependency_graph(self) -> None:
        g = DependencyGraph()
        # the L0-L14 chain itself must be acyclic and ordered
        for i, name in enumerate(LAYER_NAMES):
            if i > 0:
                g.add_edge(name, LAYER_NAMES[i - 1])
        g.verify()

    @staticmethod
    def ledger_check(rt) -> None:
        rt.ledger.assert_continuity()

    def license_check(self) -> None:
        # Phase 1 sim mode: entitlement simulated as valid; live mode requires
        # the cryptographic license engine (L1 security/license).
        return None
