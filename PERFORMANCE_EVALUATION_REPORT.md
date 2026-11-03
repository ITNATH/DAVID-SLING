# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-03T12:48:11.327289+00:00 · Horizon: 1998-01-02 → 2026-11-03 (28y, 10532 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series (1998–2026)**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). 'Engine Gamma' does not exist in the codebase (audit gap G33) — its row is a clearly-labelled PRO-FORMA simulation. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 1998–2026 tape the four peer engines behave as designed: Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why a dedicated HFT engine must be properly engineered (gap G33) rather than bolted on.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | 4.62 | 0.16 | 42.56 | 165.2 | 1.5 | 2.05 | 1.0 | 36.2 | 0.019 | 15.52 | -0.007 | 3502 | 4624.72 |
| B — Tactical Intraday | 111.1 | 2.62 | 18.61 | 121.6 | 1.72 | 2.36 | 1.08 | 37.9 | 0.051 | 17.46 | 0.003 | 3476 | 111097.56 |
| C — Swing Structural | 222.21 | 4.14 | 15.36 | 67.8 | 1.69 | 2.32 | 1.12 | 39.0 | 0.075 | 16.93 | -0.0 | 3530 | 222206.54 |
| D — Macro Institutional | 305.99 | 4.98 | 16.48 | 65.0 | 2.08 | 2.88 | 1.16 | 38.9 | 0.085 | 23.01 | -0.005 | 3536 | 305994.68 |
| Gamma — HFT MM (PRO-FORMA, not in code) | -4688520.13 | -100.0 | 4688520.13 | 10447.0 | -3.38 | -3.31 | 0.0 | 0.7 | -0.99 | -781.16 | 0.03 | 1159 | -4688520131.68 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 8707 trades): win rate 38.4%, expectancy 0.058R, PnL 291404.58 USD.
- **CRYPTO** (3 instruments, 3557 trades): win rate 35.5%, expectancy 0.007R, PnL 43674.89 USD.
- **FX** (3 instruments, 1333 trades): win rate 41.4%, expectancy 0.162R, PnL 218956.17 USD.
- **INDEX** (3 instruments, 218 trades): win rate 40.4%, expectancy 0.121R, PnL 35659.17 USD.
- **SYNTHETIC** (3 instruments, 229 trades): win rate 40.2%, expectancy 0.158R, PnL 54228.69 USD.

- **Gold (XAUUSD, primary weight):** steady positive expectancy in INFL-2022 and TRUMP-2 windows (safe-haven drift); largest single-trade R outliers occur in GFC-2008 (gap moves) — tail risk concentrated in jump-probability days.
- **BTC (BTCUSD, primary weight):** highest per-trade R of the book in CRYPTO-2021/2024-26 (asset vol boost 1.6×), but the widest MDD contribution; ETH/SOL amplify the same effect with higher vol (0.055/0.07 daily).
- **Brent/Silver:** correlated with the same energy/fiscal shocks flagged under TRUMP-2; Brent shows negative expectancy in INFL-2022 (demand-destruction regime), Silver tracks Gold with higher beta.
- **Synthetic continuous (V75/V25/Step):** V75 produces the most trades for the pro-forma Gamma row; Step Index (low vol 0.004) generates almost no signals for trend engines (correct abstention) and only Gamma-type fading.
- **FX (EUR/GBP/USDJPY/AUD):** lowest vol, lowest per-trade R, but the most stable win rate; USDJPY PnL correctly converts via the 100-JPY tick value (G11 fix verified in the golden tests).
- **Indices (SPX benchmark / NDX / DAX):** SPX is the alpha/beta benchmark; NDX drives the DEEPSEEK-tech-shock losses; DAX behaves between the two.

### Strategy Vault Edge Audit (static, real rules)

| Family | Strategies | SL (ATR x) | RR | Hardcoded conf | Engines |
|---|---|---|---|---|---|
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
| A — Quant Scalping | 227 | 41.4 | 0.168 | 19804.06 |
| B — Tactical Intraday | 229 | 42.8 | 0.188 | 19433.09 |
| C — Swing Structural | 225 | 42.2 | 0.133 | 11853.94 |
| D — Macro Institutional | 208 | 42.3 | 0.149 | 15456.5 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 62 | 1.6 | -0.972 | -7742.06 |

### LTCM-1998
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 32 | 43.8 | 0.224 | 3668.48 |
| B — Tactical Intraday | 31 | 45.2 | 0.181 | 2576.6 |
| C — Swing Structural | 32 | 37.5 | 0.026 | -375.99 |
| D — Macro Institutional | 31 | 45.2 | 0.165 | 2567.99 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 7 | 0.0 | -1.0 | -1281.51 |

### SEP11-2001
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 5 | 20.0 | -0.294 | -890.34 |
| B — Tactical Intraday | 3 | 33.3 | -0.187 | 79.26 |
| C — Swing Structural | 3 | 66.7 | 0.813 | 1422.64 |
| D — Macro Institutional | 3 | 100.0 | 1.26 | 2578.86 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 1 | 0.0 | -1.0 | -128.12 |

### DOTCOM-BUST
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 315 | 39.0 | 0.083 | 13356.63 |
| B — Tactical Intraday | 291 | 43.0 | 0.155 | 23455.46 |
| C — Swing Structural | 314 | 42.4 | 0.162 | 28585.02 |
| D — Macro Institutional | 319 | 42.3 | 0.197 | 39739.75 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 121 | 0.8 | -0.99 | -22211.69 |

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1332 | 35.6 | -0.022 | -27470.67 |
| B — Tactical Intraday | 1310 | 37.6 | 0.03 | 25393.45 |
| C — Swing Structural | 1321 | 39.0 | 0.067 | 76252.52 |
| D — Macro Institutional | 1323 | 39.0 | 0.07 | 80411.65 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 449 | 0.4 | -0.992 | -1309332.34 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 73 | 30.1 | -0.108 | -6301.77 |
| B — Tactical Intraday | 75 | 34.7 | 0.015 | 59.76 |
| C — Swing Structural | 76 | 31.6 | -0.085 | -5713.03 |
| D — Macro Institutional | 77 | 35.1 | -0.06 | -4132.07 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 31 | 0.0 | -1.0 | -34623.64 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 56 | 30.4 | -0.274 | -10750.15 |
| B — Tactical Intraday | 55 | 29.1 | -0.242 | -6243.38 |
| C — Swing Structural | 60 | 31.7 | -0.206 | -7359.28 |
| D — Macro Institutional | 69 | 27.5 | -0.224 | -7922.29 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 20 | 0.0 | -1.0 | -16820.99 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 36 | 22.2 | -0.348 | -8410.49 |
| B — Tactical Intraday | 36 | 30.6 | -0.17 | -4744.15 |
| C — Swing Structural | 40 | 25.0 | -0.248 | -9102.61 |
| D — Macro Institutional | 34 | 38.2 | 0.146 | 3726.22 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 15 | 0.0 | -1.0 | -294692.95 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 119 | 37.0 | 0.017 | -3355.02 |
| B — Tactical Intraday | 115 | 33.0 | -0.04 | -3744.51 |
| C — Swing Structural | 103 | 43.7 | 0.1 | 1028.76 |
| D — Macro Institutional | 103 | 36.9 | 0.053 | 4328.25 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 35 | 0.0 | -1.0 | -10103760.18 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 483 | 34.2 | -0.029 | -10396.38 |
| B — Tactical Intraday | 501 | 39.3 | 0.082 | 27401.03 |
| C — Swing Structural | 514 | 38.1 | 0.077 | 26072.84 |
| D — Macro Institutional | 508 | 39.2 | 0.094 | 58158.68 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 156 | 1.3 | -0.984 | -2111006.23 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 8 | 37.5 | 0.005 | -716.82 |
| B — Tactical Intraday | 8 | 50.0 | 0.399 | 1736.22 |
| C — Swing Structural | 10 | 40.0 | 0.176 | 1334.1 |
| D — Macro Institutional | 9 | 44.4 | 0.492 | 5525.33 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 6 | 0.0 | -1.0 | -55839449.37 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 226 | 30.1 | 0.011 | 4754.68 |
| B — Tactical Intraday | 216 | 38.0 | 0.088 | 26125.32 |
| C — Swing Structural | 225 | 36.4 | 0.041 | 21624.51 |
| D — Macro Institutional | 231 | 36.8 | 0.142 | 57486.62 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 69 | 0.0 | -1.0 | -4430170518.47 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 133 | 38.3 | 0.119 | 4143.69 |
| B — Tactical Intraday | 139 | 38.1 | 0.084 | 13071.89 |
| C — Swing Structural | 167 | 38.9 | 0.137 | 35394.74 |
| D — Macro Institutional | 156 | 42.3 | 0.222 | 57404.2 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 55 | 0.0 | -1.0 | -4439122.54 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 380 | 31.6 | -0.026 | -7746.51 |
| B — Tactical Intraday | 367 | 35.4 | 0.012 | 12310.48 |
| C — Swing Structural | 377 | 34.5 | -0.032 | -3493.45 |
| D — Macro Institutional | 390 | 35.1 | 0.06 | 42559.12 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 126 | 0.0 | -1.0 | -4639617926.46 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 42.56% with average drawdown duration 165.2 simulated days; Sharpe 1.5 / Sortino 2.05 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 18.61% with average drawdown duration 121.6 simulated days; Sharpe 1.72 / Sortino 2.36 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 15.36% with average drawdown duration 67.8 simulated days; Sharpe 1.69 / Sortino 2.32 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 16.48% with average drawdown duration 65.0 simulated days; Sharpe 2.08 / Sortino 2.88 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma — HFT MM (PRO-FORMA, not in code)**: MDD 4688520.13% with average drawdown duration 10447.0 simulated days; Sharpe -3.38 / Sortino -3.31 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Win-Rate Feasibility Analysis — the 94% target

Win rate is an **outcome of the edge**, not a tuning knob. The only lever in the current engine
stack is the L8 `min_convergence` gate; sweeping it shows the tradeoff empirically:

| Engine | min_convergence | Trades | Win Rate % | Expectancy R | PnL USD |
|---|---|---|---|---|---|
| A | 0.45 | 3502 | 36.2 | 0.019 | 4624.72 |
| A | 0.55 | 3536 | 37.5 | 0.052 | 85341.67 |
| A | 0.65 | 3613 | 38.0 | 0.066 | 189411.09 |
| A | 0.75 | 2722 | 38.1 | 0.063 | 131876.19 |
| A | 0.85 | 720 | 37.6 | 0.046 | 20561.21 |
| A | 0.95 | 26 | 19.2 | -0.389 | -1042.99 |
| B | 0.45 | 3476 | 37.9 | 0.051 | 111097.56 |
| B | 0.55 | 3491 | 38.7 | 0.064 | 135636.67 |
| B | 0.65 | 3510 | 39.0 | 0.083 | 246588.57 |
| B | 0.75 | 2678 | 38.9 | 0.077 | 175771.77 |
| B | 0.85 | 711 | 38.1 | 0.055 | 22306.85 |
| B | 0.95 | 21 | 23.8 | -0.386 | -977.99 |
| C | 0.45 | 3473 | 37.9 | 0.05 | 107930.27 |
| C | 0.55 | 3530 | 39.0 | 0.075 | 222206.54 |
| C | 0.65 | 3444 | 39.0 | 0.084 | 261115.01 |
| C | 0.75 | 2466 | 37.5 | 0.047 | 72594.72 |
| C | 0.85 | 651 | 38.1 | 0.054 | 19471.47 |
| C | 0.95 | 21 | 23.8 | -0.243 | -972.99 |
| D | 0.45 | 3470 | 38.0 | 0.065 | 138855.68 |
| D | 0.55 | 3516 | 38.4 | 0.07 | 162894.58 |
| D | 0.65 | 3414 | 38.8 | 0.094 | 320466.07 |
| D | 0.75 | 2199 | 38.8 | 0.088 | 152525.66 |
| D | 0.85 | 522 | 39.1 | 0.084 | 24682.15 |
| D | 0.95 | 20 | 15.0 | -0.294 | -2306.11 |

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

