import pandas as pd
import pandas_ta as ta

#이격도
def disparity(df, ndays = 10):
    df["MA"]=df["trade_price"].rolling(ndays).mean()
    df['disparity'] = 100*(df["trade_price"]/df["MA"])
    return df['disparity']

