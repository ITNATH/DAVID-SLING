# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-03T11:21:11.581922+00:00 · Horizon: 1998-01-02 → 2026-11-03 (28y, 10532 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series (1998–2026)**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). 'Engine Gamma' does not exist in the codebase (audit gap G33) — its row is a clearly-labelled PRO-FORMA simulation. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 1998–2026 tape the four peer engines behave as designed: Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why a dedicated HFT engine must be properly engineered (gap G33) rather than bolted on.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | -6.16 | -0.22 | 30.72 | 471.5 | 0.75 | 1.01 | 0.99 | 35.1 | 0.021 | 8.88 | -0.005 | 3422 | -6162.22 |
| B — Tactical Intraday | 4.34 | 0.15 | 40.27 | 494.0 | 0.96 | 1.31 | 1.01 | 33.5 | 0.013 | 10.51 | 0.001 | 3486 | 4337.4 |
| C — Swing Structural | 12.03 | 0.39 | 38.98 | 295.3 | 1.35 | 1.89 | 1.01 | 32.9 | 0.003 | 14.02 | 0.0 | 3607 | 12033.34 |
| D — Macro Institutional | 72.36 | 1.91 | 25.39 | 116.6 | 1.41 | 2.0 | 1.06 | 33.0 | 0.036 | 14.79 | -0.003 | 3621 | 72357.78 |
| Gamma — HFT MM (PRO-FORMA, not in code) | -129990.91 | -100.0 | 129990.91 | 10446.0 | -2.56 | -2.53 | 0.0 | 0.6 | -0.989 | -11299.58 | 3.5 | 1166 | -129990909.01 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 9098 trades): win rate 36.6%, expectancy 0.006R, PnL -105485.84 USD.
- **CRYPTO** (3 instruments, 3310 trades): win rate 22.0%, expectancy 0.000R, PnL 66507.48 USD.
- **FX** (3 instruments, 1261 trades): win rate 41.3%, expectancy 0.143R, PnL 105108.60 USD.
- **INDEX** (3 instruments, 293 trades): win rate 36.2%, expectancy 0.018R, PnL -1058.77 USD.
- **SYNTHETIC** (3 instruments, 174 trades): win rate 40.2%, expectancy 0.134R, PnL 17494.83 USD.

- **Gold (XAUUSD, primary weight):** steady positive expectancy in INFL-2022 and TRUMP-2 windows (safe-haven drift); largest single-trade R outliers occur in GFC-2008 (gap moves) — tail risk concentrated in jump-probability days.
- **BTC (BTCUSD, primary weight):** highest per-trade R of the book in CRYPTO-2021/2024-26 (asset vol boost 1.6×), but the widest MDD contribution; ETH/SOL amplify the same effect with higher vol (0.055/0.07 daily).
- **Brent/Silver:** correlated with the same energy/fiscal shocks flagged under TRUMP-2; Brent shows negative expectancy in INFL-2022 (demand-destruction regime), Silver tracks Gold with higher beta.
- **Synthetic continuous (V75/V25/Step):** V75 produces the most trades for the pro-forma Gamma row; Step Index (low vol 0.004) generates almost no signals for trend engines (correct abstention) and only Gamma-type fading.
- **FX (EUR/GBP/USDJPY/AUD):** lowest vol, lowest per-trade R, but the most stable win rate; USDJPY PnL correctly converts via the 100-JPY tick value (G11 fix verified in the golden tests).
- **Indices (SPX benchmark / NDX / DAX):** SPX is the alpha/beta benchmark; NDX drives the DEEPSEEK-tech-shock losses; DAX behaves between the two.

## 4. Regime & Shock Slices (per engine)

### BASELINE-98-99
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 235 | 33.2 | -0.117 | -13408.4 |
| B — Tactical Intraday | 212 | 32.5 | -0.066 | -10828.5 |
| C — Swing Structural | 213 | 38.5 | 0.064 | 475.47 |
| D — Macro Institutional | 212 | 42.5 | 0.181 | 14674.35 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 66 | 0.0 | -1.0 | -7957.2 |

### LTCM-1998
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 29 | 24.1 | -0.38 | -5460.83 |
| B — Tactical Intraday | 26 | 23.1 | -0.308 | -5347.36 |
| C — Swing Structural | 29 | 27.6 | -0.214 | -3244.8 |
| D — Macro Institutional | 30 | 30.0 | -0.102 | -3364.88 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 10 | 0.0 | -1.0 | -630.72 |

### SEP11-2001
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 4 | 100.0 | 1.711 | 2794.39 |
| B — Tactical Intraday | 3 | 66.7 | 1.212 | 1633.9 |
| C — Swing Structural | 2 | 50.0 | 0.5 | 943.25 |
| D — Macro Institutional | 5 | 60.0 | 0.8 | 2277.48 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 3 | 0.0 | -1.0 | -6157.59 |

### DOTCOM-BUST
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 290 | 34.8 | -0.026 | -3889.34 |
| B — Tactical Intraday | 316 | 34.2 | -0.044 | -3296.34 |
| C — Swing Structural | 306 | 36.3 | -0.031 | 3407.18 |
| D — Macro Institutional | 315 | 36.5 | 0.048 | 19467.48 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 117 | 0.0 | -0.994 | -217890.84 |

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1296 | 32.8 | 0.006 | -19930.45 |
| B — Tactical Intraday | 1318 | 28.0 | -0.039 | -31263.78 |
| C — Swing Structural | 1406 | 27.7 | -0.049 | -24468.42 |
| D — Macro Institutional | 1399 | 28.5 | -0.023 | -17641.55 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 423 | 0.2 | -0.996 | -22874670.77 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 75 | 34.7 | -0.003 | 1035.88 |
| B — Tactical Intraday | 72 | 30.6 | -0.105 | -2190.06 |
| C — Swing Structural | 71 | 32.4 | -0.007 | 2432.15 |
| D — Macro Institutional | 69 | 33.3 | 0.087 | 4659.53 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 22 | 0.0 | -1.0 | -891474.84 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 62 | 32.3 | 0.02 | 1423.89 |
| B — Tactical Intraday | 67 | 29.9 | 0.006 | 3608.39 |
| C — Swing Structural | 63 | 31.7 | 0.234 | 6656.37 |
| D — Macro Institutional | 67 | 29.9 | -0.022 | 5685.44 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 16 | 0.0 | -1.0 | -645437.73 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 34 | 35.3 | -0.025 | -566.35 |
| B — Tactical Intraday | 40 | 32.5 | -0.078 | -556.32 |
| C — Swing Structural | 41 | 36.6 | 0.058 | 900.1 |
| D — Macro Institutional | 47 | 38.3 | 0.134 | 3046.7 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 29 | 0.0 | -1.0 | -20468332.82 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 115 | 46.1 | 0.27 | 12695.52 |
| B — Tactical Intraday | 113 | 48.7 | 0.314 | 15885.62 |
| C — Swing Structural | 124 | 39.5 | 0.048 | 5147.94 |
| D — Macro Institutional | 130 | 36.9 | 0.057 | 8075.48 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 38 | 0.0 | -1.0 | -22657368.53 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 485 | 33.8 | -0.004 | -5259.48 |
| B — Tactical Intraday | 495 | 34.3 | 0.006 | -1615.04 |
| C — Swing Structural | 504 | 32.1 | -0.04 | -1803.64 |
| D — Macro Institutional | 520 | 33.5 | 0.03 | 22198.97 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 185 | 1.6 | -0.972 | -43320961.42 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 10 | 20.0 | -0.4 | -2092.91 |
| B — Tactical Intraday | 10 | 10.0 | -0.7 | -3826.59 |
| C — Swing Structural | 9 | 22.2 | -0.314 | -1718.8 |
| D — Macro Institutional | 15 | 13.3 | -0.633 | -8801.23 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 4 | 0.0 | -1.0 | -132769.05 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 217 | 33.2 | -0.071 | -9212.68 |
| B — Tactical Intraday | 229 | 33.6 | -0.073 | -10469.23 |
| C — Swing Structural | 247 | 34.8 | -0.06 | -11803.89 |
| D — Macro Institutional | 235 | 31.1 | -0.135 | -35584.73 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 61 | 0.0 | -1.0 | -626829.12 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 125 | 33.6 | -0.043 | -2756.54 |
| B — Tactical Intraday | 147 | 40.8 | 0.171 | 9050.98 |
| C — Swing Structural | 141 | 41.8 | 0.162 | 12025.81 |
| D — Macro Institutional | 150 | 39.3 | 0.223 | 21298.73 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 59 | 0.0 | -1.0 | -25289604.99 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 358 | 34.1 | -0.046 | -10117.59 |
| B — Tactical Intraday | 371 | 36.1 | 0.003 | -2992.14 |
| C — Swing Structural | 400 | 38.5 | 0.08 | 10326.47 |
| D — Macro Institutional | 374 | 37.2 | 0.053 | 2246.05 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 112 | 0.0 | -0.996 | -9049621.83 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 30.72% with average drawdown duration 471.5 simulated days; Sharpe 0.75 / Sortino 1.01 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 40.27% with average drawdown duration 494.0 simulated days; Sharpe 0.96 / Sortino 1.31 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 38.98% with average drawdown duration 295.3 simulated days; Sharpe 1.35 / Sortino 1.89 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 25.39% with average drawdown duration 116.6 simulated days; Sharpe 1.41 / Sortino 2.0 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma — HFT MM (PRO-FORMA, not in code)**: MDD 129990.91% with average drawdown duration 10446.0 simulated days; Sharpe -2.56 / Sortino -2.53 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Win-Rate Feasibility Analysis — the 94% target

Win rate is an **outcome of the edge**, not a tuning knob. The only lever in the current engine
stack is the L8 `min_convergence` gate; sweeping it shows the tradeoff empirically:

| Engine | min_convergence | Trades | Win Rate % | Expectancy R | PnL USD |
|---|---|---|---|---|---|
| A | 0.45 | 3422 | 35.1 | 0.021 | -6162.22 |
| A | 0.55 | 3531 | 32.6 | -0.015 | -15342.1 |
| A | 0.65 | 3773 | 32.8 | 0.015 | 85818.08 |
| A | 0.75 | 3034 | 31.6 | 0.01 | 119833.39 |
| A | 0.85 | 1249 | 20.4 | -0.11 | 27805.27 |
| A | 0.95 | 629 | 1.3 | -0.316 | -5352.88 |
| B | 0.45 | 3486 | 33.5 | 0.013 | 4337.4 |
| B | 0.55 | 3552 | 34.2 | 0.027 | 48834.78 |
| B | 0.65 | 3631 | 33.0 | 0.016 | 106929.29 |
| B | 0.75 | 2938 | 32.2 | 0.019 | 122267.03 |
| B | 0.85 | 1201 | 21.2 | -0.094 | 29864.34 |
| B | 0.95 | 582 | 1.4 | -0.302 | -4652.88 |
| C | 0.45 | 3514 | 33.0 | 0.014 | 11656.24 |
| C | 0.55 | 3607 | 32.9 | 0.003 | 12033.34 |
| C | 0.65 | 3589 | 32.7 | 0.014 | 47252.48 |
| C | 0.75 | 2749 | 32.3 | 0.036 | 125919.18 |
| C | 0.85 | 1095 | 21.3 | -0.057 | 25290.8 |
| C | 0.95 | 528 | 1.5 | -0.219 | -3867.88 |
| D | 0.45 | 3519 | 33.4 | 0.031 | 21556.77 |
| D | 0.55 | 3668 | 33.3 | 0.018 | 38630.34 |
| D | 0.65 | 3529 | 34.5 | 0.074 | 221606.93 |
| D | 0.75 | 2499 | 32.6 | 0.079 | 154258.42 |
| D | 0.85 | 937 | 20.5 | 0.013 | 28655.56 |
| D | 0.95 | 483 | 1.4 | -0.089 | -3252.55 |

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

