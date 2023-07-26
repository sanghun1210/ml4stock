import pandas as pd

from pandas_datareader import data
import statistics as stats
import math as math
import numpy as np

#표준편차
def stddev(pd_dataset):
    close = pd_dataset['trade_price']

    time_period = 20 # look back period
    history = [] # history of prices
    sma_values = [] # to track moving average values for visualization purposes
    stddev_values = [] # history of computed stdev values

    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # we track at most 'time_period' number of prices
            del (history[0])

        sma = stats.mean(history)
        sma_values.append(sma)
        variance = 0 # variance is square of standard deviation
        for hist_price in history:
            variance = variance + ((hist_price - sma) ** 2)

        stdev = math.sqrt(variance / len(history))
        stddev_values.append(stdev)

    pd_dataset = pd_dataset.assign(ClosePrice=pd.Series(close, index=pd_dataset.index))
    pd_dataset = pd_dataset.assign(StandardDeviationOver20Days=pd.Series(stddev_values, index=pd_dataset.index))

    close_price = pd_dataset['ClosePrice']
    stddev = pd_dataset['StandardDeviationOver20Days']

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax1 = fig.add_subplot(211, ylabel='Google price in $')
    close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    ax2 = fig.add_subplot(212, ylabel='Stddev in $')
    stddev.plot(ax=ax2, color='b', lw=2., legend=True)
    ax2.axhline(y=stats.mean(stddev_values), color='k')
    plt.show()

def get_stddev(pd_dataset, size):
    reversed_dataset = pd_dataset['trade_price'][::-1]
    tp = reversed_dataset[0:20]
    return np.std(tp,ddof=1)

