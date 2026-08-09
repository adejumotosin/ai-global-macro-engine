from __future__ import annotations
import numpy as np, pandas as pd
REGIME_PRIORS={
"Goldilocks":{"SPY":1,"EFA":.8,"EEM":.8,"TLT":.1,"IEF":.1,"GLD":.2,"DBC":-.2,"UUP":-.4},
"Reflation":{"SPY":.5,"EFA":.4,"EEM":.5,"TLT":-.8,"IEF":-.4,"GLD":.4,"DBC":1,"UUP":-.2},
"Stagflation":{"SPY":-.8,"EFA":-.7,"EEM":-.5,"TLT":-.4,"IEF":.1,"GLD":1,"DBC":.8,"UUP":.4},
"Deflation":{"SPY":-1,"EFA":-.8,"EEM":-1,"TLT":1,"IEF":.8,"GLD":.3,"DBC":-.8,"UUP":.7}}
def _z(v):
    s=v.std(ddof=0); return v*0 if not np.isfinite(s) or s==0 else ((v-v.mean())/s).clip(-2.5,2.5)
def signal_table(monthly_prices:pd.DataFrame,regime:str,confidence:float|None,liquidity:float=0)->pd.DataFrame:
    p=monthly_prices.dropna(how="all").ffill()
    if len(p)<13: raise ValueError("Need 13 months market history")
    last=p.iloc[-1]; mom3=last/p.iloc[-4]-1; mom12=last/p.iloc[-13]-1; trend=pd.Series(np.where(last>=p.tail(10).mean(),1.,-1.),index=last.index)
    momentum=_z(.4*mom3+.6*mom12); prior=pd.Series(REGIME_PRIORS.get(regime,{}),dtype=float).reindex(last.index).fillna(0); conf=.5 if confidence is None else float(confidence)
    tilt=pd.Series(0.,index=last.index)
    for s in ["SPY","EFA","EEM","DBC"]:
        if s in tilt: tilt[s]=np.clip(liquidity,-2,2)/2
    for s in ["UUP","IEF","TLT"]:
        if s in tilt: tilt[s]=-np.clip(liquidity,-2,2)/3
    score=.50*prior*(.55+.45*conf)+.30*momentum+.15*trend+.05*tilt
    out=pd.DataFrame({"price":last,"regime_prior":prior,"momentum_3m":mom3,"momentum_12m":mom12,"trend":trend,"liquidity_tilt":tilt,"score":score})
    out["direction"]=np.select([out.score>=.35,out.score<=-.35],["LONG","SHORT"],default="NEUTRAL"); return out.sort_values("score",ascending=False)
