# DAVID SLING — Round-6 Scan: Every Technical Bottleneck / Lapse Limiting a 90%+ Win Rate
Date: 2026-11-03 · Read-only scan of all 113 source files · Branch: arena/f285e712-david-sling

Win rate is gated by **entry quality, invalidation discipline, cost modeling, and adaptation**.
Each item below is a concrete, code-cited bottleneck observed in this scan. Carried items
(G31–G35 from round 4) are included for completeness and marked *(carried)*.

## A. Entry-quality bottlenecks (directly cap win rate)

| ID | Lapse / gap | Code anchor | Win-rate impact |
|---|---|---|---|
| G31 *(carried, CRITICAL)* | Forming/unclosed candle leaks into every signal matrix; pipeline re-runs on the live M1 bar | `data/market.py:110-116` (`candles()` appends `forming`), `bootstrap/runtime.py:333-355` (dedup key = `m1[-1].open_time`) | Entries taken mid-bar on noise; worst for Engine A's M5/M10/M15 triggers |
| G34 *(carried, CRITICAL)* | No calibrated forward probability distributions for 5m/15m/30m/1H/4H/8H; entries are threshold gates | `hypothesis/engine.py:23-44` (thesis + invalidation price only), `precision/engine.py:18-46` (tiers only) | No probabilistic sizing/selection — cannot rank setups by P(win); blocks any high-WR design |
| G40 *(new)* | Direction defaults to SHORT in neutral regimes | `strategies/vault.py:54-55` `_dir()`: `return "long" if (displacement_up or trend>0) else "short"` | Structural short bias when no displacement → systematic WR skew in chop |
| G35 *(carried)* | All four engines share one `qualify()`; no per-engine microstructure | `engines/supervisor.py:69-95` | Engines cannot differentiate entry quality; WR identical across A–D by construction |
| G38 *(new)* | Strategy rule exceptions silently swallowed | `strategies/vault.py:443-446` `except Exception: cand = None` | Violates the zero-silent-drop law; buggy rules silently stop firing instead of surfacing — hides the losing setups' true cause |
| G41 *(new)* | No per-symbol stacking limit pinned in config; default `max_positions_per_symbol=3` allows pyramiding | `risk/gate.py:45,94-95`; `config/risk/risk_policy.yaml` has **no** `max_positions_per_symbol` key (only session/daily/DD/8-position caps) | Up to 3 same-symbol positions from repeated M1 signals → correlated losses, worse R |

## B. Invalidation / trade-management bottlenecks

| ID | Lapse / gap | Code anchor | Win-rate impact |
|---|---|---|---|
| G37 *(new, CRITICAL)* | `HypothesisEngine.check_invalidation` is **never called** anywhere in the codebase (0 call sites) | `hypothesis/engine.py:46-54` | Theses never invalidate → entries taken against broken structure; losers run to full SL instead of scratch |
| G32 *(carried)* | `TEN_AM_CLUB` killzone unreachable (branch shadowed) | `core/session_epoch_manager.py:39-41` | NY-10AM session edge dead — a known high-WR window is not modeled |
| — | TMS SL/TP enforcement exists and is sound | `position_management/tms.py:67-98`, broker `simulated.py:122` | (positive) breakeven at +1.5 ATR converts losers to scratch — raises realized WR; keep |

## C. Cost / realism bottlenecks (inflated simulated WR)

| ID | Lapse / gap | Code anchor | Impact |
|---|---|---|---|
| G42 *(new)* | Backtest harness (`scripts/performance_evaluation.py`) uses `slippage_points=0.0`; live sim uses 0.5 pt + spread both sides | `broker/simulated.py:39,100-105,144` vs harness | Simulated WR overstated vs fills; 94%-class WR claims must be net of spread+slippage |
| G43 *(new)* | `news_active` is a random 2%-per-tick flag, not a real economic calendar | `bootstrap/runtime.py:364-369` (`rng.random() < 0.02`) | Random vetoes + `news_repricing` noise; real news windows (CPI/NFP/FOMC) not modeled |
| — | Commission model absent (only spread/swap) | `broker/simulated.py` | Real accounts pay commissions on crypto/metals CFDs |

## D. Adaptation / learning bottlenecks (WR cannot improve over time)

| ID | Lapse / gap | Code anchor | Impact |
|---|---|---|---|
| G39 *(new)* | Monitoring/learning `proposals` are **never consumed** by any decision path — only read by the API | `monitoring_learning/engine.py` proposals; no consumer outside `api/routers/audit.py` + `mission_control/server.py` | Concept-drift proposals (G16) dead-end; the system cannot adapt → WR frozen at structural level |

## E. Throughput / latency bottlenecks (signals dropped under load)

| ID | Lapse / gap | Code anchor | Impact |
|---|---|---|---|
| G44 *(new)* | Evidence ledger `fsync`s **every append**, and the pipeline appends `decision.context` every M1 bar per symbol | `evidence_ledger/ledger.py:62` (`os.fsync`), `runtime.py:507` | At 30 t/s × 3 symbols the fsync-per-bar path is the IO ceiling; under load bars queue and entries go stale |
| G45 *(new)* | Fusion latency budget **raises** `FusionError` on >500µs — the whole bar's signal is dropped with no fallback | `fusion/brain.py:91` | Under CPU pressure, signals are silently lost (bars skipped), not degraded gracefully |
| G46 *(new)* | `params.assert_no_silent_drops()` runs per bar per symbol (full audit each bar) | `runtime.py:507` | O(parameters) scan per bar — latency cost with no WR benefit at this frequency |

## F. The 94% / 90%+ win-rate verdict
A 90%+ win rate requires **P(win) per entry ≈ 0.9 with positive R**, which needs exactly the
missing pieces above: bar-close-isolated entries (G31), calibrated forward probabilities (G34),
live invalidation (G37), session/killzone correctness (G32), per-engine microstructure (G35),
cost-realistic fills (G42/G43), and a closed learning loop (G39). Today the empirical sweep
(report §6) shows WR pinned at ~35–37% regardless of gate tightening — filtering cannot lift WR;
only entry quality can. **Priority fix order for WR: G31 → G37 → G34 → G40 → G41 → G32 → G35 → G39 → G42/G43 → G44–G46.**

Gates at scan time: pytest 48/48 · ruff clean · mypy strict 113 files · architecture audit PASS.
