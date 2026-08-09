from __future__ import annotations
import numpy as np
import pandas as pd
from .specs import BASE_SPEC, SignalSpec

REGIME_PRIORS = {
    "Goldilocks": {"SPY": 1, "EFA": .8, "EEM": .8, "TLT": .1, "IEF": .1, "GLD": .2, "DBC": -.2, "UUP": -.4},
    "Reflation": {"SPY": .5, "EFA": .4, "EEM": .5, "TLT": -.8, "IEF": -.4, "GLD": .4, "DBC": 1, "UUP": -.2},
    "Stagflation": {"SPY": -.8, "EFA": -.7, "EEM": -.5, "TLT": -.4, "IEF": .1, "GLD": 1, "DBC": .8, "UUP": .4},
    "Deflation": {"SPY": -1, "EFA": -.8, "EEM": -1, "TLT": 1, "IEF": .8, "GLD": .3, "DBC": -.8, "UUP": .7},
}


def _z(v: pd.Series) -> pd.Series:
    s = v.std(ddof=0)
    return v * 0 if not np.isfinite(s) or s == 0 else ((v - v.mean()) / s).clip(-2.5, 2.5)


def signal_table(
    monthly_prices: pd.DataFrame,
    regime: str,
    confidence: float | None,
    liquidity: float = 0,
    carry: pd.Series | None = None,
    spec: SignalSpec = BASE_SPEC,
) -> pd.DataFrame:
    p = monthly_prices.dropna(how="all").ffill()
    if len(p) < 13:
        raise ValueError("Need 13 months market history")

    spec = spec.normalized()
    last = p.iloc[-1]
    mom3 = last / p.iloc[-4] - 1
    mom12 = last / p.iloc[-13] - 1
    trend = pd.Series(np.where(last >= p.tail(10).mean(), 1.0, -1.0), index=last.index)
    momentum = _z(0.4 * mom3 + 0.6 * mom12)
    prior = pd.Series(REGIME_PRIORS.get(regime, {}), dtype=float).reindex(last.index).fillna(0)
    conf = 0.5 if confidence is None else float(confidence)

    tilt = pd.Series(0.0, index=last.index)
    for symbol in ["SPY", "EFA", "EEM", "DBC"]:
        if symbol in tilt:
            tilt[symbol] = np.clip(liquidity, -2, 2) / 2
    for symbol in ["UUP", "IEF", "TLT"]:
        if symbol in tilt:
            tilt[symbol] = -np.clip(liquidity, -2, 2) / 3

    carry_vec = pd.Series(0.0, index=last.index)
    if carry is not None:
        carry_vec = pd.to_numeric(carry, errors="coerce").reindex(last.index).fillna(0.0).clip(-2.5, 2.5)

    score = (
        spec.regime_weight * prior * (0.55 + 0.45 * conf)
        + spec.momentum_weight * momentum
        + spec.trend_weight * trend
        + spec.liquidity_weight * tilt
        + spec.carry_weight * carry_vec
    )
    out = pd.DataFrame({
        "price": last,
        "regime_prior": prior,
        "momentum_3m": mom3,
        "momentum_12m": mom12,
        "trend": trend,
        "liquidity_tilt": tilt,
        "carry": carry_vec,
        "score": score,
    })
    out["direction"] = np.select(
        [out.score >= spec.long_threshold, out.score <= spec.short_threshold],
        ["LONG", "SHORT"],
        default="NEUTRAL",
    )
    return out.sort_values("score", ascending=False)
