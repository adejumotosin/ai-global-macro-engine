from __future__ import annotations
import numpy as np
import pandas as pd


def build_carry_scores(macro_features: pd.DataFrame, symbols: list[str] | pd.Index) -> pd.DataFrame:
    """Build simple, transparent ex-ante carry proxies.

    The MVP only applies carry where the macro inputs have a defensible mapping:
    - TLT: 10y Treasury yield minus policy rate
    - IEF: 5y Treasury yield minus policy rate, falling back to 10y when 5y is absent

    Other assets remain zero until proper FX-rate differentials and commodity
    futures curves are added. Values are cross-sectionally bounded before use.
    """
    idx = macro_features.index
    out = pd.DataFrame(0.0, index=idx, columns=list(symbols), dtype=float)
    policy = pd.to_numeric(macro_features.get("fed_funds"), errors="coerce")
    ten = pd.to_numeric(macro_features.get("treasury_10y"), errors="coerce")
    five = pd.to_numeric(macro_features.get("treasury_5y"), errors="coerce")
    if five is None or getattr(five, "isna", lambda: pd.Series([True]))().all():
        five = ten

    if "TLT" in out:
        out["TLT"] = ((ten - policy) / 4.0).clip(-1.5, 1.5).fillna(0.0)
    if "IEF" in out:
        out["IEF"] = ((five - policy) / 4.0).clip(-1.5, 1.5).fillna(0.0)
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)
