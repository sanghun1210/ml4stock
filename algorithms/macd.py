import pandas as pd
import numpy as np

from pandas_datareader import data

# MACD선이 0값을 상향돌파 할 경우: MACD선이 0을 상향돌파 할 경우는 단기이동평균선이 장기이동평균선 위에 있는 정배열을 의미한다. 
# MACD선이 0값을 하향돌파 할 경우: 아래의 그림처럼 MACD선이 0을 하향돌파 할 경우는 단기이동평균선이 장기이동평균선 아래에 있는 역배열을 의미한다. 
# MACD선이 Signal선을 상향돌파 할 경우: Oscillator가 (+)로 전환된다. -> 매수 포지션
# MACD선이 Signal선을 하향돌파 할 경우: Oscillator가 (-)로 전환된다. -> 매도 포지션

def macd(pd_dataframe):
    goog_data = pd_dataframe
    close = goog_data['trade_price']

    num_periods_fast = 6 # fast EMA time period #default : 12
    K_fast = 2 / (num_periods_fast + 1) # fast EMA smoothing factor
    ema_fast = 0
    num_periods_slow = 19 # slow EMA time period #default : 26
    K_slow = 2 / (num_periods_slow + 1) # slow EMA smoothing factor
    ema_slow = 0
    num_periods_macd = 6 # MACD EMA time period #default : 9
    K_macd = 2 / (num_periods_macd + 1) # MACD EMA smoothing factor
    ema_macd = 0

    ema_fast_values = [] # track fast EMA values for visualization purposes
    ema_slow_values = [] # track slow EMA values for visualization purposes
    macd_values = [] # track MACD values for visualization purposes
    macd_signal_values = [] # MACD EMA values tracker
    macd_historgram_values = [] # MACD - MACD-EMA
    for close_price in close:
        if (ema_fast == 0): # first observation
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_fast + ema_fast
            ema_slow = (close_price - ema_slow) * K_slow + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)

        macd = ema_fast - ema_slow # MACD is fast_MA - slow_EMA
        if ema_macd == 0:
            ema_macd = macd
        else:
            ema_macd = (macd - ema_macd) * K_macd + ema_macd # signal is EMA of MACD values

        macd_values.append(macd)
        macd_signal_values.append(ema_macd)
        macd_historgram_values.append(macd - ema_macd)

    goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
    goog_data = goog_data.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=goog_data.index))
    goog_data = goog_data.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=goog_data.index))
    goog_data = goog_data.assign(MovingAverageConvergenceDivergence=pd.Series(macd_values, index=goog_data.index))
    goog_data = goog_data.assign(Exponential20DayMovingAverageOfMACD=pd.Series(macd_signal_values, index=goog_data.index))
    goog_data = goog_data.assign(MACDHistorgram=pd.Series(macd_historgram_values, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    ema_f = goog_data['FastExponential10DayMovingAverage']
    ema_s = goog_data['SlowExponential40DayMovingAverage']
    macd = goog_data['MovingAverageConvergenceDivergence']
    ema_macd = goog_data['Exponential20DayMovingAverageOfMACD']
    macd_histogram = goog_data['MACDHistorgram']

    goog_data['signal'] =\
        np.where(goog_data['MovingAverageConvergenceDivergence'][0:]
                                                < goog_data['Exponential20DayMovingAverageOfMACD'][0:], 1.0, 0.0)
    goog_data['orders'] = goog_data['signal'].diff()

    initial_capital = float(1000.0)
    positions = pd.DataFrame(index=goog_data.index).fillna(0.0)
    portfolio = pd.DataFrame(index=goog_data.index).fillna(0.0)
    positions['GOOG'] = goog_data['signal'] 

    portfolio['positions'] = (positions.multiply(goog_data['trade_price'], axis = 0))

    portfolio['cash'] = initial_capital - (positions.diff().multiply(goog_data['trade_price'], axis=0)).cumsum()
    portfolio['total'] = portfolio['positions'] + portfolio['cash']

    print(portfolio)

    import matplotlib.pyplot as plt

    

    fig = plt.figure()
    ax1 = fig.add_subplot(311, ylabel='Google price in $')
    close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    ax1.plot(goog_data.loc[goog_data.orders== 1.0].index,
            pd_dataframe["trade_price"][goog_data.orders == 1.0],
            '^', markersize=7, color='k')
    ax1.plot(goog_data.loc[goog_data.orders== -1.0].index,
            pd_dataframe["trade_price"][goog_data.orders == -1.0],
            'v', markersize=7, color='k')

    # ax2 = fig.add_subplot(312, ylabel='MACD')
    # macd.plot(ax=ax2, color='black', lw=2., legend=True)
    # ema_macd.plot(ax=ax2, color='g', lw=2., legend=True)
    # ax3 = fig.add_subplot(313, ylabel='MACD')
    # macd_histogram.plot(ax=ax3, color='r', kind='bar', legend=True, use_index=False)
    # plt.show()

    plt.show()


def macd_cross(pd_dataframe):
    goog_data = pd_dataframe
    close = goog_data['trade_price']

    num_periods_fast = 12 # fast EMA time period
    K_fast = 2 / (num_periods_fast + 1) # fast EMA smoothing factor
    ema_fast = 0
    num_periods_slow = 26 # slow EMA time period
    K_slow = 2 / (num_periods_slow + 1) # slow EMA smoothing factor
    ema_slow = 0
    num_periods_macd = 9 # MACD EMA time period
    K_macd = 2 / (num_periods_macd + 1) # MACD EMA smoothing factor
    ema_macd = 0

    ema_fast_values = [] # track fast EMA values for visualization purposes
    ema_slow_values = [] # track slow EMA values for visualization purposes
    macd_values = [] # track MACD values for visualization purposes
    macd_signal_values = [] # MACD EMA values tracker
    macd_historgram_values = [] # MACD - MACD-EMA
    for close_price in close:
        if (ema_fast == 0): # first observation
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_fast + ema_fast
            ema_slow = (close_price - ema_slow) * K_slow + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)

        macd = ema_fast - ema_slow # MACD is fast_MA - slow_EMA
        if ema_macd == 0:
            ema_macd = macd
        else:
            ema_macd = (macd - ema_macd) * K_macd + ema_macd # signal is EMA of MACD values

        macd_values.append(macd)
        macd_signal_values.append(ema_macd)
        macd_historgram_values.append(macd - ema_macd)

    goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
    goog_data = goog_data.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=goog_data.index))
    goog_data = goog_data.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=goog_data.index))
    goog_data = goog_data.assign(MovingAverageConvergenceDivergence=pd.Series(macd_values, index=goog_data.index))
    goog_data = goog_data.assign(Exponential20DayMovingAverageOfMACD=pd.Series(macd_signal_values, index=goog_data.index))
    goog_data = goog_data.assign(MACDHistorgram=pd.Series(macd_historgram_values, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    ema_f = goog_data['FastExponential10DayMovingAverage']
    ema_s = goog_data['SlowExponential40DayMovingAverage']
    macd = goog_data['MovingAverageConvergenceDivergence']
    ema_macd = goog_data['Exponential20DayMovingAverageOfMACD']
    macd_histogram = goog_data['MACDHistorgram']

    goog_data['signal'] =\
        np.where(goog_data['MovingAverageConvergenceDivergence'][0:]
                                                > goog_data['Exponential20DayMovingAverageOfMACD'][0:], 1.0, 0.0)
    goog_data['orders'] = goog_data['signal'].diff()

    return goog_data['orders'].iloc[-1] > 0.0

def macd_line_over_than_signal(pd_dataframe, short, long, signal):
    goog_data = pd_dataframe
    close = goog_data['trade_price']

    num_periods_fast = short # fast EMA time period
    K_fast = 2 / (num_periods_fast + 1) # fast EMA smoothing factor
    ema_fast = 0
    num_periods_slow = long # slow EMA time period
    K_slow = 2 / (num_periods_slow + 1) # slow EMA smoothing factor
    ema_slow = 0
    num_periods_macd = signal # MACD EMA time period
    K_macd = 2 / (num_periods_macd + 1) # MACD EMA smoothing factor
    ema_macd = 0

    ema_fast_values = [] # track fast EMA values for visualization purposes
    ema_slow_values = [] # track slow EMA values for visualization purposes
    macd_values = [] # track MACD values for visualization purposes
    macd_signal_values = [] # MACD EMA values tracker
    macd_historgram_values = [] # MACD - MACD-EMA
    for close_price in close:
        if (ema_fast == 0): # first observation
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_fast + ema_fast
            ema_slow = (close_price - ema_slow) * K_slow + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)

        macd = ema_fast - ema_slow # MACD is fast_MA - slow_EMA
        if ema_macd == 0:
            ema_macd = macd
        else:
            ema_macd = (macd - ema_macd) * K_macd + ema_macd # signal is EMA of MACD values

        macd_values.append(macd)
        macd_signal_values.append(ema_macd)
        macd_historgram_values.append(macd - ema_macd)

    goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
    goog_data = goog_data.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=goog_data.index))
    goog_data = goog_data.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=goog_data.index))
    goog_data = goog_data.assign(MovingAverageConvergenceDivergence=pd.Series(macd_values, index=goog_data.index))
    goog_data = goog_data.assign(Exponential20DayMovingAverageOfMACD=pd.Series(macd_signal_values, index=goog_data.index))
    goog_data = goog_data.assign(MACDHistorgram=pd.Series(macd_historgram_values, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    ema_f = goog_data['FastExponential10DayMovingAverage']
    ema_s = goog_data['SlowExponential40DayMovingAverage']
    macd = goog_data['MovingAverageConvergenceDivergence']
    ema_macd = goog_data['Exponential20DayMovingAverageOfMACD']
    macd_histogram = goog_data['MACDHistorgram']

    goog_data['signal'] =\
        np.where(goog_data['MovingAverageConvergenceDivergence'][0:]
                                                > goog_data['Exponential20DayMovingAverageOfMACD'][0:], 1.0, 0.0)
    goog_data['orders'] = goog_data['signal'].diff()

    return goog_data['MovingAverageConvergenceDivergence'].iloc[-1] > goog_data['Exponential20DayMovingAverageOfMACD'].iloc[-1]
    

def macd2(df, period1, period2, period3): # default MACD period values are: period1 = 26, period2 = 12, period3 = 9.
    EMA_1 = df['trade_price'].ewm(span=period1, adjust=False).mean()
    EMA_2 = df['trade_price'].ewm(span=period2, adjust=False).mean()
    MACD_line = EMA_1 - EMA_2
    MACD_Signal_line = MACD_line.ewm(span=period3, adjust=False).mean()
    MACD_Histogram = MACD_line - MACD_Signal_line
    return MACD_line, MACD_Signal_line, MACD_Histogram


def macd_line_over_than_signal2(pd_dataframe, short, long, signal):
    MACD_line, MACD_Signal_line, MACD_Histogram = macd2(pd_dataframe, short, long, signal)
    return MACD_Histogram.iloc[-1] > 0
