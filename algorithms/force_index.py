import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

def force_index(data,ndays):
    ForceIndex=pd.Series(data['trade_price'].diff(ndays)* data['trade_volume'],name='ForceIndex')
    data=data.join(ForceIndex)
    return data