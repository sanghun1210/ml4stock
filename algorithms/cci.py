import pandas as pd
from pandas_datareader import data
import numpy as np

# Commodity Channel Index 
def cci(df, ndays = 10): 
    df['TP'] = (df['high_price'] + df['low_price'] + df['trade_price']) / 3 
    df['sma'] = df['TP'].rolling(ndays).mean()
    df['mad'] = df['TP'].rolling(ndays).apply(lambda x: pd.Series(x).mad())
    df['CCI'] = (df['TP'] - df['sma']) / (0.015 * df['mad'])
    return df

def get_current_cci(df, ndays = 14): 
    df['TP'] = (df['high_price'] + df['low_price'] + df['trade_price']) / 3 
    df['sma'] = df['TP'].rolling(ndays).mean()
    df['mad'] = df['TP'].rolling(ndays).apply(lambda x: pd.Series(x).mad(), raw=False)
    df['CCI'] = (df['TP'] - df['sma']) / (0.015 * df['mad'])
    return df['CCI'].iloc[-1]

