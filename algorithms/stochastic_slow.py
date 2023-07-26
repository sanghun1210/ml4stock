import numpy as np

import pandas_ta as ta

def stc_slow(data, N=9, M=3, T=3) :
    L = data["low_price"].rolling(window=N).min()
    H = data["high_price"].rolling(window=N).max()

    fast_k = ((data["trade_price"] - L) / (H - L)) * 100
    slow_k = fast_k.rolling(window=M).mean()
    slow_d = slow_k.rolling(window=T).mean()
    
    return slow_k, slow_d

def is_stc_slow_good(data, N=10, M=5, T=5) :
    L = data["low_price"].rolling(window=N).min()
    H = data["high_price"].rolling(window=N).max()

    fast_k = ((data["trade_price"] - L) / (H - L)) * 100
    slow_k = fast_k.ewm(span=M).mean()
    slow_d = slow_k.ewm(span=T).mean()

    if slow_k.iloc[-1] > slow_d.iloc[-1]:
        return slow_d.iloc[-1]
    else:
        return 100
