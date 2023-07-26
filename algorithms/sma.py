import pandas as pd

from pandas_datareader import data
import statistics as stats

#단순 이동 평균
def sma(pd_dataframe, time_period):
    close = pd_dataframe['trade_price']
    history = [] # to track a history of prices
    sma_values = [] # to track simple moving average values
    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # we remove oldest price because we only average over last 'time_period' prices
            del (history[0])

        sma_values.append(stats.mean(history))

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(Simple20DayMovingAverage=pd.Series(sma_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    pd_dataframe['Simple20DayMovingAverage']
    return pd_dataframe['Simple20DayMovingAverage']


def get_current_sma(pd_dataframe, time_period):
    goog_data = sma(pd_dataframe, time_period)
    return goog_data.iloc[-1]
