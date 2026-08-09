from __future__ import annotations
import math, numpy as np, pandas as pd
from .portfolio import construct_portfolio
from .signals import signal_table

def performance_metrics(returns):
    r=pd.to_numeric(returns,errors="coerce").dropna()
    if r.empty:return {}
    eq=(1+r).cumprod(); years=max(len(r)/12,1/12); cagr=float(eq.iloc[-1]**(1/years)-1); vol=float(r.std(ddof=0)*math.sqrt(12)); sharpe=float(r.mean()*12/vol) if vol>0 else 0
    down=r[r<0].std(ddof=0)*math.sqrt(12); sortino=float(r.mean()*12/down) if down and np.isfinite(down) else 0; dd=eq/eq.cummax()-1; mdd=float(dd.min())
    return {"cagr":round(cagr,4),"annual_volatility":round(vol,4),"sharpe":round(sharpe,3),"sortino":round(sortino,3),"max_drawdown":round(mdd,4),"calmar":round(cagr/abs(mdd),3) if mdd<0 else 0,"positive_months":round(float((r>0).mean()),3),"ending_growth_of_1":round(float(eq.iloc[-1]),3)}

def run_backtest(monthly_prices,macro_features,regimes,target_volatility=.10,max_gross=1.5,max_weight=.35,transaction_cost_bps=10,min_history_months=18):
    prices=monthly_prices.sort_index().ffill(); rets=prices.pct_change(fill_method=None); common=prices.index.intersection(macro_features.index).intersection(regimes.index).sort_values(); strategy={}; bench={}; turn={}; weights={}; prev=pd.Series(0.,index=prices.columns)
    for pos in range(min_history_months,len(common)-1):
        date=common[pos]; nxt=common[pos+1]; rr=regimes.loc[date]; feat=macro_features.loc[date]
        if pd.isna(rr.get("regime")):continue
        sig=signal_table(prices.loc[:date],str(rr["regime"]),None if pd.isna(rr.get("confidence")) else float(rr["confidence"]),float(feat.get("liquidity",0)))
        w=construct_portfolio(sig,rets.loc[:date],target_volatility,max_gross,max_weight,float(feat.get("risk",0))).reindex(prices.columns).fillna(0); nr=rets.loc[nxt].fillna(0); traded=float((w-prev).abs().sum())
        strategy[nxt]=float((w*nr).sum()-traded*transaction_cost_bps/10000); turn[nxt]=traded; weights[date]=w.to_dict(); bench[nxt]=.6*float(nr.get("SPY",0))+.4*float(nr.get("IEF",0)); prev=w
    s=pd.Series(strategy,dtype=float).sort_index(); b=pd.Series(bench,dtype=float).sort_index(); return {"strategy_returns":s,"benchmark_returns":b,"weights":pd.DataFrame(weights).T if weights else pd.DataFrame(),"turnover":pd.Series(turn,dtype=float),"strategy_metrics":{**performance_metrics(s),"average_monthly_turnover":round(float(pd.Series(turn).mean()),3) if turn else 0},"benchmark_metrics":performance_metrics(b)}
