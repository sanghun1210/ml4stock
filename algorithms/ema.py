import pandas as pd
from pandas_datareader import data

def ema(pd_dataframe, period):
    close = pd_dataframe['trade_price']

    ema= pd_dataframe['trade_price'].ewm(span=period, adjust=False).mean()
    return ema

    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, ylabel='Google price in $')
    # close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    # ema.plot(ax=ax1, color='b', lw=2., legend=True)
    # plt.show()

