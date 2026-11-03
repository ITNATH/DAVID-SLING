# DAVID SLING — Round-8: Execution-Stack Functional Tests + Consistent Failure-Moment Analysis (2026-11-03)

## 1. Functional test matrix (tests/integration/test_execution_stack_functional.py — 14 tests, all PASS)
| Component | Test | Result |
|---|---|---|
| broker_execution | submit→fill, close PnL (golden 49.9 USD net of half-spread), modify SL/TP, account_snapshot, reconcile | **ACTIVE + EFFECTIVE** |
| broker idempotency (G55) | duplicate `idempotency_key` → `ExecutionError`, no second position | **ACTIVE (fixed)** |
| order_management | OrderManager FILLED / RISK_VETOED lifecycle; same-key replay returns existing order, no duplicate | **ACTIVE + EFFECTIVE (fixed)** |
| tp_sl_management | TMS closes at SL (`stop_loss`) and TP (`take_profit`) on adverse/favorable ticks | **ACTIVE + EFFECTIVE** |
| breakeven management | at +1.5 ATR SL moves to entry, `breakeven_done=True` | **ACTIVE + EFFECTIVE** |
| trailing_logic | at +2.0R SL trails 1 ATR behind price | **was BROKEN after breakeven (G56) → FIXED** (R now measured from original risk distance `_risk_dist`) |
| partial_close | 25/50/75% closes; residual < min_lot → full close, no dust (G22) | **ACTIVE + EFFECTIVE** |
| portfolio_management | `net_exposure` per currency; `concentration_ok` 0.85-correlation veto | **ACTIVE + EFFECTIVE** |
| spike defense | ATR > 3× avg → position closed `spike_defense` | **ACTIVE + EFFECTIVE** |
| thesis failure | invalidation → `FAILURE` state + pipeline abstains that bar (G37) | **ACTIVE + EFFECTIVE** |

## 2. Consistent failure moments — observed live, then fixed
From the live evidence ledger (`storage/audit/evidence_ledger.jsonl`) BEFORE round 8:
- `circuit breaker: spread widen` ×11 — **G53**: `spread_avg` was a hardcoded constant 2.5 (runtime) / static `spread_points` (facade), so XAUUSD (30 pts) was vetoed on every signal. FIX: rolling per-symbol mean (`_spread_hist`, warm-up neutral).
- `total exposure 766% exceeds 60%` ×17 — **G51/G52**: gate compared raw NOTIONAL to equity (3-lot EURUSD = 300% → veto). FIX: margin basis (notional/leverage) + per-currency check added (was never enforced).
- `session risk cap` never bound — **G54**: `risk_amount = 0.0` placeholder. FIX: real estimate `|entry−SL| × volume × contract_size`, wired from pipeline with `fs.price`/`spec.contract_size`.
- duplicate orders on retry — **G55**: no idempotency enforcement. FIX: broker `_seen_keys` + OrderManager `_by_key` idempotent replay.
AFTER round 8 (45s live run): veto reasons = **only `max positions per symbol` ×8** — the G41 cap working as designed. Fill ratio: 6/14 signals filled vs 13/50 before, with false-positive vetoes eliminated.

## 3. Lapse/gap register update
FIXED this round: G51, G52, G53, G54, G55, G56. Still open: G47 (confidence calibration), G48 (walk-forward OOS), G49 (vol clustering in tape), G50 (gap-through-SL fill modeling), G33 (Gamma absent).

Gates: pytest **71/71** · ruff clean · mypy strict 115 files · architecture audit PASS · live: ticks advancing, chain OK, XAUUSD forecast served, zero false spread vetoes.
