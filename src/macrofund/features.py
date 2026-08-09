from __future__ import annotations
import numpy as np, pandas as pd

def _monthly_last(s: pd.Series)->pd.Series: return s.dropna().resample("ME").last()
def expanding_zscore(s: pd.Series,min_periods:int=36)->pd.Series:
    s=pd.to_numeric(s,errors="coerce"); mean=s.expanding(min_periods=min_periods).mean(); std=s.expanding(min_periods=min_periods).std(ddof=0).replace(0,np.nan)
    return ((s-mean)/std).clip(-4,4)

def build_macro_features(raw: pd.DataFrame)->pd.DataFrame:
    idx=pd.date_range(raw.index.min(),raw.index.max(),freq="ME"); base=pd.DataFrame(index=idx)
    def get(name):
        if name not in raw: return pd.Series(index=idx,dtype=float)
        return _monthly_last(raw[name]).reindex(idx).ffill()
    cpi=get("cpi").shift(1); ind=get("industrial_production").shift(1); un=get("unemployment").shift(1)
    fed=get("fed_funds"); curve=get("yield_curve"); nfci=get("financial_conditions"); usd=get("usd_trade_weighted"); oil=get("oil"); vix=get("vix"); ten=get("treasury_10y"); two=get("treasury_2y")
    o=pd.DataFrame(index=idx); o["cpi_yoy"]=cpi.pct_change(12,fill_method=None)*100; o["inflation_accel"]=o["cpi_yoy"].diff(3)
    o["indpro_yoy"]=ind.pct_change(12,fill_method=None)*100; o["unemployment_6m_change"]=un.diff(6); o["fed_funds"]=fed; o["policy_3m_change"]=fed.diff(3)
    o["yield_curve"]=curve.where(curve.notna(),ten-two); o["financial_conditions"]=nfci; o["usd_3m"]=usd.pct_change(3,fill_method=None)*100; o["oil_3m"]=oil.pct_change(3,fill_method=None)*100; o["vix"]=vix
    o["growth"]=(expanding_zscore(o["indpro_yoy"])-expanding_zscore(o["unemployment_6m_change"]))/2
    o["inflation"]=(expanding_zscore(o["cpi_yoy"])+.35*expanding_zscore(o["inflation_accel"])+.20*expanding_zscore(o["oil_3m"]))/1.55
    o["liquidity"]=(-expanding_zscore(o["policy_3m_change"])-expanding_zscore(o["financial_conditions"])+.35*expanding_zscore(o["yield_curve"]))/2.35
    o["risk"]=(expanding_zscore(o["vix"])+.35*expanding_zscore(o["usd_3m"])+expanding_zscore(o["financial_conditions"]))/2.35
    return o.replace([np.inf,-np.inf],np.nan)
