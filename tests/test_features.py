import numpy as np, pandas as pd
from src.macrofund.features import expanding_zscore

def test_expanding_zscore_has_warmup_and_finite_tail():
    s=pd.Series(np.arange(60,dtype=float)); z=expanding_zscore(s,min_periods=12)
    assert z.iloc[:11].isna().all(); assert np.isfinite(z.iloc[-1])
