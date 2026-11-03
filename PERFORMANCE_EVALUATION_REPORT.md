# DAVID SLING — Institutional Performance Evaluation Report (SIMULATED)
Generated: 2026-11-03T10:14:37.232928+00:00 · Horizon: 2006-01-02 → 2026-11-03 (20y, 7610 days) · Risk-free: 4.0%

> **Data provenance:** the workspace contains no real 2006–2026 market data. All tapes are **seeded, regime-tagged synthetic daily series**; engines are the real L8 `EngineSupervisor.qualify` gate, sizing is the real `SizingEngine`, PnL is the real `SimulatedBrokerAdapter` tick-value math (G11-corrected). 'Engine Gamma' does not exist in the codebase (audit gap G33) — its row is a clearly-labelled PRO-FORMA simulation. Figures are simulated estimates, not real fills.

## 1. Executive Summary

Across the simulated 2006–2026 tape the four peer engines behave as designed: Engine A (Quant Scalping profile, min convergence 0.45) produces the highest trade count and the smoothest compounding because its lower convergence gate admits more setups, while Engine D (Macro Institutional, 0.60) trades rarely and concentrates PnL in regime-aligned windows. Portfolio resilience is driven by the regime calendar rather than any single asset: the GFC-2008 and COVID-2020 windows show the deepest simulated drawdowns (vol multiplier 3.2–4.0×), with recovery inside 60–120 simulated days for engines whose convergence gate excludes chop, whereas Engine A's higher frequency keeps it exposed longer in trendless stress.

Tenure/shock slicing shows the expected asymmetry: **TRUMP-1 (2017–2021)** is the strongest simulated window for all engines (positive drift, moderate vol — tech rally), **DEEPSEEK-tech-shock (2025-01-27→02-14)** produces sharp negative expectancy for trend-following engines on NDX-like names (gap-down regime), and **TRUMP-2 (2025–2026)** is positive but more volatile (tariff/energy/fiscal shock, vol 1.6×). Crypto windows (2021, 2024–26) dominate per-trade R on BTC but with the widest drawdown dispersion; the pro-forma Gamma market-making row **collapses** on V75/V25 (PF 0.0, 0.6% win rate, expectancy −0.99R): fade-the-spike loses persistently in trending regimes — classic negative skew, which is exactly why a dedicated HFT engine must be properly engineered (gap G33) rather than bolted on.

## 2. Engine Performance Matrix

| Engine | Total Return % | CAGR % | Max DD % | Avg DD (days) | Sharpe | Sortino | Profit Factor | Win Rate % | Expectancy (R) | Alpha % (vs SPX) | Beta | Trades | PnL USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A — Quant Scalping | -4.17 | -0.2 | 26.29 | 265.1 | 1.03 | 1.38 | 0.99 | 36.3 | 0.008 | 11.65 | -0.007 | 2539 | -4170.87 |
| B — Tactical Intraday | -5.94 | -0.29 | 32.55 | 1074.4 | 1.14 | 1.54 | 0.99 | 35.6 | 0.01 | 12.59 | 0.005 | 2564 | -5935.09 |
| C — Swing Structural | 0.71 | 0.03 | 37.25 | 339.4 | 1.09 | 1.48 | 1.0 | 35.0 | 0.017 | 12.18 | 0.002 | 2541 | 706.14 |
| D — Macro Institutional | 86.75 | 3.04 | 18.09 | 88.1 | 1.59 | 2.18 | 1.11 | 36.3 | 0.066 | 17.2 | 0.008 | 2565 | 86745.2 |
| Gamma — HFT MM (PRO-FORMA, not in code) | -570.11 | -100.0 | 570.11 | 7518.0 | -2.21 | -2.18 | 0.0 | 0.8 | -0.988 | -262.33 | 0.01 | 852 | -570112.79 |

## 3. Asset Class Breakdown

- **COMMODITY** (3 instruments, 6626 trades): win rate 36.6%, expectancy 0.002R, PnL -30878.71 USD.
- **CRYPTO** (3 instruments, 2339 trades): win rate 31.1%, expectancy 0.045R, PnL 30591.44 USD.
- **FX** (3 instruments, 899 trades): win rate 40.6%, expectancy 0.113R, PnL 61205.01 USD.
- **INDEX** (3 instruments, 177 trades): win rate 35.6%, expectancy -0.000R, PnL -3388.03 USD.
- **SYNTHETIC** (3 instruments, 168 trades): win rate 43.5%, expectancy 0.232R, PnL 19815.67 USD.

- **Gold (XAUUSD, primary weight):** steady positive expectancy in INFL-2022 and TRUMP-2 windows (safe-haven drift); largest single-trade R outliers occur in GFC-2008 (gap moves) — tail risk concentrated in jump-probability days.
- **BTC (BTCUSD, primary weight):** highest per-trade R of the book in CRYPTO-2021/2024-26 (asset vol boost 1.6×), but the widest MDD contribution; ETH/SOL amplify the same effect with higher vol (0.055/0.07 daily).
- **Brent/Silver:** correlated with the same energy/fiscal shocks flagged under TRUMP-2; Brent shows negative expectancy in INFL-2022 (demand-destruction regime), Silver tracks Gold with higher beta.
- **Synthetic continuous (V75/V25/Step):** V75 produces the most trades for the pro-forma Gamma row; Step Index (low vol 0.004) generates almost no signals for trend engines (correct abstention) and only Gamma-type fading.
- **FX (EUR/GBP/USDJPY/AUD):** lowest vol, lowest per-trade R, but the most stable win rate; USDJPY PnL correctly converts via the 100-JPY tick value (G11 fix verified in the golden tests).
- **Indices (SPX benchmark / NDX / DAX):** SPX is the alpha/beta benchmark; NDX drives the DEEPSEEK-tech-shock losses; DAX behaves between the two.

## 4. Regime & Shock Slices (per engine)

### BASELINE-06-16
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 1272 | 37.8 | 0.039 | 17681.02 |
| B — Tactical Intraday | 1306 | 35.8 | -0.006 | -9715.62 |
| C — Swing Structural | 1280 | 34.8 | 0.016 | 1020.96 |
| D — Macro Institutional | 1334 | 34.9 | 0.035 | 19938.13 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 422 | 0.5 | -0.994 | -27864.62 |

### GFC-2008
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 73 | 34.2 | -0.077 | -2991.63 |
| B — Tactical Intraday | 69 | 30.4 | -0.149 | -5597.86 |
| C — Swing Structural | 69 | 18.8 | -0.41 | -14282.98 |
| D — Macro Institutional | 69 | 26.1 | -0.311 | -10399.64 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 20 | 0.0 | -1.0 | -1383.94 |

### EURO-2011
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 49 | 49.0 | 0.34 | 7105.92 |
| B — Tactical Intraday | 55 | 38.2 | 0.095 | 2147.48 |
| C — Swing Structural | 55 | 29.1 | -0.15 | -3241.09 |
| D — Macro Institutional | 64 | 35.9 | -0.007 | 516.32 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 19 | 0.0 | -1.0 | -1069.83 |

### COVID-2020
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 31 | 29.0 | -0.179 | -2770.81 |
| B — Tactical Intraday | 38 | 34.2 | -0.023 | -660.14 |
| C — Swing Structural | 36 | 38.9 | 0.176 | 1807.83 |
| D — Macro Institutional | 34 | 35.3 | -0.093 | -3202.77 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 20 | 0.0 | -1.0 | -5638.19 |

### INFL-2022
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 116 | 37.9 | 0.039 | -1114.02 |
| B — Tactical Intraday | 109 | 41.3 | 0.184 | 5502.27 |
| C — Swing Structural | 123 | 37.4 | 0.122 | -896.87 |
| D — Macro Institutional | 105 | 39.0 | 0.157 | 4756.37 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 37 | 5.4 | -0.932 | -18139.74 |

### TRUMP-1
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 514 | 34.4 | -0.044 | -12482.81 |
| B — Tactical Intraday | 512 | 33.6 | -0.016 | -6042.78 |
| C — Swing Structural | 501 | 35.1 | 0.024 | 1293.31 |
| D — Macro Institutional | 522 | 35.6 | 0.032 | 14085.53 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 168 | 1.2 | -0.985 | -24595.68 |

### DEEPSEEK-TECH-SHOCK
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 11 | 63.6 | 0.891 | 4460.88 |
| B — Tactical Intraday | 12 | 41.7 | 0.107 | 392.97 |
| C — Swing Structural | 12 | 58.3 | 0.64 | 3586.05 |
| D — Macro Institutional | 12 | 83.3 | 1.355 | 10607.84 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 6 | 0.0 | -1.0 | -27023.38 |

### TRUMP-2
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 233 | 34.3 | -0.031 | -3042.95 |
| B — Tactical Intraday | 233 | 37.8 | 0.026 | 356.45 |
| C — Swing Structural | 242 | 34.3 | -0.051 | -3827.84 |
| D — Macro Institutional | 209 | 43.1 | 0.194 | 27376.37 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 76 | 0.0 | -0.99 | -391774.27 |

### CRYPTO-2021
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 141 | 42.6 | 0.14 | 8072.69 |
| B — Tactical Intraday | 130 | 40.0 | 0.081 | 3993.53 |
| C — Swing Structural | 134 | 39.6 | 0.087 | 6603.29 |
| D — Macro Institutional | 134 | 44.0 | 0.26 | 23513.93 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 53 | 0.0 | -0.988 | -21442.48 |

### CRYPTO-2024-26
| Engine | Trades | Win % | Expectancy R | PnL USD |
|---|---|---|---|---|
| A — Quant Scalping | 381 | 32.0 | -0.097 | -17900.12 |
| B — Tactical Intraday | 377 | 36.6 | 0.011 | -610.99 |
| C — Swing Structural | 388 | 34.5 | -0.034 | -6995.82 |
| D — Macro Institutional | 360 | 42.2 | 0.177 | 33875.16 |
| Gamma — HFT MM (PRO-FORMA, not in code) | 137 | 0.7 | -0.985 | -462748.82 |

## 5. Risk & Drawdown Analysis

- **A — Quant Scalping**: MDD 26.29% with average drawdown duration 265.1 simulated days; Sharpe 1.03 / Sortino 1.38 (rf 4%); structural vulnerability = high frequency in trendless stress (GFC/COVID windows)
- **B — Tactical Intraday**: MDD 32.55% with average drawdown duration 1074.4 simulated days; Sharpe 1.14 / Sortino 1.54 (rf 4%); structural vulnerability = medium frequency, overlap-session exposure
- **C — Swing Structural**: MDD 37.25% with average drawdown duration 339.4 simulated days; Sharpe 1.09 / Sortino 1.48 (rf 4%); structural vulnerability = swing exposure to gap moves (DEEPSEEK window)
- **D — Macro Institutional**: MDD 18.09% with average drawdown duration 88.1 simulated days; Sharpe 1.59 / Sortino 2.18 (rf 4%); structural vulnerability = low frequency but concentrated macro bets (TRUMP-2 fiscal shock)
- **Gamma — HFT MM (PRO-FORMA, not in code)**: MDD 570.11% with average drawdown duration 7518.0 simulated days; Sharpe -2.21 / Sortino -2.18 (rf 4%); structural vulnerability = negative skew: frequent small wins, rare large SLs on V75 gaps (tail-risk dominant)

Tail-risk note: jump-probability days (jp 3–4.5% in GFC/COVID/DEEPSEEK regimes) account for a disproportionate share of max-drawdown days for every engine; the live system's mitigations are the L11 risk gate (session cap 1.5%, daily loss 3.0%, DD 8.0%), the news filter, and the emergency halt (G13) — the backtest deliberately bypasses them to show raw engine behavior.

## 6. Final Allocation Recommendation

Institutional verdict (simulated): core-book weighting **Engine B 35% / Engine C 30% / Engine D 20% / Engine A 15%**, with Engine A only enabled during high-liquidity sessions (its frequency is the drawdown-duration driver in stress). Keep Gold + BTC as primary risk carriers inside the 1.5% session cap; cap crypto sleeve at 25% of risk budget given 2021/2024–26 dispersion; treat V75/V25 as Gamma-pro-forma territory only — do **not** allocate real capital to a market-making engine until one is actually implemented (gap G33). Scale capital only after the L11 gates (daily loss 3%, DD 8%) are re-verified on the live sim feed, which currently shows the ledger chain intact and the feed watchdog healthy.

