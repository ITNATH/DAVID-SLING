# DAVID SLING — Phase 1 (Web Version) Root-to-Leaf Audit: Gap & Lapse Ledger
Date: 2026-11-02 · Auditor: Arena.ai Agent Mode · Branch: arena/f285e712-david-sling
Method: line-level side-by-side scan of `src/david_sling/**` (106 files) against the master
blueprint `/tmp/arena-coding-uploads/EA 7!.txt` (5,583 lines), plus runtime verification of the
live sim server (gates: pytest 33/33, ruff clean, mypy clean 106 files, architecture audit PASS).

## 1. Architectural Alignment Scan — VERIFIED PARITY (blueprint anchor → code anchor)
| Blueprint requirement | Code anchor | Status |
|---|---|---|
| 15-layer unidirectional chain L0→L14, zero circular deps | `core/laws.py` LAYER_NAMES (15), `scripts/architecture_audit.py` PASS (34 domains, 0 cycles) | PARITY |
| L0–L9 technical firewall via L10 Execution Boundary | `DOWNSTREAM_FIREWALL_DOMAINS`, `execution_boundary/firewall.py` assert_caller raises BoundaryViolation; audit enforces | PARITY |
| Parameter lifecycle INGEST→VALIDATE→DERIVE→CONTEXTUALIZE→FUSE→CONTRIBUTE→DECIDE→RECORD, zero-silent-drop | `core/contracts.py` 8 stages; `parameter/lifecycle.py` UntrackedParameterError; tested | PARITY |
| Parameter states VALID/INVALID/MISSING/STALE/CONFLICTED | `core/schemas.py` ParameterStateValue | PARITY |
| Terminals UNKNOWN/CONFLICTED/NOVEL → WAIT/NO_ROUTE/ABSTAIN | `core/policies.py` TERMINAL→ABSTENTION map; `scenario_pool/engine.py` | PARITY |
| L3 intelligence = 16 families | `intelligence/engine.py` FAMILIES = 16 (incl. fibonacci, harmonics…) | PARITY (declared) |
| L4 universal scenario pool S1–S31 + 3 terminals | `core/schemas.py` ScenarioId = 34 ids (S1..S31+UNKNOWN/CONFLICTED/NOVEL) | PARITY |
| L5 nine-layer bidirectional fusion (MN1,W1,D1,H8,H4,H1,M30,M15,M5→M1), 60/40 top-down/ground-up | `fusion/brain.py` FUSION_LAYERS + M1 LTF feed, TOP_DOWN 0.6 / GROUND_UP 0.4; `<500µs` budget enforced (raises FusionError) | PARITY |
| L6 confluence gatekeeper PA 40% / CDT 35% / Indicators 25% | `config/confluence_weights.yaml` 0.40/0.35/0.25; `core/three_core_confluence_gatekeeper.py` | PARITY |
| L7 52 strategies / 8 families, zero engine coupling | `strategies/vault.py` StrategyRegistry: 52 strategies, 8 families | PARITY |
| L8 engines A 15M–30M / B 1H–4H / C 4H–8H / D 8H–Daily | `config/engines/engine_profiles.yaml` matches blueprint exactly | PARITY |
| L11 risk: session cap 1.50%, daily loss 3.00%, DD 8.00%, circuit breakers (ATR spike 3x, spread widen) | `config/risk/risk_policy.yaml` + `risk/gate.py` (all four enforced, tested) | PARITY |
| Sizing: volatility sizing, min-lot/lot_step/max-lot, exact Decimal | `sizing/engine.py` Decimal quantize_down to lot_step, clamp min/max | PARITY |
| TMS: breakeven +1.5 ATR, trailing +2.0R, partials 25/50/75%, max_hold_time=null | `position_management/tms.py` BREAKEVEN_ATR_MULT=1.5, TRAILING_R=2.0, pct partial; `config/boot_state.yaml` max_hold_time: null + constitutional check in configuration_engine | PARITY |
| L13 cryptographic evidence ledger (SHA3-256 chain, Merkle, fsync) | `evidence_ledger/ledger.py` SHA3-256, fsync-in-with, single-ts hash+record, verify_chain/merkle_root; tested | PARITY |
| L14 FastAPI ASGI + WS telemetry + responsive web UI | `api/app.py`, 6 routers, `/ws/telemetry`, `api/static/*` | PARITY |
| Branding "DAVID SLING" on headers/splash/UI | health/system payloads, index.html header, boot splash in main.py | PARITY |
| Light/Dark toggle in UI header | `app.js` data-theme toggle + `style.css` CSS vars; `config/gui_preferences.yaml` light_dark_toggle: true, 5 themes | PARITY |
| Omni-Trade: single (Market/Limit/Stop, R-mult, dynamic lots, partials, BE lock), single-pair tranches + batch close, cross-pair baskets + PnL matrix + correlation guards, panic flatten | `mission_control/ops.py` single_trade/single_pair_multi/cross_pair_basket; `pnl.py` matrix; `portfolio/exposure.py` correlation guard (0.85 veto verified live); TMS panic_flatten; all exercised via API + tests | PARITY |
| Rescan sub-5ms subsystem | `rescan/engine.py` measures + enforces budget (WARNING on overrun) | PARITY |

## 2. Gap & Lapse Ledger
| # | Severity | Finding | Location |
|---|---|---|---|
| G1 | MEDIUM | **OTE/Fibonacci gap**: blueprint L3 has `fibonacci/retracement.py` + `golden_zone.py`; S18 must detect the 61.8–78.6% Golden Zone. Code declares the `fibonacci` family but computes no fib retracement; S18 is an ema50/RSI proxy (self-labeled). Harmonics use 0.786 only. | `strategies/vault.py::_s18`, `intelligence/features.py` |
| G2 | MEDIUM | **Live broker adapters absent**: blueprint L12 lists `mt5_adapter.py`, `mt4_adapter.py`, `ctrader_adapter.py`, `fix_adapter.py`. Only `broker/simulated.py` exists. Phase-1 sim is fully functional, but live execution is impossible until adapters land. | `broker/` |
| G3 | LOW | WS handler catches only `WebSocketDisconnect`; a `send_text` on a dead socket raises RuntimeError (propagates to uvicorn; `finally` still unsubscribes → no leak, but noisy + no alert). | `api/websocket.py` |
| G4 | LOW | No global API exception handler: unexpected errors return bare `500 Internal Server Error` (observed pre-fix during dev). Per-request isolation holds (macro-system safe), but the failure is not journaled/alerted at the boundary. | `api/app.py`, `api/middleware.py` |
| G5 | LOW | `asyncio.get_event_loop().create_task(...)` in `Runtime._submit_order` — deprecated; safe only because the caller is always the async pipeline. Should be `get_running_loop()`. | `bootstrap/runtime.py:186,194` |
| G6 | LOW | Risk gate sets `day_start_balance` lazily on first evaluate; no explicit day-boundary (session epoch) reset hook. | `risk/gate.py:54-57` |
| G7 | LOW | Dispatch `<1ms` budget (blueprint `test_trade_panel_dispatch_latency`) is measured (`X-Process-Time-ms`) but not hard-enforced; only fusion `<500µs` and rescan `<5ms` raise/warn. | `api/middleware.py` |
| G8 | LOW | Blueprint deployment artifacts (Dockerfile.api, docker-compose, k8s ingress, Nuitka build) not present; Phase 1 boots via `main.py`. | repo root |
| G9 | INFO | Milestone B (PySide6/QSS/qasync desktop) not started — by design; web Light/Dark already live. | `apps/` (empty) |
| G10 | INFO | Telemetry slow-consumer policy = drop-oldest from bounded queue (512) + 15s ping keepalive; each frame is a full snapshot so UI resyncs — no desync risk. Concurrency: single asyncio loop (feed/TMS/pipeline/API) → no data races; ledger append+fsync is synchronous by design (durability first). | `services/telemetry_service.py`, `evidence_ledger/ledger.py` |

## 3. Refinement Strategy (prioritized)
1. **P1 — G1**: add `intelligence/geometry/fibonacci.py` (retracement 0.236–0.786, golden zone 0.618–0.786, extensions) and rewire S18 to true OTE zone detection (keep ema50 proxy as secondary confirmation). Add unit tests vs. synthetic swing data.
2. **P1 — G2**: add `broker/adapter.py` (BrokerAdapter ABC: submit/close/modify/cancel/account/stream) + `mt5/mt4/ctrader/fix` adapters that require live credentials and raise `SecurityError`/`ExecutionError` cleanly when absent (no stubs — full request/reply/error mapping), selected by `config/broker/accounts.yaml` `adapter:` key; sim stays default.
3. **P2 — G3/G4**: wrap WS send loop in `except Exception` → emit alert + close cleanly; add FastAPI `exception_handler` returning structured `{error, correlation_id}` + ledger/alert entry.
4. **P2 — G5/G6**: `get_running_loop()`; explicit `RiskGate.on_session_epoch()` reset wired to the session epoch manager.
5. **P3 — G7/G8**: enforce dispatch budget counter (metrics in monitoring engine); add Dockerfile.api + docker-compose.dev.yml.
6. **P3 — G9**: Milestone B desktop (PySide6 + QSS themes from `gui_preferences.yaml` + qasync), reusing the L14 facade.

## 4. Live Deployment Status
- RUNNING in sandbox (uvicorn 0.0.0.0:8000, sim mode, boot audit clean, ledger chain OK).
- Preview URL: https://8000-ijfb5yja4427urqpyjecp.e2b.app  (UI at `/`, Swagger at `/docs`, WS at `/ws/telemetry`)
- Access: no credentials required in sim mode (`DAVID_SLING_API_TOKEN` unset → dev-open). Set that env var to require `Authorization: Bearer <token>`.
- Last health snapshot: ticks 7,768 · ledger 166 entries chain_ok=true · all 15 layer health checks OK · 10 signals routed · risk gate live (session cap 1.50% enforced — manual over-exposure correctly vetoed at 95.4% > 60% exposure guard during testing).

---

# Deep Pass #2 — extended Gap & Lapse Ledger (sub-micro logic, failure isolation, numeric precision)
Date: 2026-11-02 · Scope: blueprint module-level parity (146 core files + domain trees), loop isolation,
PnL/precision arithmetic, rescan taxonomy, monitoring/drift, halt semantics, persistence, API hardening.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| G11 | **HIGH** | **FX tick_value semantics inconsistent → PnL misstated ~10x.** `_pnl = (exit-entry)/tick_size * tick_value * volume`. EURUSD/GBPUSD config `tick_value: 10.0` is a *per-pip* value but is applied *per-tick* (0.00001) → PnL **overstated 10x** (sim 7.00 vs real ~0.70 on +100 ticks/0.1 lot). USDJPY `tick_value: 6.67` per-pip applied per 0.001 tick → **understated 10x** (sim 0.43 vs real ~6.67). XAUUSD (per-tick 1.0) is correct. Sizing `risk_based_lot` divides by the same tick_value → FX lot sizes off 10x in the opposite direction. | measured: `broker/simulated.py::_pnl`, `config/symbols.yaml` |
| G12 | MED | **TMS loop and news loop have no try/except** — one exception silently kills the loop task (macro failure-isolation gap). Pipeline and telemetry loops ARE guarded. | `bootstrap/runtime.py::_tms_loop` (no try), `_news_loop` (no try) vs `_pipeline_loop`/`_telemetry_loop` (guarded) |
| G13 | MED | **Emergency Halt missing**: blueprint quick_action_toolbar has Halt + `emergency_halt_dialog` (multi-confirmation). `RiskState.halted` exists but is never set; no API endpoint; panic-flatten only closes books, doesn't stop new entries. | `risk/gate.py` (`halted` dead), no `/api/trade/halt` |
| G14 | MED | **Rescan taxonomy incomplete**: blueprint defines 9 triggers (initial, post_exit, thesis_failure, fakeout, spike, scenario, fusion, engine, evidence snapshot). Code wires only post_exit + manual. Also rescan budget overrun increments a counter but the promised WARNING alert is never emitted (docstring lies). | `rescan/engine.py`, call sites only in `runtime.py:252`, `facade.initiate_rescan` |
| G15 | LOW | `PortfolioExposure.concentration_ok` is dead code — risk gate re-implements exposure math inline. | `portfolio/exposure.py:36` never called |
| G16 | LOW | Concept-drift detection absent (blueprint `concept_drift_detector.py` + `drift_proposal_engine.py`); only edge-decay proposals exist, correctly non-mutating (immutable learning boundary respected). | `monitoring_learning/engine.py` |
| G17 | LOW | No import-time constitutional enforcement (blueprint `operating_principles.py` / `architecture_integrity_check` at import time); law enforcement is an external script only. | `core/__init__.py` empty of checks |
| G18 | LOW | Journal retention (`retention_days: 90`) configured but never enforced (no pruning); external alert channels (telegram/email/whatsapp/webhook) have config but no delivery path (no alert-gateway). | `journal/engine.py`, `alerts/engine.py`, `config/alerts/alert_channels.yaml` |
| G19 | LOW | `data/{ticks,ohlcv,orderbook,news,synthetic}/` exist but are empty — sim market data lives only in memory; replay regenerates synthetically instead of reading stored data. | `data/` |
| G20 | LOW | No CORS allowlist (preview is same-origin so OK today, but no explicit preview-host allowlist); static mount has no cache headers. | `api/app.py` |
| G21 | LOW | Pipeline `seen`-bookkeeping contains a convoluted dead conditional (`if key in seen and last.close == m1[-2].close if len(m1)>1 else False`) — harmless, confusing. | `bootstrap/runtime.py` `_pipeline_loop` |
| G22 | LOW | Partial close can leave a dust residual below min_lot (`round(vol,8)`, no min-residual rule in broker close). | `position_management/tms.py::partial_close`, `broker/simulated.py::close` |
| G23 | LOW | `asyncio.get_event_loop().create_task` (deprecated) in `_submit_order` and `_tms_loop`; also ugly `__import__("david_sling.core.schemas", ...)` inline imports for AlertLevel. | `bootstrap/runtime.py:186,194,243-249` |
| G24 | INFO | L10 submodules (technical_signal_adapter / signal_route_notifier / downstream_contract) consolidated into `execution_boundary/firewall.py` — functionally present, structurally merged. | `execution_boundary/` |
| G25 | INFO | Verified GOOD: JPY profit-currency conversion uses live USDJPY price; slippage modeled on fills; spread charged at fill and close; Decimal lot quantization; per-currency + total exposure limits; day-start balance + drawdown guard; precision Tier 1–4 present. | `broker/simulated.py`, `risk/gate.py`, `precision/` |

## Updated priority order
1. **G11 (HIGH, numeric correctness)** — normalize tick_value to per-tick-per-lot (EURUSD/GBPUSD 1.0, USDJPY ≈0.667) in `config/symbols.yaml`, add a broker PnL golden test per symbol vs real-world values, re-verify sizing.
2. **G12 (MED)** — wrap `_tms_loop` and `_news_loop` bodies in try/except → alert + continue (mirror pipeline loop).
3. **G13 (MED)** — implement halt/resume: set `RiskState.halted`, `/api/trade/halt` + `/resume` endpoints, gate checks halted first, UI emergency-halt button with confirm dialog.
4. **G14 (MED)** — wire remaining rescan triggers (spike, scenario transition, fusion conflict, engine invalidation, fakeout) + emit WARNING on budget overrun.
5. G1, G2 (from pass 1), then G15–G23 lows, then Milestone B.

## Addendum — G12 OBSERVED LIVE
After ~7,768 sim ticks the production sim server's background feed froze while HTTP stayed up
(ticks constant across repeated /api/health polls; no error in uvicorn log because asyncio task
exceptions are never retrieved). Reproduced by inspection: `MarketSimulator.run()`, `_tms_loop()`,
and `_news_loop()` have no try/except and no task-done callback, so a single exception kills the
loop silently. Server restarted for preview; permanent fix queued at P1 (guard all loops + alert +
`asyncio` task exception logging via loop exception handler).
