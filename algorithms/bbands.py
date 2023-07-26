import pandas as pd

from pandas_datareader import data
import numpy as np

def bbands(pd_dataframe, time_period): 
    goog_data = pd_dataframe
    close = goog_data['trade_price']

    import statistics as stats
    import math as math

    stdev_factor = 2 # Standard Deviation Scaling factor for the upper and lower bands
    history = [] # price history for computing simple moving average
    sma_values = [] # moving average of prices for visualization purposes
    upper_band = [] # upper band values
    lower_band = [] # lower band values

    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # we only want to maintain at most 'time_period' number of price observations
            del (history[0])

        sma = stats.mean(history)
        sma_values.append(sma) # simple moving average or middle band
        variance = 0 # variance is the square of standard deviation
        for hist_price in history:
            variance = variance + ((hist_price - sma) ** 2)

        stdev = math.sqrt(variance / len(history)) # use square root to get standard deviation

        upper_band.append(sma + stdev_factor * stdev)
        lower_band.append(sma - stdev_factor * stdev)

    goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
    goog_data = goog_data.assign(MiddleBollingerBand20DaySMA=pd.Series(sma_values, index=goog_data.index))
    goog_data = goog_data.assign(UpperBollingerBand20DaySMA2StdevFactor=pd.Series(upper_band, index=goog_data.index))
    goog_data = goog_data.assign(LowerBollingerBand20DaySMA2StdevFactor=pd.Series(lower_band, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    mband = goog_data['MiddleBollingerBand20DaySMA']
    uband = goog_data['UpperBollingerBand20DaySMA2StdevFactor']
    lband = goog_data['LowerBollingerBand20DaySMA2StdevFactor']

    return goog_data

    # goog_data['buy_signal'] =\
    #     np.where(goog_data['LowerBollingerBand20DaySMA2StdevFactor'][0:]
    #                                             > goog_data['trade_price'][0:], 1.0, 0.0)

    # goog_data['buy_orders'] = goog_data['buy_signal'].diff()

    # goog_data['sell_signal'] =\
    #     np.where(goog_data['MiddleBollingerBand20DaySMA'][0:]
    #                                             < goog_data['trade_price'][0:], -1.0, 0.0)
    # goog_data['sell_orders'] = goog_data['sell_signal'].diff()

    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, ylabel='Google price in $')

    # ax1.plot(goog_data.loc[goog_data.buy_orders== 1.0].index,
    #         pd_dataframe["trade_price"][goog_data.buy_orders == 1.0],
    #         '^', markersize=7, color='k')

    # ax1.plot(goog_data.loc[goog_data.sell_orders== -1.0].index,
    #         pd_dataframe["trade_price"][goog_data.sell_orders == -1.0],
    #         'v', markersize=7, color='k')

    # close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    # mband.plot(ax=ax1, color='b', lw=2., legend=True)
    # uband.plot(ax=ax1, color='g', lw=2., legend=True)
    # lband.plot(ax=ax1, color='r', lw=2., legend=True)
    # plt.show()

def get_margin(a, b):
    ma = 0
    if a > b:
        ma = ((a - b) / a) * 100
    else : 
        ma = ((b - a) / b) * 100
    return ma

def bbands_width(pd_dataframe, time_period):
    goog_data = bbands(pd_dataframe, time_period)
    mband = goog_data['MiddleBollingerBand20DaySMA']
    uband = goog_data['UpperBollingerBand20DaySMA2StdevFactor']
    lband = goog_data['LowerBollingerBand20DaySMA2StdevFactor']
    # print(uband.iloc[-1])
    # print(mband.iloc[-1])
    # print(lband.iloc[-1])
    return ((uband.iloc[-1] - lband.iloc[-1]) / mband.iloc[-1]) * 100


def bbands_is_low_touch(pd_dataframe, time_period):
    goog_data = bbands(pd_dataframe, time_period)
    mband = goog_data['MiddleBollingerBand20DaySMA']
    uband = goog_data['UpperBollingerBand20DaySMA2StdevFactor']
    lband = goog_data['LowerBollingerBand20DaySMA2StdevFactor']
    # print(uband.iloc[-1])
    # print(mband.iloc[-1])
    # print(lband.iloc[-1])
    return lband.iloc[-1] >= pd_dataframe['low_price'].iloc[-1] 
    

