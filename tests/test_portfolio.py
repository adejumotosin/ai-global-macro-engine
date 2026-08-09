import numpy as np, pandas as pd
from src.macrofund.portfolio import construct_portfolio


def _returns(syms):
    rng=np.random.default_rng(2)
    idx=pd.date_range("2020-01-31",periods=24,freq="ME")
    return pd.DataFrame(rng.normal(0,.04,size=(24,len(syms))),index=idx,columns=syms)


def test_portfolio_respects_limits():
    syms=["SPY","EFA","EEM","TLT","IEF","GLD","DBC","UUP"]
    signals=pd.DataFrame({"score":[2,1.5,1,-1,-.5,.8,.4,-.8]},index=syms)
    w=construct_portfolio(signals,_returns(syms),max_gross=1.5,max_weight=.35)
    assert w.abs().sum()<=1.50001
    assert w.abs().max()<=.35001
    assert abs(w.sum())<=.55001


def test_neutral_signals_receive_zero_weight():
    syms=["SPY","EFA","TLT","GLD","UUP"]
    signals=pd.DataFrame({
        "score":[.8,.5,-.9,-.1,-.2],
        "direction":["LONG","LONG","SHORT","NEUTRAL","NEUTRAL"],
    },index=syms)
    w=construct_portfolio(signals,_returns(syms),max_gross=1.5,max_weight=.35)
    assert w["GLD"]==0
    assert w["UUP"]==0
    assert w["SPY"]>0 and w["EFA"]>0 and w["TLT"]<0
    assert abs(w.sum())<=.55001
