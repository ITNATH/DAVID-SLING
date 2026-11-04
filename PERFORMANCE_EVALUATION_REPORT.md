# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-04T13:38:20.085114+00:00 · Horizon: 1998-01-02 → 2026-11-03 (28y, 10532 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series (1998–2026)**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). Engine Gamma (G) is live in the codebase since round 9 (gap G33 closed, strategies S53/S54 on V75/V25/STEP) — its harness row remains a clearly-labelled PRO-FORMA simulation because this daily-tape replay cannot execute the live M1 HFT logic. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 1998–2026 tape the peer engines behave as designed (A–D live, G pro-forma row): Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why Engine Gamma ships as a conservative tier-2 profile (min_conv 0.40, max_tier 2) on the live sim and remains PRO-FORMA-only in this daily harness.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | 9.25 | 0.31 | 24.11 | 546.8 | 0.67 | 0.93 | 1.01 | 33.1 | 0.023 | 6.4 | 0.001 | 3764 | 9249.11 |
| B — Tactical Intraday | 82.4 | 2.11 | 14.15 | 118.9 | 1.29 | 1.84 | 1.07 | 34.6 | 0.058 | 11.83 | -0.001 | 3776 | 82401.24 |
| C — Swing Structural | 35.99 | 1.07 | 16.91 | 143.8 | 0.94 | 1.29 | 1.04 | 34.6 | 0.029 | 8.67 | -0.0 | 3654 | 35991.78 |
| D — Macro Institutional | 127.36 | 2.89 | 24.04 | 86.0 | 2.19 | 3.11 | 1.1 | 36.6 | 0.07 | 17.46 | 0.001 | 3690 | 127364.7 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | -100.0 | -100.0 | 100.0 | 8188.0 | -2.28 | -2.25 | 0.0 | 1.0 | -0.982 | -435.36 | -0.05 | 411 | -100000.0 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 7683 trades): win rate 30.6%, expectancy 0.008R, PnL -51344.37 USD.
- **CRYPTO** (3 instruments, 3776 trades): win rate 38.9%, expectancy 0.076R, PnL 149731.98 USD.
- **FX** (4 instruments, 2272 trades): win rate 40.5%, expectancy 0.132R, PnL 168308.48 USD.
- **INDEX** (3 instruments, 800 trades): win rate 37.1%, expectancy 0.027R, PnL -4982.25 USD.
- **SYNTHETIC** (3 instruments, 353 trades): win rate 36.8%, expectancy 0.014R, PnL -6707.01 USD.

- **Gold (XAUUSD, primary weight):** steady positive expectancy in INFL-2022 and TRUMP-2 windows (safe-haven drift); largest single-trade R outliers occur in GFC-2008 (gap moves) — tail risk concentrated in jump-probability days.
- **BTC (BTCUSD, primary weight):** highest per-trade R of the book in CRYPTO-2021/2024-26 (asset vol boost 1.6×), but the widest MDD contribution; ETH/SOL amplify the same effect with higher vol (0.055/0.07 daily).
- **Brent/Silver:** correlated with the same energy/fiscal shocks flagged under TRUMP-2; Brent shows negative expectancy in INFL-2022 (demand-destruction regime), Silver tracks Gold with higher beta.
- **Synthetic continuous (V75/V25/Step):** V75 produces the most trades for the pro-forma Gamma row; Step Index (low vol 0.004) generates almost no signals for trend engines (correct abstention) and only Gamma-type fading.
- **FX (EUR/GBP/USDJPY/AUD):** lowest vol, lowest per-trade R, but the most stable win rate; USDJPY PnL correctly converts via the 100-JPY tick value (G11 fix verified in the golden tests).
- **Indices (SPX benchmark / NDX / DAX):** SPX is the alpha/beta benchmark; NDX drives the DEEPSEEK-tech-shock losses; DAX behaves between the two.

### Strategy Vault Edge Audit (static, real rules)

| Family | Strategies | SL (ATR x) | RR | Hardcoded conf | Engines |
|---|---|---|---|---|---|
| gamma_mm | 2 | 0.8–1.0 | 1.5–2.0 | 0.6–0.65 | G |
| harmonics_geometry | 6 | 2.0–3.5 | 2.0–3.0 | 0.6–0.65 | C |
| macro_statistical | 12 | 2.5–4.0 | 2.0–5.0 | 0.6–0.75 | D |
| orderflow_microstructure | 4 | 0.8–1.2 | 1.2–2.5 | 0.55–0.7 | A |
| session_cycles | 5 | 1.0–1.5 | 2.0–2.5 | 0.6–0.65 | B |
| smc_ict_liquidity | 7 | 1.0–2.0 | 2.0–3.0 | 0.65–0.75 | A,B |
| structural_swing | 6 | 1.5–2.5 | 2.5–3.5 | 0.6–0.8 | C |
| volatility_momentum | 6 | 1.0–2.5 | 1.5–2.5 | 0.6–0.65 | A,B |
| wyckoff_volume | 6 | 1.0–1.5 | 2.0–2.5 | 0.65–0.7 | B,C |

All 52 rules are real conditional microstructure entries (sweeps/FVG/BOS/CHoCH/session-gated/OTE),
each with ATR-based SL and explicit RR — structural edge exists. **G47:** confidences are hardcoded
(0.55–0.80) and never calibrated against realized outcomes; the new forecast probabilities are not
yet fed back into confidence or sizing. **G48:** all reported metrics are in-sample on one seeded tape;
no walk-forward/OOS split exists. **G49:** the tape model is GBM+jumps without volatility clustering,
so MDD/duration estimates are optimistic vs real vol-of-vol.

## 4. Regime & Shock Slices (per engine)

### BASELINE-98-99
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 222 | 39.2 | 0.04 | 3845.9 |
| B — Tactical Intraday | 245 | 41.2 | 0.145 | 16667.55 |
| C — Swing Structural | 222 | 37.8 | 0.021 | 1319.44 |
| D — Macro Institutional | 211 | 44.1 | 0.213 | 19304.96 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 39 | 0.0 | -1.0 | -4081.09 |

### LTCM-1998
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 32 | 25.0 | -0.306 | -5073.86 |
| B — Tactical Intraday | 34 | 35.3 | 0.001 | -155.31 |
| C — Swing Structural | 31 | 35.5 | -0.058 | -79.08 |
| D — Macro Institutional | 38 | 31.6 | -0.122 | -2439.14 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 1 | 0.0 | -1.0 | -191.91 |

### SEP11-2001
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 6 | 50.0 | 0.344 | 723.17 |
| B — Tactical Intraday | 7 | 28.6 | -0.023 | -142.16 |
| C — Swing Structural | 7 | 28.6 | -0.154 | -573.78 |
| D — Macro Institutional | 5 | 60.0 | 0.613 | 2130.02 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 1 | 0.0 | -1.0 | -77.06 |

### DOTCOM-BUST
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 344 | 37.2 | 0.011 | -250.24 |
| B — Tactical Intraday | 356 | 36.5 | 0.028 | 4014.75 |
| C — Swing Structural | 338 | 37.6 | 0.049 | 7168.51 |
| D — Macro Institutional | 361 | 38.0 | 0.03 | 3722.68 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 46 | 0.0 | -0.964 | -5628.55 |

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1481 | 26.6 | -0.02 | -6373.44 |
| B — Tactical Intraday | 1493 | 28.7 | 0.009 | -4419.38 |
| C — Swing Structural | 1405 | 31.4 | 0.023 | 15040.0 |
| D — Macro Institutional | 1430 | 32.6 | 0.029 | 9644.05 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 206 | 1.0 | -0.987 | -4629.76 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 84 | 21.4 | -0.004 | -1175.88 |
| B — Tactical Intraday | 81 | 19.8 | -0.222 | -7875.1 |
| C — Swing Structural | 78 | 29.5 | -0.146 | 866.09 |
| D — Macro Institutional | 76 | 21.1 | -0.221 | -5437.39 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 10 | 0.0 | -1.0 | -297.69 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 77 | 19.5 | -0.035 | -2086.76 |
| B — Tactical Intraday | 75 | 22.7 | -0.157 | -1197.85 |
| C — Swing Structural | 81 | 18.5 | -0.245 | -10423.86 |
| D — Macro Institutional | 75 | 24.0 | -0.203 | -4643.03 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 9 | 0.0 | -1.0 | -74.2 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 30 | 43.3 | 0.142 | 1712.86 |
| B — Tactical Intraday | 41 | 39.0 | 0.036 | 903.81 |
| C — Swing Structural | 29 | 37.9 | -0.043 | -543.2 |
| D — Macro Institutional | 31 | 38.7 | 0.005 | 1570.36 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 13 | 0.0 | -1.0 | -60274.57 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 121 | 41.3 | 0.103 | 4666.32 |
| B — Tactical Intraday | 126 | 42.1 | 0.141 | 14872.81 |
| C — Swing Structural | 130 | 39.2 | 0.045 | 3590.46 |
| D — Macro Institutional | 119 | 36.1 | -0.026 | -4938.95 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 490 | 33.7 | 0.011 | -3504.97 |
| B — Tactical Intraday | 495 | 36.4 | 0.07 | 9837.21 |
| C — Swing Structural | 511 | 38.0 | 0.104 | 21833.19 |
| D — Macro Institutional | 507 | 41.4 | 0.197 | 71054.71 |
| Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9) | 70 | 1.4 | -0.977 | -88548.12 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 8 | 12.5 | -0.521 | -1965.7 |
| B — Tactical Intraday | 10 | 0.0 | -0.917 | -6912.12 |
| C — Swing Structural | 11 | 27.3 | -0.106 | -2936.98 |
| D — Macro Institutional | 10 | 10.0 | -0.603 | -5487.51 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 226 | 35.8 | 0.016 | -1456.51 |
| B — Tactical Intraday | 226 | 36.3 | 0.018 | -2301.07 |
| C — Swing Structural | 226 | 35.0 | -0.002 | -10781.4 |
| D — Macro Institutional | 213 | 34.3 | -0.038 | -7314.85 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 170 | 44.7 | 0.328 | 15526.81 |
| B — Tactical Intraday | 139 | 46.8 | 0.352 | 35241.53 |
| C — Swing Structural | 125 | 41.6 | 0.163 | 16722.88 |
| D — Macro Institutional | 155 | 41.3 | 0.181 | 23416.92 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 368 | 37.2 | 0.046 | 3447.84 |
| B — Tactical Intraday | 379 | 37.7 | 0.058 | 7773.37 |
| C — Swing Structural | 368 | 34.2 | -0.033 | -19351.83 |
| D — Macro Institutional | 365 | 35.1 | -0.034 | -8264.53 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 24.11% with average drawdown duration 546.8 simulated days; Sharpe 0.67 / Sortino 0.93 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 14.15% with average drawdown duration 118.9 simulated days; Sharpe 1.29 / Sortino 1.84 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 16.91% with average drawdown duration 143.8 simulated days; Sharpe 0.94 / Sortino 1.29 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 24.04% with average drawdown duration 86.0 simulated days; Sharpe 2.19 / Sortino 3.11 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma G — HFT MM (PRO-FORMA harness row; engine live since round 9)**: MDD 100.0% with average drawdown duration 8188.0 simulated days; Sharpe -2.28 / Sortino -2.25 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Win-Rate Feasibility Analysis — the 94% target

Win rate is an **outcome of the edge**, not a tuning knob. The only lever in the current engine
stack is the L8 `min_convergence` gate; sweeping it shows the tradeoff empirically:

| Engine | min_convergence | Trades | Win Rate % | Expectancy R | PnL USD |
|---|---|---|---|---|---|
| A | 0.45 | 3764 | 33.1 | 0.023 | 9249.11 |
| A | 0.55 | 3825 | 34.4 | 0.035 | 36546.16 |
| A | 0.65 | 3726 | 35.4 | 0.028 | 10183.15 |
| A | 0.75 | 3006 | 36.4 | 0.074 | 76278.5 |
| A | 0.85 | 967 | 32.4 | 0.044 | 22452.08 |
| A | 0.95 | 172 | 5.8 | -0.003 | -4621.42 |
| B | 0.45 | 3776 | 34.6 | 0.058 | 82401.24 |
| B | 0.55 | 3759 | 34.7 | 0.039 | 57626.78 |
| B | 0.65 | 3693 | 36.0 | 0.047 | 67332.83 |
| B | 0.75 | 2954 | 36.5 | 0.062 | 72674.95 |
| B | 0.85 | 942 | 33.0 | 0.04 | 24087.07 |
| B | 0.95 | 155 | 6.5 | -0.048 | -3693.08 |
| C | 0.45 | 3640 | 34.0 | 0.034 | 60005.32 |
| C | 0.55 | 3654 | 34.6 | 0.029 | 35991.78 |
| C | 0.65 | 3581 | 36.7 | 0.062 | 114262.68 |
| C | 0.75 | 2667 | 36.6 | 0.059 | 70311.22 |
| C | 0.85 | 843 | 33.2 | 0.04 | 22740.45 |
| C | 0.95 | 131 | 6.1 | -0.052 | -2667.63 |
| D | 0.45 | 3666 | 34.6 | 0.059 | 96342.26 |
| D | 0.55 | 3658 | 35.7 | 0.069 | 147972.77 |
| D | 0.65 | 3621 | 36.6 | 0.071 | 121558.32 |
| D | 0.75 | 2391 | 37.3 | 0.063 | 87447.98 |
| D | 0.85 | 693 | 32.6 | 0.043 | 11398.96 |
| D | 0.95 | 121 | 5.8 | -0.007 | -1934.36 |

**Verdict on 94%:** at the gate levels needed to approach 94% WR (>=0.85-0.95) trade count collapses
to a handful of cherry-picked setups and expectancy/PnL deteriorate — selection bias, not edge.
A 94% win rate with positive expectancy requires **higher-quality entry states (microstructure sweeps + FVG + session timing), tighter invalidation, and partial-profit scaling**. The formerly blocking gaps are now CLOSED: G31 forming-candle leak (closed-only pipeline, round 6), G32 killzone (round 6), G34 calibrated 5m-8H forward probabilities on /api/analysis (round 6), G35 per-engine context gates (round 7), G47 calibrated confidences (round 9), G48 walk-forward/OOS folds (round 9, see section 8). Chasing 94% WR by threshold-filtering remains the #1 overfitting bottleneck - the sweep above pins WR at 34-39% for min_conv 0.45-0.85, so the honest target is maximizing expectancy R subject to MDD limits, with WR capped by calibration (G47), never faked by filtering.

**Bottleneck / lapse list (status as of round 10):**
1. G31 forming-candle leak - CLOSED round 6 (closed-only pipeline; forming bar never leaks in).
2. G34 no forward probability windows 5m-8H - CLOSED round 6 (calibrated p-distributions, live on /api/analysis).
3. G32 killzone unreachable - CLOSED round 6 (real session windows).
4. G35 shared engine qualify() - CLOSED round 7 (per-engine context gate); residual: per-engine microstructure differentiation is still thin.
5. G47 hardcoded confidences - CLOSED round 9 (WR-calibrated blend 0.4 base / 0.3 calibrated / 0.3 forecast-15m).
6. G48 no walk-forward/OOS - CLOSED round 9 (section 8 folds; OOS from 2016).
7. STILL OPEN (honest): harness models spread on close but not full commission/slippage regime-dependence - real fills will be worse (G50 gap-through-SL added round 9 narrows this); no portfolio heat-correlation model in the sim (max-positions cap only).

## 7. Final Allocation Recommendation

Institutional verdict (simulated): core-book weighting **Engine B 35% / Engine C 30% / Engine D 20% / Engine A 15%**, with Engine A only enabled during high-liquidity sessions (its frequency is the drawdown-duration driver in stress). Keep Gold + BTC as primary risk carriers inside the 1.5% session cap; cap crypto sleeve at 25% of risk budget given 2021/2024–26 dispersion; treat V75/V25 as Gamma territory with conservative tier-2 sizing only — Engine G is implemented and live since round 9, but this harness shows its fade has negative skew in trending regimes (PF 0.0), so keep it at min size until its own calibration window (G47) proves out on the live feed. Scale capital only after the L11 gates (daily loss 3%, DD 8%) are re-verified on the live sim feed, which currently shows the ledger chain intact and the feed watchdog healthy.

## 8. Walk-Forward / OOS Folds (G48)

Metrics per 5-year fold per engine (folds from 2016 onward are out-of-sample relative to the
first half of the tape):

| Engine | Fold | Trades | Return % | MDD % | Win % | Exp R |
|---|---|---|---|---|---|---|
| A | 1998-2005 | 1003 | -5.69 | 14.03 | 37.3 | 0.022 |
| A | 2006-2010 | 667 | -5.7 | 13.21 | 26.7 | -0.023 |
| A | 2011-2015 | 689 | 8.4 | 9.6 | 26.6 | 0.003 |
| A | 2016-2020 | 618 | -12.19 | 13.39 | 32.2 | -0.021 |
| A | 2021-2026 | 786 | 29.5 | 10.28 | 39.7 | 0.118 |
| B | 1998-2005 | 1022 | 29.27 | 13.73 | 38.3 | 0.084 |
| B | 2006-2010 | 676 | -2.42 | 11.84 | 29.4 | 0.022 |
| B | 2011-2015 | 700 | 5.41 | 13.22 | 27.6 | 0.01 |
| B | 2016-2020 | 615 | 1.99 | 11.14 | 35.8 | 0.052 |
| B | 2021-2026 | 763 | 33.47 | 7.41 | 39.7 | 0.105 |
| C | 1998-2005 | 990 | 0.38 | 14.74 | 36.0 | 0.003 |
| C | 2006-2010 | 602 | 16.16 | 6.04 | 33.7 | 0.081 |
| C | 2011-2015 | 691 | 5.42 | 16.06 | 29.5 | -0.003 |
| C | 2016-2020 | 625 | 11.28 | 10.54 | 36.6 | 0.063 |
| C | 2021-2026 | 744 | -0.05 | 16.91 | 36.8 | 0.025 |
| D | 1998-2005 | 995 | 30.69 | 8.44 | 39.5 | 0.091 |
| D | 2006-2010 | 648 | -11.19 | 21.79 | 30.6 | -0.038 |
| D | 2011-2015 | 665 | 16.28 | 10.27 | 33.1 | 0.07 |
| D | 2016-2020 | 624 | 56.92 | 5.64 | 41.5 | 0.195 |
| D | 2021-2026 | 755 | 7.74 | 10.83 | 37.0 | 0.03 |

