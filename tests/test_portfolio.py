import numpy as np, pandas as pd
from src.macrofund.portfolio import construct_portfolio

def test_portfolio_respects_limits():
    syms=["SPY","EFA","EEM","TLT","IEF","GLD","DBC","UUP"]; signals=pd.DataFrame({"score":[2,1.5,1,-1,-.5,.8,.4,-.8]},index=syms); rng=np.random.default_rng(2); idx=pd.date_range("2020-01-31",periods=24,freq="ME"); rets=pd.DataFrame(rng.normal(0,.04,size=(24,8)),index=idx,columns=syms)
    w=construct_portfolio(signals,rets,max_gross=1.5,max_weight=.35); assert w.abs().sum()<=1.50001; assert w.abs().max()<=.35001; assert abs(w.sum())<=.55001
