import numpy as np, pandas as pd
from src.macrofund.regime import expanding_regimes, semantic_regime

def test_semantic_quadrants():
    assert semantic_regime(1,-1)=="Goldilocks"; assert semantic_regime(1,1)=="Reflation"; assert semantic_regime(-1,1)=="Stagflation"; assert semantic_regime(-1,-1)=="Deflation"
def test_expanding_regime_produces_clusters_after_warmup():
    rng=np.random.default_rng(7); idx=pd.date_range("2010-01-31",periods=90,freq="ME"); frame=pd.DataFrame(rng.normal(size=(90,4)),index=idx,columns=["growth","inflation","liquidity","risk"])
    out=expanding_regimes(frame,warmup=24,k=4,refit_every=6); assert out.cluster.iloc[:24].isna().all(); assert out.cluster.iloc[30:].notna().all(); assert out.confidence.dropna().between(0,1).all()
