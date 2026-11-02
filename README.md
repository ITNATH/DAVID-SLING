# DAVID SLING

**DAVID SLING IATOS** — Institutional Algorithmic Trading Operating System.
Pure **Python** architecture (target Python 3.12+; code is 3.11-compatible).

- **Phase 1 (Milestone A — this phase):** fully running **web application** — FastAPI (ASGI) backend, real-time telemetry **WebSockets**, 30 API routers, and a responsive operator web interface (served by the Python backend itself — the mixed TS/Next.js stack was purged by design).
- **Phase 2 (Milestone B):** native desktop app in **PySide6 (Qt 6.7+)** with QSS theming and `qasync` (`apps/mission_control_gui/`).

## Architecture

15-layer unidirectional dependency chain, zero circular dependencies:

`L0 Kernel → L1 Platform → L2 Data & Parameter → L3 Perception → L4 Scenario & Thesis → L5 Fusion Brain → L6 Validation → L7 Routing → L8 Peer Engines → L9 Precision & Signal → L10 Execution Boundary Firewall → L11 Risk & Sizing → L12 Broker & Order Execution → L13 Audit & Learning → L14 Application & GUI/API`

Technical layers (L0–L9) can never touch Risk/Sizing/Broker (L11–L12) except through the **L10 Execution Boundary Firewall**.

Key doctrines: 8-stage parameter lifecycle with **zero silent drops** (`UntrackedParameterError` halts execution), hash-chained cryptographic evidence ledger, Three-Core Confluence Gatekeeper (PA 40% / Candle-CDT 35% / Indicators 25%), Universal Scenario Pool (S1–S31 + UNKNOWN/CONFLICTED/NOVEL terminal states → WAIT/NO_ROUTE/ABSTAIN), 9-layer bidirectional fusion brain (MN1→M1), 52 strategies in 8 families, 4 peer engines (A Quant Scalping 15M–30M, B Tactical Intraday 1H–4H, C Swing Structural 4H–8H, D Macro Institutional 8H–Daily), hard risk veto (1.50% session cap, `max_hold_time = null`), broker minimum-lot authority, sub-5ms rescan lifecycle.

Full root-to-leaf comprehension dossier: **`ARCHITECTURE_ANALYSIS.md`**.

## Run (Phase 1 — web version)

```bash
pip install -e . && pip install -r requirements-dev.txt
python main.py --mode sim --host 0.0.0.0 --port 8000
# open http://localhost:8000  (operator interface, DAVID SLING branding, light/dark toggle)
# API docs: http://localhost:8000/docs
```

Modes: `sim` (synthetic deterministic market feed driving the full pipeline live), `live` (broker bridge), `backtest` (replay), via `python run.py <mode>`.

## Test / lint / audit

```bash
pytest                 # unit + integration + property suites
python scripts/architecture_audit.py   # zero-layer-violation + zero-circular-dependency audit
```
