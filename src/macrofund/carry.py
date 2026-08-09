from __future__ import annotations
import numpy as np
import pandas as pd


def _series(frame: pd.DataFrame, name: str) -> pd.Series:
    if name not in frame:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[name], errors="coerce").reindex(frame.index)


def build_carry_scores(macro_features: pd.DataFrame, symbols: list[str] | pd.Index) -> pd.DataFrame:
    """Build transparent ex-ante carry proxies from rates available at decision time.

    The first production candidate deliberately applies carry only where the
    mapping is defensible with the existing data:
    - TLT: 10-year Treasury yield minus the policy rate.
    - IEF: 5-year Treasury yield minus the policy rate.

    Other assets stay at zero until proper FX interest differentials and
    commodity futures curves are added. This avoids inventing carry from ETF
    price momentum.
    """
    idx = macro_features.index
    out = pd.DataFrame(0.0, index=idx, columns=list(symbols), dtype=float)
    policy = _series(macro_features, "fed_funds")
    ten = _series(macro_features, "treasury_10y")
    five = _series(macro_features, "treasury_5y")
    if five.isna().all():
        five = ten

    if "TLT" in out.columns:
        out["TLT"] = ((ten - policy) / 4.0).clip(-1.5, 1.5).fillna(0.0)
    if "IEF" in out.columns:
        out["IEF"] = ((five - policy) / 4.0).clip(-1.5, 1.5).fillna(0.0)
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)
