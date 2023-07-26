import pandas as pd
import pandas_ta as ta
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time


def tr(data):
    data['previous_close'] = data['trade_price'].shift(1)
    data['high-low'] = abs(data['high_price'] - data['low_price'])
    data['high-pc'] = abs(data['high_price'] - data['previous_close'])
    data['low-pc'] = abs(data['low_price'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()
    return atr

def supertrend(df, period=7, atr_multiplier=2):
    ST = ta.supertrend(df['high_price'], df['low_price'], df['trade_price'], 7, 2)
    ST.rename(columns = {'SUPERTd_7_2.0' : 'SUPERTd_7_2'}, inplace = True)
    # print(ST)

    import matplotlib.pyplot as plt


    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, ylabel='Google price in $')
    # df["trade_price"].plot(ax=ax1, color='g', lw=.5)
    # ax1.plot(df.loc[ST.SUPERTd_7_3 == 1.0].index,
    #         df["trade_price"][ST.SUPERTd_7_3 == 1.0],
    #         '^', markersize=7, color='k')

    # ax1.plot(df.loc[ST.SUPERTd_7_3 == -1.0].index,
    #         df["trade_price"][ST.SUPERTd_7_3  == -1.0],
    #         'v', markersize=7, color='k')

    # plt.legend(["Price","Short mavg","Long mavg","Buy","Sell"])
    # plt.title("Double Moving Average Trading Strategy")

    # plt.show()

    return ST

def is_supertrend_signal(df):
    ST = supertrend(df)
    sut_list = ST['SUPERTd_7_2']

    first = sut_list.iloc[0]
    for i in range(1,len(sut_list)):
        if first == sut_list.iloc[i]:
            sut_list.iloc[i] = 0
        else:
            first = sut_list.iloc[i]

    return ST['SUPERTd_7_2'].iloc[-2] > 0 or ST['SUPERTd_7_2'].iloc[-3] > 0  

#    return ST['SUPERTd_7_2'].iloc[-2] > 0

in_position = False

def plot_trend(df):
    global in_position

    # print("checking for buy and sell signals")
    # print(df.tail(5))
    # last_row_index = len(df.index) - 1
    # previous_row_index = last_row_index - 1


    df['signal'] = pd.Series(np.zeros(len(df)))

    for i in range(1,len(df)):
        if df['in_uptrend'].iloc[i]: 
            df['signal'].iloc[i] = 1.0
            
        else:
            df['signal'].iloc[i] = 0.0
    
    df['orders'] = df['signal'].diff()

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    df["trade_price"].plot(ax=ax1, color='g', lw=.5)
    ax1.plot(df.loc[df.orders== 1.0].index,
            df["trade_price"][df.orders == 1.0],
            '^', markersize=7, color='k')

    ax1.plot(df.loc[df.orders== -1.0].index,
            df["trade_price"][df.orders == -1.0],
            'v', markersize=7, color='k')

    plt.legend(["Price","Short mavg","Long mavg","Buy","Sell"])
    plt.title("Double Moving Average Trading Strategy")

    plt.show()
    # if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
    #     print("changed to uptrend, buy")
    #     if not in_position:
    #         order = exchange.create_market_buy_order('ETH/USD', 0.05)
    #         print(order)
    #         in_position = True
    #     else:
    #         print("already in position, nothing to do")
    
    # if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
    #     if in_position:
    #         print("changed to downtrend, sell")
    #         order = exchange.create_market_sell_order('ETH/USD', 0.05)
    #         print(order)
    #         in_position = False
    #     else:
    #         print("You aren't in position, nothing to sell")

