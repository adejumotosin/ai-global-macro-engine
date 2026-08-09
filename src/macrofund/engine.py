from __future__ import annotations
import time, pandas as pd
from .backtest import run_backtest
from .config import SETTINGS, Settings
from .data import fetch_asset_prices, fetch_macro_bundle
from .features import build_macro_features
from .memo import build_investment_memo
from .portfolio import construct_portfolio, portfolio_stats
from .regime import current_regime, expanding_regimes
from .signals import signal_table
_CACHE={}

def run_engine(settings:Settings=SETTINGS,force:bool=False):
    now=time.time(); cached=_CACHE.get("engine")
    if cached and not force and now-cached[0]<settings.cache_ttl_seconds:return cached[1]
    macro_raw=fetch_macro_bundle(settings.macro_series,settings.start_date); macro=build_macro_features(macro_raw); regimes=expanding_regimes(macro,settings.regime_warmup_months,settings.regime_clusters)
    daily=fetch_asset_prices(settings.assets.keys(),settings.start_date); monthly=daily.resample("ME").last().dropna(how="all").ffill(); shared=macro.index.intersection(monthly.index).intersection(regimes.index)
    if len(shared)<36:raise RuntimeError("Insufficient common macro and market history")
    macro=macro.reindex(shared); regimes=regimes.reindex(shared); monthly=monthly.reindex(shared).ffill(); snap=current_regime(macro,regimes); date=pd.Timestamp(snap["date"])
    sig=signal_table(monthly.loc[:date],snap["regime"],snap["confidence"],snap["liquidity"]); rets=monthly.pct_change(fill_method=None)
    w=construct_portfolio(sig,rets.loc[:date],settings.target_volatility,settings.max_gross_exposure,settings.max_single_weight,snap["risk"])
    bt=run_backtest(monthly,macro,regimes,settings.target_volatility,settings.max_gross_exposure,settings.max_single_weight,settings.transaction_cost_bps); memo=build_investment_memo(snap,sig,w)
    records=[{"symbol":s,"asset":settings.assets.get(s,s),"score":round(float(r.score),3),"direction":r.direction,"momentum_3m":round(float(r.momentum_3m),4),"momentum_12m":round(float(r.momentum_12m),4),"weight":round(float(w.get(s,0)),4)} for s,r in sig.iterrows()]
    result={"as_of":snap["date"],"regime":snap,"portfolio":{**portfolio_stats(w),"weights":{k:round(float(v),4) for k,v in w.sort_values(ascending=False).items()}},"signals":records,"backtest":{"strategy":bt["strategy_metrics"],"benchmark_60_40":bt["benchmark_metrics"],"months":int(len(bt["strategy_returns"]))},"memo":memo,"data_notes":{"macro_provider":"FRED","market_provider":"Yahoo chart endpoint (MVP adapter)","macro_provider_errors":macro_raw.attrs.get("provider_errors",{}),"market_provider_errors":daily.attrs.get("provider_errors",{}),"revised_data_warning":"Latest-vintage macro data may contain revisions. Publication lags are applied, but ALFRED vintages are required for a fully point-in-time backtest."}}
    _CACHE["engine"]=(now,result); return result
