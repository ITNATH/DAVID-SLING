# DAVID SLING — Round-7 Audit: Real Strategy Edge + Re-Verification of Round-6 Fixes (2026-11-03)

Read-only verification pass. Question under test: **does the strategy layer carry real edge,
and are the round-6 bottleneck fixes actually in the code?**

## 1. Round-6 fixes verified in code (empirical anchors)
| Gap | Verification anchor | Status |
|---|---|---|
| G31 | `runtime.py` uses `candles(..., include_forming=False)` in `candles_by_tf` + pipeline dedup (2 sites); `market.py:110-117` `candles(include_forming=...)` | PASS |
| G32 | `session_epoch_manager.py`: `if 14 <= h < 15: TEN_AM_CLUB` now precedes the 13–16 overlap branch | PASS |
| G34 | `intelligence/forecast.py` exists; `/api/analysis/{symbol}` returns `forecast` (live-verified: 5m–8H map) | PASS |
| G35 | `supervisor.qualify` gates each engine on its own `context_tfs` via `fusion.layers` | PASS |
| G37 | `runtime.py` calls `hypothesis.check_invalidation(symbol, fs.price)` in `run_symbol`; engine marks FAILURE | PASS |
| G39 | `runtime.py:540` consumes `monitoring.active_drift_strategies()` and abstains drifted strategies | PASS |
| G40 | `vault._dir` returns `None` on neutral; `evaluate` returns [] | PASS |
| G41 | `config/risk/risk_policy.yaml: max_positions_per_symbol: 1` | PASS |
| G42/G43 | harness `slippage_points=0.5`; `data/news_calendar.py` (NFP/CPI/FOMC + config dates) drives `_news_loop` | PASS |
| G44–G46 | throttled per-bar appends/audit (1 per 5s), `DAVID_SLING_LEDGER_FSYNC` switch, fusion FusionError → neutral fallback | PASS |

## 2. Strategy edge audit (the core test)
- **52/52 rules are real conditional entries** — sweeps, FVG, BOS/CHoCH, CISD/breaker blocks,
  session-gated Judas (S06), OTE/golden-zone (S18, G1), each with ATR-based SL and explicit RR.
  Per-family map (SL-ATR / RR / engines) is in `PERFORMANCE_EVALUATION_REPORT.md` §3b:
  orderflow_microstructure and smc_ict_liquidity → Engine A; session_cycles/wyckoff → B;
  structural_swing/harmonics → C; macro_statistical (12 rules) → D.
- **Verdict: structural edge EXISTS at the rule level.** What limits realized edge is calibration,
  not rule existence — see new gaps below.

## 3. New lapses / gaps observed (round 7)
| ID | Lapse | Anchor | Severity |
|---|---|---|---|
| G47 | Strategy confidences hardcoded (0.55–0.80), never calibrated to realized outcomes; forecast probabilities (G34) not fed back into confidence or sizing | `vault.py` `_mk(..., conf=...)` per rule; report §3b | HIGH — directly caps achievable WR |
| G48 | No walk-forward / out-of-sample split — every reported metric is in-sample on one seeded tape (seed fixed); determinism is good for reproducibility but edge claims are unverified OOS | `scripts/performance_evaluation.py` (single seed, single tape) | HIGH |
| G49 | Tape model = GBM + regime jumps, no volatility clustering / autocorrelation → MDD & avg-DD-duration estimates optimistic vs real vol-of-vol | `scripts/performance_evaluation.py` `gen_tape` | MEDIUM |
| G50 | Sim fills assume continuous liquidity; no partial-fill / gap-through-SL modeling (SL assumed exact) | `broker/simulated.py` `_close` at SL price | MEDIUM — live fills worse at SL in gaps |
| G33 | Engine Gamma / HFT-MM still absent (pro-forma negative skew) | `engines/` | HIGH (roadmap) |

## 4. Side-by-Side Diagnostic Matrix (updated statuses)
| Component | Round-4 status | Round-7 status |
|---|---|---|
| MTF state memory (10 TFs) | PASS | PASS |
| Bar-close isolation (G31) | FAIL | **PASS** (closed-only pipeline series) |
| Session clocks (G32) | CONDITIONAL | **PASS** (TEN_AM_CLUB reachable) |
| Predictive horizons 5m–8H (G34) | CRITICAL FAIL | **PASS** (calibrated probs exist; calibration unverified → G47) |
| Engine peer logic (G35) | CONDITIONAL | **PASS** (per-engine context gate) |
| Thesis invalidation (G37) | CRITICAL FAIL (dead code) | **PASS** (wired, FAILURE state) |
| Strategy edge | untested | **PASS structurally; calibration gap G47** |
| Costs (G42/G43/G50) | overstated | PASS in harness (slippage 0.5pt); gap-through-SL still unmodeled (G50) |
| OOS validation | absent | **FAIL — G48** (no walk-forward) |
| Engine Gamma | absent (G33) | still absent (roadmap) |

## 5. Verdict
Whole bot: **PASS with conditions** — all round-6 CRITICALs closed and code-verified. The binding
constraint on a 90%+ win rate is no longer infrastructure; it is **strategy calibration (G47)**
and **out-of-sample proof (G48)**. Next highest-value work: (1) calibrate rule confidences from
`MonitoringEngine` outcomes and feed `forecast` probabilities into sizing; (2) add walk-forward
splits to the evaluation harness; (3) model gap-through-SL in the broker sim.

Gates: pytest 57/57 · ruff clean · mypy strict 115 files · architecture audit PASS.
