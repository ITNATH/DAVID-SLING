"""L0 core/dependency_graph - zero-circular-dependency verification (stdlib DFS).

The blueprint models this with NetworkX; the runtime invariant is identical and
dependency-free: a directed graph of domain imports must be acyclic and must
respect the 15-layer unidirectional order enforced in `laws.assert_import_allowed`.
"""
from __future__ import annotations

from .errors import ArchitectureError
from .laws import layer_of


class DependencyGraph:
    def __init__(self) -> None:
        self._edges: dict[str, set[str]] = {}

    def add_edge(self, importer: str, importee: str) -> None:
        layer_of(importer)  # validates domain names against the manifest
        layer_of(importee)
        self._edges.setdefault(importer, set()).add(importee)

    def edges(self) -> dict[str, set[str]]:
        return {k: set(v) for k, v in self._edges.items()}

    def find_cycle(self) -> list[str] | None:
        """Return a cycle (list of domains) if one exists, else None."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self._nodes()}
        stack: list[str] = []

        def dfs(node: str) -> list[str] | None:
            color[node] = GRAY
            stack.append(node)
            for nxt in sorted(self._edges.get(node, ())):
                if color[nxt] == GRAY:
                    return stack[stack.index(nxt):] + [nxt]
                if color[nxt] == WHITE:
                    cycle = dfs(nxt)
                    if cycle:
                        return cycle
            stack.pop()
            color[node] = BLACK
            return None

        for node in sorted(self._nodes()):
            if color[node] == WHITE:
                cycle = dfs(node)
                if cycle:
                    return cycle
        return None

    def _nodes(self) -> set[str]:
        nodes = set(self._edges)
        for targets in self._edges.values():
            nodes |= targets
        return nodes

    def verify(self) -> None:
        cycle = self.find_cycle()
        if cycle:
            raise ArchitectureError(f"circular dependency detected: {' -> '.join(cycle)}")
        for importer, targets in self._edges.items():
            for importee in targets:
                li, lj = layer_of(importer), layer_of(importee)
                if lj > li:
                    raise ArchitectureError(
                        f"layer violation: {importer}(L{li}) imports {importee}(L{lj})"
                    )
