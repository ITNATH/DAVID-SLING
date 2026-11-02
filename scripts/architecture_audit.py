"""Architecture audit: AST scan of src/david_sling verifying
  1. zero circular imports,
  2. 15-layer unidirectional order (Li imports only Lj, j < i),
  3. technical firewall: L0-L9 domains never import L11/L12 domains
     (risk, sizing, portfolio, broker, order_management, position_management)
     except through execution_boundary (L10).
Exits 0 when clean, 1 otherwise. Run: python scripts/architecture_audit.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "david_sling"

sys.path.insert(0, str(ROOT / "src"))

from david_sling.core.dependency_graph import DependencyGraph  # noqa: E402
from david_sling.core.laws import (  # noqa: E402
    COMPOSITION_ROOT_DOMAINS,
    DOWNSTREAM_FIREWALL_DOMAINS,
    layer_of,
)

TECHNICAL_MAX_LAYER = 9
ALLOWED_BRIDGE = {"execution_boundary"}


def domain_of(module_rel: str) -> str:
    return module_rel.split("/")[0].split(".")[0] if module_rel else ""


def scan_imports() -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {}
    for path in SRC.rglob("*.py"):
        rel = path.relative_to(SRC).with_suffix("").as_posix()
        is_init = path.name == "__init__.py"
        if is_init:
            rel = rel[: -len("/__init__")] if rel.endswith("/__init__") else ""
        pkg = rel.split("/") if (is_init and rel) else rel.split("/")[:-1]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        targets: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("david_sling"):
                        t = alias.name.removeprefix("david_sling.").strip(".")
                        if t:
                            targets.add(t)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module and node.module.startswith("david_sling"):
                    t = node.module.removeprefix("david_sling.").strip(".")
                    if t:
                        targets.add(t)
                elif node.level > 0:  # relative import within package
                    base = list(pkg)
                    for _ in range(node.level - 1):
                        if base:
                            base.pop()
                    mod = "/".join(base + ([node.module] if node.module else []))
                    if mod:
                        targets.add(mod)
        edges[rel or "<root>"] = targets
    return edges


def domain_edges(edges: dict[str, set[str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for mod, targets in edges.items():
        d = domain_of(mod)
        if not d or mod == "<root>":
            continue
        out.setdefault(d, set())
        for t in targets:
            td = domain_of(t)
            if td and td != d and td != "david_sling":
                out[d].add(td)
    return out


def run_audit() -> bool:
    edges = scan_imports()
    dedges = domain_edges(edges)
    ok = True

    g = DependencyGraph()
    for importer, targets in dedges.items():
        for t in targets:
            g.add_edge(importer, t)
    cycle = g.find_cycle()
    if cycle:
        print(f"FAIL circular dependency: {' -> '.join(cycle)}")
        ok = False
    else:
        print(f"OK   zero circular dependencies across {len(dedges)} domains")

    for importer, targets in sorted(dedges.items()):
        li = layer_of(importer)
        is_composition_root = importer in COMPOSITION_ROOT_DOMAINS
        for t in sorted(targets):
            lj = layer_of(t)
            if not is_composition_root and lj > li:
                print(f"FAIL layer violation: {importer}(L{li}) imports {t}(L{lj})")
                ok = False
            if (not is_composition_root and li <= TECHNICAL_MAX_LAYER
                    and t in DOWNSTREAM_FIREWALL_DOMAINS and importer not in ALLOWED_BRIDGE):
                print(f"FAIL technical firewall: {importer}(L{li}) imports downstream {t} (L{lj}) "
                      f"- must route via L10 execution_boundary")
                ok = False
    if ok:
        print("OK   15-layer unidirectional order respected")
        print("OK   technical firewall (L0-L9 -> L11/L12) respected via L10 execution_boundary")
    print(f"\nDAVID SLING architecture audit: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run_audit() else 1)
