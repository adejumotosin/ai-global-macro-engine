from __future__ import annotations
import numpy as np, pandas as pd


def _cap(w,gross,maxw):
    w=w.copy().fillna(0.)
    for _ in range(12):
        g=float(w.abs().sum())
        if g<=1e-12:return w
        w*=gross/g
        clipped=w.clip(-maxw,maxw)
        if np.allclose(clipped.to_numpy(),w.to_numpy(),atol=1e-8):
            w=clipped
            break
        w=clipped
    g=float(w.abs().sum())
    if g>gross:w*=gross/g
    return w


def _limit_net_exposure(w:pd.Series,max_net:float=.55)->pd.Series:
    """Reduce the dominant side without creating new positions or flipping signs."""
    w=w.copy()
    net=float(w.sum())
    if net>max_net:
        longs=w>0
        long_sum=float(w.loc[longs].sum())
        short_sum=float(w.loc[w<0].sum())
        target_long=max(0.,max_net-short_sum)
        if long_sum>0:w.loc[longs]*=min(1.,target_long/long_sum)
    elif net<-max_net:
        shorts=w<0
        short_abs=float(-w.loc[shorts].sum())
        long_sum=float(w.loc[w>0].sum())
        target_short_abs=max(0.,long_sum+max_net)
        if short_abs>0:w.loc[shorts]*=min(1.,target_short_abs/short_abs)
    return w


def construct_portfolio(signals:pd.DataFrame,monthly_returns:pd.DataFrame,target_volatility=.10,max_gross=1.5,max_weight=.35,risk_score=0.)->pd.Series:
    syms=signals.index.intersection(monthly_returns.columns)
    score=signals.loc[syms,"score"].astype(float)
    if "direction" in signals.columns:
        active=signals.loc[syms,"direction"].astype(str).str.upper().ne("NEUTRAL")
    else:
        active=score.abs()>=.35
    score=score.where(active,0.)

    hist=monthly_returns[syms].tail(12)
    vol=(hist.std(ddof=0)*np.sqrt(12)).replace(0,np.nan)
    vol=vol.fillna(vol.median()).clip(.06,.60)
    raw=(np.tanh(score)/vol).where(active,0.)

    stress=float(np.clip((risk_score-1)/2,0,.5))
    gross=max_gross*(1-stress)
    w=_cap(raw,gross,max_weight)
    w.loc[~active]=0.
    w=_limit_net_exposure(w,.55)

    if len(hist.dropna())>=6:
        cov=hist.cov().to_numpy(float)*12
        vec=w.reindex(hist.columns).fillna(0).to_numpy(float)
        est=float(np.sqrt(max(vec@cov@vec,0)))
        if est>target_volatility and est>1e-8:w*=target_volatility/est
    w.loc[~active]=0.
    return w.round(6)


def portfolio_stats(w):
    return {"gross_exposure":round(float(w.abs().sum()),4),"net_exposure":round(float(w.sum()),4),"long_exposure":round(float(w.clip(lower=0).sum()),4),"short_exposure":round(float(w.clip(upper=0).sum()),4)}