import numpy as np, pandas as pd
from src.macrofund.backtest import run_backtest

def test_backtest_is_next_period_aligned():
    rng=np.random.default_rng(3); idx=pd.date_range("2012-01-31",periods=100,freq="ME"); syms=["SPY","EFA","EEM","TLT","IEF","GLD","DBC","UUP"]; rets=pd.DataFrame(rng.normal(.004,.03,size=(100,8)),index=idx,columns=syms); prices=100*(1+rets).cumprod(); macro=pd.DataFrame(rng.normal(size=(100,4)),index=idx,columns=["growth","inflation","liquidity","risk"]); regimes=pd.DataFrame({"regime":["Goldilocks"]*100,"confidence":[.5]*100,"cluster":[1]*100},index=idx)
    result=run_backtest(prices,macro,regimes,min_history_months=18); assert len(result["strategy_returns"])>50; assert result["strategy_returns"].index.min()>idx[18]; assert "sharpe" in result["strategy_metrics"]
