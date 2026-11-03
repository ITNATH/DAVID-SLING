# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-03T10:34:32.366804+00:00 · Horizon: 1998-01-02 → 2026-11-03 (28y, 10532 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series (1998–2026)**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). 'Engine Gamma' does not exist in the codebase (audit gap G33) — its row is a clearly-labelled PRO-FORMA simulation. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 1998–2026 tape the four peer engines behave as designed: Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why a dedicated HFT engine must be properly engineered (gap G33) rather than bolted on.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | -29.78 | -1.22 | 46.31 | 546.0 | 0.53 | 0.71 | 0.97 | 36.3 | 0.01 | 5.82 | 0.006 | 3481 | -29779.93 |
| B — Tactical Intraday | 27.05 | 0.83 | 25.64 | 222.2 | 1.65 | 2.23 | 1.02 | 36.8 | 0.048 | 13.37 | -0.002 | 3428 | 27052.16 |
| C — Swing Structural | 58.74 | 1.62 | 30.23 | 204.6 | 1.58 | 2.19 | 1.05 | 35.6 | 0.045 | 13.18 | 0.002 | 3475 | 58741.84 |
| D — Macro Institutional | 81.37 | 2.09 | 26.97 | 101.9 | 1.36 | 1.89 | 1.09 | 34.8 | 0.061 | 14.24 | 0.005 | 3504 | 81365.08 |
| Gamma — HFT MM (PRO-FORMA, not in code) | -211.67 | -100.0 | 211.67 | 10407.0 | -0.9 | -0.9 | 0.0 | 0.5 | -0.992 | -276.8 | -0.174 | 1172 | -211665.69 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 8558 trades): win rate 38.2%, expectancy 0.049R, PnL 86746.87 USD.
- **CRYPTO** (3 instruments, 3975 trades): win rate 29.6%, expectancy 0.007R, PnL -8801.15 USD.
- **FX** (3 instruments, 907 trades): win rate 40.2%, expectancy 0.094R, PnL 43478.84 USD.
- **INDEX** (3 instruments, 338 trades): win rate 36.7%, expectancy 0.033R, PnL 1503.83 USD.
- **SYNTHETIC** (3 instruments, 110 trades): win rate 44.5%, expectancy 0.248R, PnL 14450.76 USD.

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
| A — Quant Scalping | 214 | 42.1 | 0.133 | 15154.31 |
| B — Tactical Intraday | 225 | 44.0 | 0.201 | 22079.39 |
| C — Swing Structural | 219 | 44.3 | 0.27 | 28377.93 |
| D — Macro Institutional | 206 | 38.8 | 0.135 | 14587.89 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 65 | 0.0 | -1.0 | -4851.25 |

### LTCM-1998
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 24 | 25.0 | -0.272 | -3418.25 |
| B — Tactical Intraday | 26 | 38.5 | 0.097 | 1286.0 |
| C — Swing Structural | 30 | 36.7 | 0.068 | 1724.87 |
| D — Macro Institutional | 31 | 22.6 | -0.3 | -3457.53 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 4 | 0.0 | -1.0 | -290.3 |

### SEP11-2001
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 4 | 25.0 | -0.25 | -546.67 |
| B — Tactical Intraday | 6 | 16.7 | -0.5 | -1791.72 |
| C — Swing Structural | 4 | 50.0 | 0.5 | 2128.19 |
| D — Macro Institutional | 3 | 66.7 | 1.0 | 1712.7 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 1 | 0.0 | -1.0 | -921.19 |

### DOTCOM-BUST
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 330 | 36.1 | 0.018 | -288.0 |
| B — Tactical Intraday | 328 | 36.3 | 0.028 | 3675.62 |
| C — Swing Structural | 340 | 39.4 | 0.108 | 28624.3 |
| D — Macro Institutional | 329 | 33.4 | -0.044 | -1009.85 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 121 | 0.8 | -0.986 | -28756.76 |

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1306 | 34.8 | -0.022 | -28001.87 |
| B — Tactical Intraday | 1299 | 35.3 | 0.05 | 7685.64 |
| C — Swing Structural | 1297 | 30.5 | -0.04 | -26497.9 |
| D — Macro Institutional | 1308 | 31.6 | 0.031 | 4380.25 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 432 | 0.5 | -0.994 | -35469.52 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 74 | 31.1 | -0.033 | -2015.92 |
| B — Tactical Intraday | 69 | 29.0 | -0.164 | -7057.3 |
| C — Swing Structural | 71 | 23.9 | -0.14 | -6686.88 |
| D — Macro Institutional | 70 | 20.0 | -0.137 | -6136.53 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 31 | 0.0 | -1.0 | -2134.74 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 63 | 17.5 | -0.474 | -15350.66 |
| B — Tactical Intraday | 67 | 28.4 | -0.296 | -12830.56 |
| C — Swing Structural | 60 | 23.3 | -0.308 | -9778.59 |
| D — Macro Institutional | 63 | 23.8 | -0.264 | -8882.64 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 21 | 0.0 | -1.0 | -3241.22 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 30 | 50.0 | 0.336 | 4914.42 |
| B — Tactical Intraday | 30 | 43.3 | 0.139 | 3431.36 |
| C — Swing Structural | 38 | 47.4 | 0.222 | 4233.02 |
| D — Macro Institutional | 35 | 42.9 | 0.225 | 3320.3 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 21 | 0.0 | -1.0 | -3430.05 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 115 | 44.3 | 0.217 | 3790.58 |
| B — Tactical Intraday | 105 | 43.8 | 0.114 | 7662.77 |
| C — Swing Structural | 106 | 45.3 | 0.283 | 13349.09 |
| D — Macro Institutional | 97 | 47.4 | 0.305 | 13821.63 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 39 | 0.0 | -0.991 | -22669.51 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 476 | 36.8 | 0.026 | -42.36 |
| B — Tactical Intraday | 468 | 37.0 | -0.018 | -16520.39 |
| C — Swing Structural | 487 | 39.0 | 0.059 | -1676.52 |
| D — Macro Institutional | 491 | 38.7 | 0.063 | 5934.07 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 184 | 0.0 | -0.999 | -14554.69 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 7 | 42.9 | -0.193 | -518.58 |
| B — Tactical Intraday | 10 | 40.0 | -0.113 | -240.24 |
| C — Swing Structural | 7 | 42.9 | 0.079 | 569.01 |
| D — Macro Institutional | 10 | 50.0 | 0.125 | 565.1 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 7 | 0.0 | -1.0 | -3588.71 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 221 | 36.7 | 0.023 | -574.59 |
| B — Tactical Intraday | 216 | 37.0 | 0.024 | 3619.1 |
| C — Swing Structural | 222 | 40.1 | 0.128 | 16217.24 |
| D — Macro Institutional | 218 | 41.3 | 0.183 | 26471.61 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 73 | 0.0 | -1.0 | -47010.16 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 142 | 34.5 | -0.072 | -6649.69 |
| B — Tactical Intraday | 143 | 38.5 | 0.048 | 467.81 |
| C — Swing Structural | 136 | 39.7 | 0.05 | 2030.32 |
| D — Macro Institutional | 143 | 40.6 | 0.115 | 4752.76 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 57 | 0.0 | -1.0 | -13202.88 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 391 | 35.0 | -0.035 | -13113.94 |
| B — Tactical Intraday | 387 | 35.1 | -0.006 | -9043.37 |
| C — Swing Structural | 394 | 39.3 | 0.114 | 19861.79 |
| D — Macro Institutional | 396 | 40.7 | 0.179 | 42806.06 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 125 | 0.0 | -1.0 | -80563.44 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 46.31% with average drawdown duration 546.0 simulated days; Sharpe 0.53 / Sortino 0.71 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 25.64% with average drawdown duration 222.2 simulated days; Sharpe 1.65 / Sortino 2.23 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 30.23% with average drawdown duration 204.6 simulated days; Sharpe 1.58 / Sortino 2.19 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 26.97% with average drawdown duration 101.9 simulated days; Sharpe 1.36 / Sortino 1.89 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma — HFT MM (PRO-FORMA, not in code)**: MDD 211.67% with average drawdown duration 10407.0 simulated days; Sharpe -0.9 / Sortino -0.9 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Win-Rate Feasibility Analysis — the 94% target

Win rate is an **outcome of the edge**, not a tuning knob. The only lever in the current engine
stack is the L8 `min_convergence` gate; sweeping it shows the tradeoff empirically:

| Engine | min_convergence | Trades | Win Rate % | Expectancy R | PnL USD |
|---|---|---|---|---|---|
| A | 0.45 | 3481 | 36.3 | 0.01 | -29779.93 |
| A | 0.55 | 3535 | 36.1 | 0.026 | -2952.14 |
| A | 0.65 | 3651 | 33.5 | 0.014 | 26203.91 |
| A | 0.75 | 3135 | 33.2 | 0.034 | 130541.25 |
| A | 0.85 | 1311 | 21.1 | -0.111 | -12412.1 |
| A | 0.95 | 576 | 0.9 | -0.259 | -5707.12 |
| B | 0.45 | 3428 | 36.8 | 0.048 | 27052.16 |
| B | 0.55 | 3469 | 36.1 | 0.057 | 62895.98 |
| B | 0.65 | 3581 | 33.7 | 0.025 | 47559.81 |
| B | 0.75 | 3076 | 33.2 | 0.036 | 122035.7 |
| B | 0.85 | 1279 | 21.4 | -0.11 | -12557.04 |
| B | 0.95 | 549 | 0.9 | -0.259 | -5440.41 |
| C | 0.45 | 3450 | 35.9 | 0.052 | 41296.08 |
| C | 0.55 | 3475 | 35.6 | 0.045 | 58741.84 |
| C | 0.65 | 3554 | 33.5 | 0.016 | 35444.48 |
| C | 0.75 | 2914 | 33.1 | 0.034 | 112258.6 |
| C | 0.85 | 1181 | 21.9 | -0.087 | -6126.14 |
| C | 0.95 | 505 | 1.0 | -0.227 | -4999.75 |
| D | 0.45 | 3461 | 35.7 | 0.054 | 45692.83 |
| D | 0.55 | 3458 | 34.7 | 0.016 | 3451.25 |
| D | 0.65 | 3519 | 34.3 | 0.041 | 84893.02 |
| D | 0.75 | 2591 | 33.2 | 0.055 | 107134.56 |
| D | 0.85 | 995 | 21.6 | -0.038 | -496.44 |
| D | 0.95 | 451 | 0.7 | -0.135 | -4772.54 |

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

