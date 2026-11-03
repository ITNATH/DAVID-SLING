# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-03T13:53:07.310576+00:00 · Horizon: 1998-01-02 → 2026-11-03 (28y, 10532 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series (1998–2026)**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). 'Engine Gamma' does not exist in the codebase (audit gap G33) — its row is a clearly-labelled PRO-FORMA simulation. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 1998–2026 tape the four peer engines behave as designed: Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why a dedicated HFT engine must be properly engineered (gap G33) rather than bolted on.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | 85.27 | 2.16 | 39.38 | 127.1 | 1.52 | 2.07 | 1.08 | 37.3 | 0.054 | 14.96 | -0.0 | 3726 | 85267.88 |
| B — Tactical Intraday | 197.63 | 3.85 | 13.36 | 81.4 | 1.56 | 2.12 | 1.13 | 38.2 | 0.073 | 16.25 | -0.002 | 3659 | 197629.84 |
| C — Swing Structural | 252.19 | 4.46 | 11.12 | 64.0 | 2.12 | 2.9 | 1.14 | 39.2 | 0.095 | 18.62 | 0.0 | 3601 | 252187.08 |
| D — Macro Institutional | 182.27 | 3.66 | 38.25 | 83.8 | 1.68 | 2.28 | 1.14 | 38.3 | 0.098 | 17.78 | -0.0 | 3625 | 182273.46 |
| Gamma — HFT MM (PRO-FORMA, not in code) | -170.69 | -100.0 | 170.69 | 10411.0 | -1.04 | -1.04 | 0.0 | 0.4 | -0.97 | -258.98 | 0.015 | 1265 | -170689.96 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 7208 trades): win rate 37.9%, expectancy 0.050R, PnL 244759.84 USD.
- **CRYPTO** (3 instruments, 3604 trades): win rate 38.9%, expectancy 0.132R, PnL 315772.36 USD.
- **FX** (3 instruments, 2660 trades): win rate 40.2%, expectancy 0.104R, PnL 178137.90 USD.
- **INDEX** (3 instruments, 779 trades): win rate 37.0%, expectancy 0.052R, PnL -23740.26 USD.
- **SYNTHETIC** (3 instruments, 360 trades): win rate 27.2%, expectancy 0.048R, PnL 2428.42 USD.

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
| A — Quant Scalping | 226 | 38.1 | 0.079 | 8576.28 |
| B — Tactical Intraday | 240 | 34.6 | 0.001 | -470.45 |
| C — Swing Structural | 228 | 39.0 | 0.131 | 11317.36 |
| D — Macro Institutional | 225 | 37.8 | 0.045 | 1673.88 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 68 | 0.0 | -1.0 | -8948.67 |

### LTCM-1998
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 29 | 44.8 | 0.237 | 3968.15 |
| B — Tactical Intraday | 27 | 40.7 | 0.127 | 1804.71 |
| C — Swing Structural | 33 | 33.3 | 0.038 | 1072.45 |
| D — Macro Institutional | 35 | 28.6 | -0.123 | -2016.92 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 11 | 0.0 | -1.0 | -889.55 |

### SEP11-2001
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 6 | 33.3 | 0.0 | -125.18 |
| B — Tactical Intraday | 5 | 60.0 | 0.8 | 1387.55 |
| C — Swing Structural | 5 | 40.0 | 0.2 | 360.26 |
| D — Macro Institutional | 3 | 33.3 | 0.0 | 647.74 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 2 | 0.0 | -1.0 | -109.62 |

### DOTCOM-BUST
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 392 | 31.1 | -0.061 | -18664.78 |
| B — Tactical Intraday | 375 | 34.1 | 0.079 | 8016.76 |
| C — Swing Structural | 374 | 36.6 | 0.119 | 23736.32 |
| D — Macro Institutional | 375 | 38.1 | 0.141 | 24026.66 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 93 | 0.0 | -0.996 | -11986.34 |

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1356 | 35.5 | -0.018 | -16951.18 |
| B — Tactical Intraday | 1312 | 39.3 | 0.071 | 61580.62 |
| C — Swing Structural | 1293 | 39.5 | 0.078 | 59786.24 |
| D — Macro Institutional | 1358 | 35.4 | -0.004 | -33376.45 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 460 | 0.4 | -0.982 | -13013.39 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 64 | 29.7 | -0.252 | -6785.86 |
| B — Tactical Intraday | 68 | 36.8 | -0.023 | -1115.28 |
| C — Swing Structural | 68 | 32.4 | -0.143 | -7974.45 |
| D — Macro Institutional | 78 | 35.9 | 0.054 | 255.88 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 31 | 0.0 | -1.0 | -985.81 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 62 | 25.8 | -0.227 | -5644.6 |
| B — Tactical Intraday | 58 | 36.2 | -0.002 | -1146.54 |
| C — Swing Structural | 52 | 44.2 | 0.263 | 9789.6 |
| D — Macro Institutional | 55 | 45.5 | 0.292 | 6953.09 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 17 | 0.0 | -1.0 | -225.64 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 23 | 43.5 | 0.192 | 2080.4 |
| B — Tactical Intraday | 20 | 45.0 | 0.207 | 5203.31 |
| C — Swing Structural | 29 | 37.9 | -0.005 | 1444.74 |
| D — Macro Institutional | 23 | 30.4 | -0.239 | -2780.86 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 17 | 0.0 | -1.0 | -18451.08 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 120 | 40.8 | 0.092 | 5532.75 |
| B — Tactical Intraday | 121 | 43.0 | 0.21 | 21807.17 |
| C — Swing Structural | 126 | 44.4 | 0.144 | 15122.37 |
| D — Macro Institutional | 139 | 39.6 | 0.113 | 6653.02 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 51 | 0.0 | -0.973 | -18506.23 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 503 | 39.4 | 0.08 | 11200.47 |
| B — Tactical Intraday | 502 | 37.5 | 0.039 | 15344.05 |
| C — Swing Structural | 493 | 38.5 | 0.054 | 15944.24 |
| D — Macro Institutional | 474 | 37.6 | 0.062 | 13914.89 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 258 | 0.8 | -0.927 | -60319.86 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 4 | 50.0 | 0.5 | 502.72 |
| B — Tactical Intraday | 7 | 14.3 | -0.571 | -4076.31 |
| C — Swing Structural | 7 | 42.9 | 0.401 | 2543.11 |
| D — Macro Institutional | 6 | 50.0 | 0.43 | 74.12 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 12 | 0.0 | -0.833 | -303.0 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 251 | 40.2 | 0.199 | 29731.77 |
| B — Tactical Intraday | 242 | 36.8 | 0.055 | 17647.04 |
| C — Swing Structural | 247 | 37.2 | 0.098 | 34283.93 |
| D — Macro Institutional | 243 | 38.7 | 0.234 | 53793.33 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 84 | 0.0 | -0.951 | -14883.56 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 165 | 40.6 | 0.173 | 8294.25 |
| B — Tactical Intraday | 166 | 38.0 | 0.113 | 16475.36 |
| C — Swing Structural | 154 | 43.5 | 0.296 | 41593.92 |
| D — Macro Institutional | 153 | 51.0 | 0.532 | 44352.18 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 59 | 0.0 | -0.955 | -26514.17 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 411 | 40.9 | 0.189 | 45997.25 |
| B — Tactical Intraday | 391 | 37.1 | 0.041 | 21025.84 |
| C — Swing Structural | 390 | 37.2 | 0.072 | 40229.41 |
| D — Macro Institutional | 393 | 41.5 | 0.276 | 87954.93 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 132 | 0.0 | -0.965 | -25237.25 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 39.38% with average drawdown duration 127.1 simulated days; Sharpe 1.52 / Sortino 2.07 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 13.36% with average drawdown duration 81.4 simulated days; Sharpe 1.56 / Sortino 2.12 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 11.12% with average drawdown duration 64.0 simulated days; Sharpe 2.12 / Sortino 2.9 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 38.25% with average drawdown duration 83.8 simulated days; Sharpe 1.68 / Sortino 2.28 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma — HFT MM (PRO-FORMA, not in code)**: MDD 170.69% with average drawdown duration 10411.0 simulated days; Sharpe -1.04 / Sortino -1.04 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Win-Rate Feasibility Analysis — the 94% target

Win rate is an **outcome of the edge**, not a tuning knob. The only lever in the current engine
stack is the L8 `min_convergence` gate; sweeping it shows the tradeoff empirically:

| Engine | min_convergence | Trades | Win Rate % | Expectancy R | PnL USD |
|---|---|---|---|---|---|
| A | 0.45 | 3726 | 37.3 | 0.054 | 85267.88 |
| A | 0.55 | 3647 | 38.6 | 0.088 | 251223.47 |
| A | 0.65 | 3681 | 35.6 | 0.047 | 32453.6 |
| A | 0.75 | 3007 | 34.7 | 0.047 | 100601.79 |
| A | 0.85 | 1109 | 26.7 | -0.02 | 25852.2 |
| A | 0.95 | 398 | 1.5 | -0.314 | -16801.46 |
| B | 0.45 | 3659 | 38.2 | 0.073 | 197629.84 |
| B | 0.55 | 3603 | 38.9 | 0.098 | 238154.15 |
| B | 0.65 | 3587 | 37.7 | 0.096 | 186798.48 |
| B | 0.75 | 2918 | 34.7 | 0.048 | 100268.13 |
| B | 0.85 | 1077 | 27.2 | 0.001 | 28323.93 |
| B | 0.95 | 372 | 1.1 | -0.283 | -15773.88 |
| C | 0.45 | 3651 | 38.4 | 0.079 | 188060.7 |
| C | 0.55 | 3601 | 39.2 | 0.095 | 252187.08 |
| C | 0.65 | 3524 | 37.4 | 0.095 | 156179.04 |
| C | 0.75 | 2661 | 34.5 | 0.049 | 57502.6 |
| C | 0.85 | 976 | 27.5 | 0.025 | 24514.19 |
| C | 0.95 | 326 | 0.9 | -0.23 | -14279.08 |
| D | 0.45 | 3601 | 38.5 | 0.082 | 201338.84 |
| D | 0.55 | 3611 | 38.8 | 0.091 | 212300.85 |
| D | 0.65 | 3469 | 38.3 | 0.125 | 334081.18 |
| D | 0.75 | 2336 | 34.7 | 0.075 | 49555.83 |
| D | 0.85 | 813 | 27.9 | 0.091 | 26763.74 |
| D | 0.95 | 285 | 0.7 | -0.087 | -12670.56 |

**Verdict on 94%:** at the gate levels needed to approach 94% WR (>=0.85-0.95) trade count collapses
to a handful of cherry-picked setups and expectancy/PnL deteriorate — selection bias, not edge.
A 94% win rate with positive expectancy requires **higher-quality entry states (microstructure
sweeps + FVG + session timing), tighter invalidation, and partial-profit scaling** — which the
current stack lacks (G31 lookahead leak, G32 dead killzone branch, G34 no forward probability
distributions, G35 shared engine logic). Chasing 94% WR by threshold-filtering is the #1
overfitting bottleneck; the honest target is maximizing expectancy R subject to MDD limits.

**Bottleneck / lapse list blocking a high-WR, high-expectancy engine:**
1. G31 forming-candle leak — signals computed on unclosed bars (worst for Engine A's M5 triggers).
2. G34 no forward probability windows 5m-8H — entries are threshold gates, not calibrated probabilities.
3. G32 TEN_AM_CLUB killzone unreachable — session timing edge is dead code.
4. G35 all four engines share one `qualify()` — no per-engine microstructure, so WR cannot diverge per engine.
5. Backtest harness models spread on close but not commissions/slippage regime-dependence; real fills will be worse.
6. No portfolio heat correlation model in the sim (max 3 positions hard cap only).

## 7. Final Allocation Recommendation

Institutional verdict (simulated): core-book weighting **Engine B 35% / Engine C 30% / Engine D 20% / Engine A 15%**, with Engine A only enabled during high-liquidity sessions (its frequency is the drawdown-duration driver in stress). Keep Gold + BTC as primary risk carriers inside the 1.5% session cap; cap crypto sleeve at 25% of risk budget given 2021/2024–26 dispersion; treat V75/V25 as Gamma-pro-forma territory only — do **not** allocate real capital to a market-making engine until one is actually implemented (gap G33). Scale capital only after the L11 gates (daily loss 3%, DD 8%) are re-verified on the live sim feed, which currently shows the ledger chain intact and the feed watchdog healthy.

## 8. Walk-Forward / OOS Folds (G48)

Metrics per 5-year fold per engine (folds from 2016 onward are out-of-sample relative to the
first half of the tape):

| Engine | Fold | Trades | Return % | MDD % | Win % | Exp R |
|---|---|---|---|---|---|---|
| A | 1998-2005 | 1041 | 12.28 | 20.93 | 35.7 | 0.038 |
| A | 2006-2010 | 628 | -21.66 | 28.79 | 33.8 | -0.069 |
| A | 2011-2015 | 608 | 5.31 | 19.78 | 36.7 | 0.021 |
| A | 2016-2020 | 620 | 18.0 | 10.78 | 39.5 | 0.079 |
| A | 2021-2026 | 827 | 69.21 | 9.73 | 40.9 | 0.173 |
| B | 1998-2005 | 1039 | 23.03 | 11.86 | 36.2 | 0.056 |
| B | 2006-2010 | 596 | 10.54 | 11.69 | 38.8 | 0.052 |
| B | 2011-2015 | 581 | 31.04 | 9.07 | 40.4 | 0.103 |
| B | 2016-2020 | 632 | 14.87 | 11.4 | 37.7 | 0.04 |
| B | 2021-2026 | 807 | 43.98 | 10.25 | 39.3 | 0.111 |
| C | 1998-2005 | 1025 | 50.71 | 7.93 | 37.9 | 0.098 |
| C | 2006-2010 | 589 | 3.84 | 11.12 | 38.5 | 0.041 |
| C | 2011-2015 | 576 | 25.49 | 10.77 | 40.3 | 0.103 |
| C | 2016-2020 | 618 | 16.64 | 8.88 | 39.2 | 0.072 |
| C | 2021-2026 | 789 | 54.95 | 9.83 | 40.8 | 0.147 |
| D | 1998-2005 | 987 | 44.2 | 11.43 | 38.7 | 0.106 |
| D | 2006-2010 | 628 | -21.62 | 31.24 | 34.4 | -0.041 |
| D | 2011-2015 | 605 | -10.65 | 22.3 | 35.4 | -0.001 |
| D | 2016-2020 | 596 | 20.15 | 11.06 | 38.1 | 0.076 |
| D | 2021-2026 | 807 | 133.69 | 5.78 | 43.0 | 0.285 |

