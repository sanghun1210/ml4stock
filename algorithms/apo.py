import pandas as pd

from pandas_datareader import data

def apo(pd_dataframe):
    close = pd_dataframe['trade_price']

    num_periods_fast = 10 # time period for the fast EMA
    K_fast = 2 / (num_periods_fast + 1) # smoothing factor for fast EMA
    ema_fast = 0
    num_periods_slow = 40 # time period for slow EMA
    K_slow = 2 / (num_periods_slow + 1) # smoothing factor for slow EMA
    ema_slow = 0

    ema_fast_values = [] # we will hold fast EMA values for visualization purposes
    ema_slow_values = [] # we will hold slow EMA values for visualization purposes
    apo_values = [] # track computed absolute price oscillator values
    for close_price in close:
        if (ema_fast == 0): # first observation
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_fast + ema_fast
            ema_slow = (close_price - ema_slow) * K_slow + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)
        apo_values.append(ema_fast - ema_slow)

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(AbsolutePriceOscillator=pd.Series(apo_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    ema_f = pd_dataframe['FastExponential10DayMovingAverage']
    ema_s = pd_dataframe['SlowExponential40DayMovingAverage']
    apo = pd_dataframe['AbsolutePriceOscillator']

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax1 = fig.add_subplot(211, ylabel='Google price in $')
    close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    ema_f.plot(ax=ax1, color='b', lw=2., legend=True)
    ema_s.plot(ax=ax1, color='r', lw=2., legend=True)
    ax2 = fig.add_subplot(212, ylabel='APO')
    apo.plot(ax=ax2, color='black', lw=2., legend=True)
    plt.show()
