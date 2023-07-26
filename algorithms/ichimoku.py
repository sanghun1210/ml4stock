import pandas as pd
import pandas_ta as ta

def ichimoku_cal(df):
    ichimoku = ta.ichimoku(df["high_price"], df["low_price"], df["trade_price"])
    return ichimoku 

def tenkan_sen(price_df):
    # (9-period high + 9-period low)/2))
    df = price_df.copy()
    df['tenkan_high'] = df['High'].rolling(window=9).max()
    df['tenkan_low'] = df['Low'].rolling(window=9).min()
    df['tenkan_sen'] = (df['tenkan_high'] + df['tenkan_low']) / 2
    return df['tenkan_sen']

def kijun_sen(price_df):
    # (26-period high + 26-period low)/2))
    df = price_df.copy()
    df['kijun_high'] = df['High'].rolling(window=26).max()
    df['kijun_low'] = df['Low'].rolling(window=26).min()
    df['kijun_sen'] = (df['kijun_high'] + df['kijun_low']) / 2
    return df['kijun_sen']

def chikou_span(price_df):
    # Close shifted 26 days to the past
    df = price_df.copy()
    df['chikou_span'] = df['Close'].shift(-26)
    return df['chikou_span']

def a_senkou_span(price_df):
    #  (Tenkan Line + Kijun Line)/2))
    df = price_df.copy()
    df['tenkan_sen'] = tenkan_sen(df)
    df['kijun_sen'] = kijun_sen(df)
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    return df['senkou_span_a']

def b_senkou_span(price_df):
    #  (52-period high + 52-period low)/2))
    df = price_df.copy()
    df['span_b_high'] = df['High'].rolling(window=52).max()
    df['span_b_low'] = df['Low'].rolling(window=52).min()
    df['senkou_span_b'] = ((df['span_b_high'] + df['span_b_low']) / 2).shift(26)
    return df['senkou_span_b']