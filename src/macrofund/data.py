from __future__ import annotations
from datetime import datetime, timezone
from io import StringIO
from typing import Iterable
import pandas as pd
import requests

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
class DataProviderError(RuntimeError): pass

def fetch_fred_series(series_id: str, start: str = "2000-01-01", timeout: int = 20) -> pd.Series:
    r = requests.get(FRED_CSV, params={"id": series_id, "cosd": start}, timeout=timeout,
                     headers={"User-Agent": "MacroFundAI/0.1 research-engine"})
    r.raise_for_status()
    frame = pd.read_csv(StringIO(r.text))
    if frame.empty or len(frame.columns) < 2: raise DataProviderError(f"No usable FRED data for {series_id}")
    dates = pd.to_datetime(frame.iloc[:,0], errors="coerce")
    values = pd.to_numeric(frame.iloc[:,1], errors="coerce")
    s = pd.Series(values.to_numpy(), index=dates, name=series_id).dropna().sort_index()
    s = s[~s.index.isna()]
    if s.empty: raise DataProviderError(f"No numeric FRED data for {series_id}")
    return s

def fetch_macro_bundle(series_map: dict[str,str], start: str) -> pd.DataFrame:
    columns, errors = {}, {}
    for name, sid in series_map.items():
        try: columns[name] = fetch_fred_series(sid, start)
        except Exception as exc: errors[name] = str(exc)
    if len(columns) < 7: raise DataProviderError(f"Too few macro series loaded: {errors}")
    out = pd.concat(columns, axis=1).sort_index(); out.attrs["provider_errors"] = errors; return out

def _unix(text: str) -> int: return int(pd.Timestamp(text, tz="UTC").timestamp())

def fetch_yahoo_price(symbol: str, start: str, end: str|None=None, timeout: int=20) -> pd.Series:
    end = end or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r = requests.get(YAHOO_CHART.format(symbol=symbol), params={"period1":_unix(start),"period2":_unix(end)+86400,
        "interval":"1d","events":"history","includeAdjustedClose":"true"},
        headers={"User-Agent":"Mozilla/5.0 MacroFundAI/0.1"}, timeout=timeout)
    r.raise_for_status(); payload=r.json()
    try:
        result=payload["chart"]["result"][0]; timestamps=result["timestamp"]; inds=result["indicators"]
        adj=(inds.get("adjclose") or [{}])[0].get("adjclose"); closes=adj or inds["quote"][0]["close"]
    except Exception as exc: raise DataProviderError(f"Unexpected market response for {symbol}") from exc
    idx=pd.to_datetime(timestamps,unit="s",utc=True).tz_convert(None)
    s=pd.Series(pd.to_numeric(closes, errors="coerce"), index=idx, name=symbol).dropna().sort_index()
    if s.empty: raise DataProviderError(f"No market history for {symbol}")
    return s

def fetch_asset_prices(symbols: Iterable[str], start: str) -> pd.DataFrame:
    columns, errors = {}, {}
    for sym in symbols:
        try: columns[sym]=fetch_yahoo_price(sym,start)
        except Exception as exc: errors[sym]=str(exc)
    if len(columns)<5: raise DataProviderError(f"Too few assets loaded: {errors}")
    out=pd.concat(columns,axis=1).sort_index(); out.attrs["provider_errors"]=errors; return out
