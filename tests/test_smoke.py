"""Smoke test: both strategies import and run on synthetic data."""
import numpy as np, pandas as pd
from strategy.core import backtest as gold_bt, stats
from strategy.btc import backtest as btc_bt, build_plan as btc_plan

def _syn(n=900, seed=0):
    rng=np.random.default_rng(seed)
    price=1500+np.cumsum(rng.normal(0,8,n))
    dt=pd.date_range("2015-01-01",periods=n,freq="D")
    hi=price+np.abs(rng.normal(0,5,n)); lo=price-np.abs(rng.normal(0,5,n))
    return pd.DataFrame(dict(datetime=dt,open=price,high=np.maximum(hi,price),
                             low=np.minimum(lo,price),close=price))

def test_gold(): 
    s=stats(gold_bt(_syn())); assert "n" in s; print("gold ok:",s.get("n"),"trades")
def test_btc():
    df=_syn(); s=btc_bt(df); p=btc_plan(df)
    assert "sharpe" in s and "action" in p; print("btc ok:",p["action"])

if __name__=="__main__":
    test_gold(); test_btc()
