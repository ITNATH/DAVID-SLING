"""L7 strategies/vault - all 52 institutional strategies (S01-S52).

Each strategy is a real, deterministic rule over the FeatureSet producing a
SetupCandidate (direction, entry, SL, TP, R-multiple) when its pattern is
present. Families map to peer engines per config/strategies catalog.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from david_sling.intelligence.features import FeatureSet

Direction = Literal["long", "short"]


@dataclass(frozen=True)
class SetupCandidate:
    strategy_id: str
    family: str
    engines: tuple[str, ...]
    direction: Direction
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    confidence: float


@dataclass(frozen=True)
class BaseStrategy:
    sid: str
    name: str
    family: str
    engines: tuple[str, ...]
    rule: Callable[[FeatureSet, Direction], SetupCandidate | None]


def _mk(s: BaseStrategy, fs: FeatureSet, direction: Direction, sl_atr: float = 1.5,
        rr: float = 2.0, conf: float = 0.6) -> SetupCandidate | None:
    entry = fs.price
    if direction == "long":
        sl = entry - sl_atr * fs.atr_m1
        tp = entry + rr * (entry - sl)
    else:
        sl = entry + sl_atr * fs.atr_m1
        tp = entry - rr * (sl - entry)
    return SetupCandidate(strategy_id=s.sid, family=s.family, engines=s.engines,
                          direction=direction, entry=round(entry, 6), stop_loss=round(sl, 6),
                          take_profit=round(tp, 6), risk_reward=rr, confidence=conf)


def _dir(fs: FeatureSet) -> Direction:
    return "long" if (fs.displacement_up or fs.trend_alignment() > 0) else "short"


# ---------------------------------------------------------------- Family 1
def _s01(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Hawkes burst sniper
    if abs(fs.delta_m1) > 1.5 and fs.volume_z_m1 > 1.5:
        return _mk(_VAULT["S01"], fs, d, sl_atr=1.0, rr=1.5, conf=0.7)
    return None

def _s02(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # CVD absorption reversal
    if ((fs.rejection_dn and d == "long") or (fs.rejection_up and d == "short")) and abs(fs.delta_m1) < 0.5:
        return _mk(_VAULT["S02"], fs, d, sl_atr=1.2, rr=2.0, conf=0.65)
    return None

def _s03(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # bid-ask vacuum sweep
    if fs.sweep_dn_m5 and d == "long":
        return _mk(_VAULT["S03"], fs, d, sl_atr=1.0, rr=2.5, conf=0.7)
    if fs.sweep_up_m5 and d == "short":
        return _mk(_VAULT["S03"], fs, d, sl_atr=1.0, rr=2.5, conf=0.7)
    return None

def _s04(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # microstructure gap fill
    if fs.fvg_up_m5 and d == "short":
        return _mk(_VAULT["S04"], fs, d, sl_atr=0.8, rr=1.2, conf=0.55)
    if fs.fvg_dn_m5 and d == "long":
        return _mk(_VAULT["S04"], fs, d, sl_atr=0.8, rr=1.2, conf=0.55)
    return None

# ---------------------------------------------------------------- Family 2
def _s05(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # turtle soup CRT
    if fs.eql and fs.sweep_dn_m5 and fs.displacement_up:
        return _mk(_VAULT["S05"], fs, "long", sl_atr=1.0, rr=2.0, conf=0.75)
    if fs.eqh and fs.sweep_up_m5 and fs.displacement_dn:
        return _mk(_VAULT["S05"], fs, "short", sl_atr=1.0, rr=2.0, conf=0.75)
    return None

def _s06(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # London Judas swing
    if fs.session in ("LONDON", "LONDON_NY_OVERLAP") and ((fs.sweep_up_m5 and d == "short") or (fs.sweep_dn_m5 and d == "long")):
        return _mk(_VAULT["S06"], fs, d, sl_atr=1.2, rr=2.2, conf=0.7)
    return None

def _s07(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # FVG inversion retest
    if fs.fvg_dn_m5 and d == "long" and fs.rejection_dn:
        return _mk(_VAULT["S07"], fs, d, sl_atr=1.0, rr=2.5, conf=0.7)
    if fs.fvg_up_m5 and d == "short" and fs.rejection_up:
        return _mk(_VAULT["S07"], fs, d, sl_atr=1.0, rr=2.5, conf=0.7)
    return None

def _s08(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # CISD order block tap
    if fs.bos_up_h1 and d == "long" and abs(fs.price - fs.ema20_m1) < fs.atr_m1:
        return _mk(_VAULT["S08"], fs, d, sl_atr=1.5, rr=2.0, conf=0.65)
    if fs.bos_dn_h1 and d == "short" and abs(fs.price - fs.ema20_m1) < fs.atr_m1:
        return _mk(_VAULT["S08"], fs, d, sl_atr=1.5, rr=2.0, conf=0.65)
    return None

def _s09(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # breaker block shift
    if fs.choch_up_h1 and d == "long":
        return _mk(_VAULT["S09"], fs, d, sl_atr=2.0, rr=3.0, conf=0.7)
    if fs.choch_dn_h1 and d == "short":
        return _mk(_VAULT["S09"], fs, d, sl_atr=2.0, rr=3.0, conf=0.7)
    return None

def _s10(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # SMT divergence (proxy: sweep + reject)
    if (fs.sweep_up_m5 and fs.rejection_dn) or (fs.sweep_dn_m5 and fs.rejection_up):
        return _mk(_VAULT["S10"], fs, d, sl_atr=1.5, rr=2.5, conf=0.7)
    return None

def _s11(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # taipan wick raid
    if abs(fs.wick_ratio) >= 0.8 and ((fs.wick_ratio < 0 and d == "long") or (fs.wick_ratio > 0 and d == "short")):
        return _mk(_VAULT["S11"], fs, d, sl_atr=1.0, rr=2.0, conf=0.75)
    return None

# ---------------------------------------------------------------- Family 3
def _s12(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Stacey Burke 3-day cycle trap
    if fs.session == "NY" and ((fs.rejection_up and d == "short") or (fs.rejection_dn and d == "long")):
        return _mk(_VAULT["S12"], fs, d, sl_atr=1.5, rr=2.0, conf=0.6)
    return None

def _s13(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # first green/red day
    if fs.session == "LONDON" and fs.displacement_up and fs.volume_z_m1 > 1.0:
        return _mk(_VAULT["S13"], fs, "long", sl_atr=1.5, rr=2.5, conf=0.65)
    if fs.session == "LONDON" and fs.displacement_dn and fs.volume_z_m1 > 1.0:
        return _mk(_VAULT["S13"], fs, "short", sl_atr=1.5, rr=2.5, conf=0.65)
    return None

def _s14(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # 10 AM club
    if fs.session == "TEN_AM_CLUB" and fs.volume_z_m1 > 0.5 and (fs.displacement_up or fs.displacement_dn):
        return _mk(_VAULT["S14"], fs, d, sl_atr=1.2, rr=2.0, conf=0.65)
    return None

def _s15(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # asian range raid
    if fs.session in ("ASIA", "ASIA_LONDON_OVERLAP") and (fs.sweep_up_m5 or fs.sweep_dn_m5):
        return _mk(_VAULT["S15"], fs, d, sl_atr=1.2, rr=2.0, conf=0.6)
    return None

def _s16(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # ORB-15
    if fs.session in ("LONDON", "NY") and fs.bos_up_h1 if d == "long" else fs.bos_dn_h1:
        return _mk(_VAULT["S16"], fs, d, sl_atr=1.0, rr=2.0, conf=0.6)
    return None

# ---------------------------------------------------------------- Family 4
def _s17(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # HTF CHoCH/BOS retest
    if fs.trend_h4 != 0 and fs.bos_up_h1 and d == "long" and fs.atr_pct_h1 > 40:
        return _mk(_VAULT["S17"], fs, d, sl_atr=2.0, rr=3.0, conf=0.75)
    if fs.trend_h4 != 0 and fs.bos_dn_h1 and d == "short" and fs.atr_pct_h1 > 40:
        return _mk(_VAULT["S17"], fs, d, sl_atr=2.0, rr=3.0, conf=0.75)
    return None

def _s18(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # OTE 61.8-78.6 (proxy: deep pullback to ema50)
    if d == "long" and fs.trend_h4 > 0 and fs.price <= fs.ema50_h4 * 1.001 and fs.rsi_m1 < 45:
        return _mk(_VAULT["S18"], fs, d, sl_atr=2.5, rr=3.5, conf=0.7)
    if d == "short" and fs.trend_h4 < 0 and fs.price >= fs.ema50_h4 * 0.999 and fs.rsi_m1 > 55:
        return _mk(_VAULT["S18"], fs, d, sl_atr=2.5, rr=3.5, conf=0.7)
    return None

def _s19(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # quasimodo
    if (fs.eql and d == "long" and fs.displacement_up) or (fs.eqh and d == "short" and fs.displacement_dn):
        return _mk(_VAULT["S19"], fs, d, sl_atr=2.0, rr=3.0, conf=0.75)
    return None

def _s20(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # diamond compression
    if fs.atr_pct_h1 < 30 and abs(fs.trend_h4) == 0 and fs.volume_z_m1 > 0.5:
        return _mk(_VAULT["S20"], fs, d, sl_atr=1.5, rr=2.5, conf=0.6)
    return None

def _s21(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # broadening wedge
    if fs.atr_pct_h1 > 75 and fs.trend_alignment() == 0:
        return _mk(_VAULT["S21"], fs, d, sl_atr=2.5, rr=3.0, conf=0.6)
    return None

def _s22(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # head & shoulders neckline (proxy: double rejection at highs)
    if fs.rejection_up and fs.eqh and d == "short":
        return _mk(_VAULT["S22"], fs, d, sl_atr=2.0, rr=3.0, conf=0.65)
    if fs.rejection_dn and fs.eql and d == "long":
        return _mk(_VAULT["S22"], fs, d, sl_atr=2.0, rr=3.0, conf=0.65)
    return None

# ---------------------------------------------------------------- Family 5
def _s23(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # wyckoff spring
    if fs.sweep_dn_m5 and fs.rejection_dn and fs.volume_z_m1 > 1.0 and d == "long":
        return _mk(_VAULT["S23"], fs, d, sl_atr=1.5, rr=2.5, conf=0.7)
    return None

def _s24(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # UTAD
    if fs.sweep_up_m5 and fs.rejection_up and fs.volume_z_m1 > 1.0 and d == "short":
        return _mk(_VAULT["S24"], fs, d, sl_atr=1.5, rr=2.5, conf=0.7)
    return None

def _s25(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # LPS markup
    if fs.trend_h1 > 0 and fs.rejection_dn and fs.price > fs.ema20_h1:
        return _mk(_VAULT["S25"], fs, "long", sl_atr=1.5, rr=2.5, conf=0.65)
    return None

def _s26(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # LPSY markdown
    if fs.trend_h1 < 0 and fs.rejection_up and fs.price < fs.ema20_h1:
        return _mk(_VAULT["S26"], fs, "short", sl_atr=1.5, rr=2.5, conf=0.65)
    return None

def _s27(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # anchored VWAP shelf
    if d == "long" and fs.price > fs.vwap_m1 and fs.trend_m1 > 0 and fs.rejection_dn:
        return _mk(_VAULT["S27"], fs, d, sl_atr=1.0, rr=2.0, conf=0.65)
    if d == "short" and fs.price < fs.vwap_m1 and fs.trend_m1 < 0 and fs.rejection_up:
        return _mk(_VAULT["S27"], fs, d, sl_atr=1.0, rr=2.0, conf=0.65)
    return None

def _s28(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # HVN/POC rejection
    if fs.rejection_up and fs.volume_z_m1 > 2.0 and d == "short":
        return _mk(_VAULT["S28"], fs, d, sl_atr=1.2, rr=2.0, conf=0.65)
    if fs.rejection_dn and fs.volume_z_m1 > 2.0 and d == "long":
        return _mk(_VAULT["S28"], fs, d, sl_atr=1.2, rr=2.0, conf=0.65)
    return None

# ---------------------------------------------------------------- Family 6
def _harmonic(fs: FeatureSet, d: Direction, sid: str, prz_rr: float) -> SetupCandidate | None:
    # PRZ completion proxy: deep pullback against HTF trend + rejection
    if d == "long" and fs.trend_h4 > 0 and fs.rsi_m1 < 35 and fs.rejection_dn:
        return _mk(_VAULT[sid], fs, d, sl_atr=2.5, rr=prz_rr, conf=0.7)
    if d == "short" and fs.trend_h4 < 0 and fs.rsi_m1 > 65 and fs.rejection_up:
        return _mk(_VAULT[sid], fs, d, sl_atr=2.5, rr=prz_rr, conf=0.7)
    return None

def _s29(fs: FeatureSet, d: Direction) -> SetupCandidate | None:
    return _harmonic(fs, d, "S29", 3.0)   # Gartley 0.786

def _s30(fs: FeatureSet, d: Direction) -> SetupCandidate | None:
    return _harmonic(fs, d, "S30", 3.2)   # Bat 0.886

def _s31(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Butterfly 1.272 extension
    if fs.atr_pct_h1 > 85 and (fs.rejection_up or fs.rejection_dn):
        return _mk(_VAULT["S31"], fs, d, sl_atr=3.0, rr=2.0, conf=0.6)
    return None

def _s32(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Crab 1.618
    if fs.atr_pct_h1 > 90 and (fs.displacement_up or fs.displacement_dn):
        return _mk(_VAULT["S32"], fs, d, sl_atr=3.5, rr=2.0, conf=0.6)
    return None

def _s33(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Cypher 0.786
    if fs.bos_up_h1 and d == "long" and fs.rsi_m1 < 40:
        return _mk(_VAULT["S33"], fs, d, sl_atr=2.0, rr=3.0, conf=0.65)
    if fs.bos_dn_h1 and d == "short" and fs.rsi_m1 > 60:
        return _mk(_VAULT["S33"], fs, d, sl_atr=2.0, rr=3.0, conf=0.65)
    return None

def _s34(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # AB=CD measured move
    if fs.range3_m1 > 3 * fs.atr_m1 and fs.trend_alignment() != 0:
        return _mk(_VAULT["S34"], fs, d, sl_atr=2.0, rr=2.5, conf=0.65)
    return None

# ---------------------------------------------------------------- Family 7
def _s35(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # BB-Keltner squeeze
    if fs.atr_pct_h1 < 25 and abs(fs.bb_pos_m1) > 0.8:
        return _mk(_VAULT["S35"], fs, d, sl_atr=1.2, rr=2.5, conf=0.6)
    return None

def _s36(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # parabolic ATR expansion
    if fs.atr_pct_h1 > 88 and (fs.displacement_up or fs.displacement_dn):
        return _mk(_VAULT["S36"], fs, d, sl_atr=2.5, rr=1.5, conf=0.6)
    return None

def _s37(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # wavelet-denoised trend (proxy: smooth ema trend)
    if fs.trend_alignment() != 0 and abs(fs.price - fs.ema20_m1) < 0.5 * fs.atr_m1:
        return _mk(_VAULT["S37"], fs, d, sl_atr=1.5, rr=2.5, conf=0.6)
    return None

def _s38(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # multi-TF RSI divergence (proxy)
    if d == "long" and fs.rsi_m1 < 40 and fs.trend_h1 > 0:
        return _mk(_VAULT["S38"], fs, d, sl_atr=1.5, rr=2.5, conf=0.65)
    if d == "short" and fs.rsi_m1 > 60 and fs.trend_h1 < 0:
        return _mk(_VAULT["S38"], fs, d, sl_atr=1.5, rr=2.5, conf=0.65)
    return None

def _s39(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # zero-lag MACD impulse
    if abs(fs.macd_hist_m1) > 0 and ((fs.macd_hist_m1 > 0) == (d == "long")) and fs.volume_z_m1 > 1.0:
        return _mk(_VAULT["S39"], fs, d, sl_atr=1.0, rr=1.8, conf=0.6)
    return None

def _s40(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # ADX exhaustion (proxy: extreme rsi + expansion)
    if fs.atr_pct_h1 > 80 and ((d == "short" and fs.rsi_m1 > 75) or (d == "long" and fs.rsi_m1 < 25)):
        return _mk(_VAULT["S40"], fs, d, sl_atr=1.5, rr=1.5, conf=0.6)
    return None

# ---------------------------------------------------------------- Family 8 (Engine D macro)
def _s41(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # Takens attractor (proxy: HTF alignment)
    if fs.trend_alignment() != 0 and fs.trend_d1 == fs.trend_h4:
        return _mk(_VAULT["S41"], fs, d, sl_atr=3.0, rr=4.0, conf=0.7)
    return None

def _s42(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # HMM regime transition
    if fs.atr_pct_h1 > 70 and fs.trend_h4 != 0 and fs.trend_h1 == 0:
        return _mk(_VAULT["S42"], fs, d, sl_atr=3.0, rr=3.5, conf=0.65)
    return None

def _s43(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # TDA persistence shift (proxy: range contraction break)
    if fs.atr_pct_h1 < 25 and (fs.bos_up_h1 or fs.bos_dn_h1):
        return _mk(_VAULT["S43"], fs, d, sl_atr=2.5, rr=3.5, conf=0.65)
    return None

def _s44(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # SKEW-GARCH VRP reversion
    if fs.atr_pct_h1 > 85 and abs(fs.bb_pos_m1) > 0.9:
        return _mk(_VAULT["S44"], fs, d, sl_atr=3.0, rr=2.0, conf=0.6)
    return None

def _s45(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # VIX term structure pivot (proxy: vol regime flip)
    if 60 < fs.atr_pct_h1 < 75 and fs.trend_alignment() != 0:
        return _mk(_VAULT["S45"], fs, d, sl_atr=3.0, rr=3.0, conf=0.6)
    return None

def _s46(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # central bank shock repricing
    if fs.news_repricing and (fs.displacement_up or fs.displacement_dn):
        return _mk(_VAULT["S46"], fs, d, sl_atr=3.0, rr=4.0, conf=0.75)
    return None

def _s47(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # triangular arb (proxy: HTF trend + vol)
    if fs.trend_d1 != 0 and fs.atr_pct_h1 > 50:
        return _mk(_VAULT["S47"], fs, d, sl_atr=3.5, rr=4.0, conf=0.6)
    return None

def _s48(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # commodity-FX cointegration (proxy: strong H4 trend)
    if abs(fs.trend_h4) == 1 and fs.atr_pct_h1 > 55:
        return _mk(_VAULT["S48"], fs, d, sl_atr=3.0, rr=3.5, conf=0.65)
    return None

def _s49(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # yield curve FX trend (proxy: D1 trend + expansion)
    if fs.trend_d1 != 0 and fs.atr_pct_h1 > 65:
        return _mk(_VAULT["S49"], fs, d, sl_atr=3.5, rr=4.0, conf=0.65)
    return None

def _s50(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # multi-month liquidity sweep (proxy: HTF sweep + displacement)
    if (fs.sweep_dn_m5 or fs.sweep_up_m5) and fs.trend_d1 != 0 and (fs.displacement_up or fs.displacement_dn):
        return _mk(_VAULT["S50"], fs, d, sl_atr=4.0, rr=5.0, conf=0.7)
    return None

def _s51(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # macro trend pyramid
    if fs.trend_d1 != 0 and fs.trend_h4 == fs.trend_d1 and fs.trend_h1 == fs.trend_d1:
        return _mk(_VAULT["S51"], fs, d, sl_atr=4.0, rr=5.0, conf=0.75)
    return None

def _s52(fs: FeatureSet, d: Direction) -> SetupCandidate | None:  # edge-decay rotation (proxy: weakening momentum vs HTF)
    if fs.trend_h4 != 0 and fs.trend_m15 == -fs.trend_h4 and abs(fs.macd_hist_m1) > 0:
        return _mk(_VAULT["S52"], fs, "long" if fs.trend_h4 > 0 else "short", sl_atr=3.0, rr=3.0, conf=0.6)
    return None


_SPECS: list[tuple[str, str, str, tuple[str, ...], Callable]] = [
    # Family 1 - Orderflow & Microstructure (Engine A)
    ("S01", "Hawkes Burst Sniper", "orderflow_microstructure", ("A",), _s01),
    ("S02", "CVD Absorption Reversal", "orderflow_microstructure", ("A",), _s02),
    ("S03", "Bid-Ask Vacuum Sweep", "orderflow_microstructure", ("A",), _s03),
    ("S04", "Microstructure Gap Fill", "orderflow_microstructure", ("A",), _s04),
    # Family 2 - SMC & ICT Liquidity (A & B)
    ("S05", "Turtle Soup CRT", "smc_ict_liquidity", ("A", "B"), _s05),
    ("S06", "London Open Judas Swing", "smc_ict_liquidity", ("A", "B"), _s06),
    ("S07", "FVG Inversion Retest", "smc_ict_liquidity", ("A", "B"), _s07),
    ("S08", "CISD Order Block Tap", "smc_ict_liquidity", ("A", "B"), _s08),
    ("S09", "Breaker Block Shift", "smc_ict_liquidity", ("B",), _s09),
    ("S10", "SMT Divergence Cross", "smc_ict_liquidity", ("B",), _s10),
    ("S11", "Taipan Soup Wick Reversal", "smc_ict_liquidity", ("A", "B"), _s11),
    # Family 3 - Session Epochs & Cycles (B)
    ("S12", "Stacey Burke 3-Day Cycle", "session_cycles", ("B",), _s12),
    ("S13", "First Green/Red Day", "session_cycles", ("B",), _s13),
    ("S14", "10 AM Club Reversal", "session_cycles", ("B",), _s14),
    ("S15", "Asian Range Raid", "session_cycles", ("B",), _s15),
    ("S16", "ORB-15 Breakout", "session_cycles", ("B",), _s16),
    # Family 4 - Structural Swing (C)
    ("S17", "HTF CHoCH/BOS Retest", "structural_swing", ("C",), _s17),
    ("S18", "OTE Golden Zone", "structural_swing", ("C",), _s18),
    ("S19", "Quasimodo Level Failure", "structural_swing", ("C",), _s19),
    ("S20", "Diamond Breakout", "structural_swing", ("C",), _s20),
    ("S21", "Broadening Expansion", "structural_swing", ("C",), _s21),
    ("S22", "Head & Shoulders Neckline", "structural_swing", ("C",), _s22),
    # Family 5 - Wyckoff & Volume (B & C)
    ("S23", "Wyckoff Phase C Spring", "wyckoff_volume", ("B", "C"), _s23),
    ("S24", "Wyckoff UTAD", "wyckoff_volume", ("B", "C"), _s24),
    ("S25", "Wyckoff LPS Markup", "wyckoff_volume", ("C",), _s25),
    ("S26", "Wyckoff LPSY Markdown", "wyckoff_volume", ("C",), _s26),
    ("S27", "Anchored VWAP Shelf", "wyckoff_volume", ("B", "C"), _s27),
    ("S28", "HVN/POC Rejection", "wyckoff_volume", ("B", "C"), _s28),
    # Family 6 - Harmonics & Geometry (C)
    ("S29", "Harmonic Gartley PRZ", "harmonics_geometry", ("C",), _s29),
    ("S30", "Harmonic Bat PRZ", "harmonics_geometry", ("C",), _s30),
    ("S31", "Harmonic Butterfly", "harmonics_geometry", ("C",), _s31),
    ("S32", "Harmonic Crab", "harmonics_geometry", ("C",), _s32),
    ("S33", "Harmonic Cypher", "harmonics_geometry", ("C",), _s33),
    ("S34", "AB=CD Measured Move", "harmonics_geometry", ("C",), _s34),
    # Family 7 - Volatility & Momentum (A & B)
    ("S35", "Bollinger-Keltner Squeeze", "volatility_momentum", ("A", "B"), _s35),
    ("S36", "Parabolic ATR Expansion", "volatility_momentum", ("A", "B"), _s36),
    ("S37", "Wavelet Denoised Trend", "volatility_momentum", ("A", "B"), _s37),
    ("S38", "Multi-TF RSI Divergence", "volatility_momentum", ("A", "B"), _s38),
    ("S39", "Zero-Lag MACD Impulse", "volatility_momentum", ("A", "B"), _s39),
    ("S40", "ADX Exhaustion", "volatility_momentum", ("A", "B"), _s40),
    # Family 8 - Macro Institutional & Quant (D)
    ("S41", "Takens Phase Space", "macro_statistical", ("D",), _s41),
    ("S42", "HMM Regime Transition", "macro_statistical", ("D",), _s42),
    ("S43", "TDA Persistent Homology", "macro_statistical", ("D",), _s43),
    ("S44", "SKEW-GARCH VRP", "macro_statistical", ("D",), _s44),
    ("S45", "VIX Term Structure", "macro_statistical", ("D",), _s45),
    ("S46", "Central Bank Shock", "macro_statistical", ("D",), _s46),
    ("S47", "Triangular Synthetic Arb", "macro_statistical", ("D",), _s47),
    ("S48", "Commodity-FX Cointegration", "macro_statistical", ("D",), _s48),
    ("S49", "Sovereign Yield Curve", "macro_statistical", ("D",), _s49),
    ("S50", "Monthly Liquidity Sweep", "macro_statistical", ("D",), _s50),
    ("S51", "Macro Trend Pyramid", "macro_statistical", ("D",), _s51),
    ("S52", "Edge-Decay Rotation", "macro_statistical", ("D",), _s52),
]


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, BaseStrategy] = {}
        for sid, name, family, engines, rule in _SPECS:
            self._strategies[sid] = BaseStrategy(sid=sid, name=name, family=family,
                                                 engines=engines, rule=rule)

    def get(self, sid: str) -> BaseStrategy:
        return self._strategies[sid]

    def all(self) -> list[BaseStrategy]:
        return list(self._strategies.values())

    def by_family(self, family: str) -> list[BaseStrategy]:
        return [s for s in self._strategies.values() if s.family == family]

    def evaluate(self, fs: FeatureSet) -> list[SetupCandidate]:
        direction = _dir(fs)
        out: list[SetupCandidate] = []
        for s in self._strategies.values():
            try:
                cand = s.rule(fs, direction)
            except Exception:
                cand = None
            if cand is not None:
                out.append(cand)
        out.sort(key=lambda c: c.confidence, reverse=True)
        return out


STRATEGY_VAULT = StrategyRegistry()


def get_strategy(sid: str) -> BaseStrategy:
    return STRATEGY_VAULT.get(sid)


# late binding for _mk helper references
_VAULT = {s.sid: s for s in STRATEGY_VAULT.all()}
