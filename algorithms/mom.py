import pandas as pd

from pandas_datareader import data

def momentum(pd_dataframe):
    goog_data = pd_dataframe
    close = goog_data['trade_price']

    time_period = 10 # how far to look back to find reference price to compute momentum
    history = [] # history of observed prices to use in momentum calculation
    mom_values = [] # track momentum values for visualization purposes

    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # history is at most 'time_period' number of observations
            del (history[0])

        mom = close_price - history[0]
        mom_values.append(mom)

    goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
    goog_data = goog_data.assign(MomentumFromPrice20DaysAgo=pd.Series(mom_values, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    mom = goog_data['MomentumFromPrice20DaysAgo']
    return goog_data
    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(211, ylabel='Google price in $')
    # close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    # ax2 = fig.add_subplot(212, ylabel='Momentum in $')
    # mom.plot(ax=ax2, color='b', lw=2., legend=True)
    # plt.show()

def is_increase_momentum(pd_dataframe):
    goog_data = momentum(pd_dataframe)
    emov4 = goog_data['MomentumFromPrice20DaysAgo'].ewm(span=3).mean()
    emov8 = goog_data['MomentumFromPrice20DaysAgo'].ewm(span=7).mean()

    # print(goog_data['MomentumFromPrice20DaysAgo'].iloc[-1])
    # print(emov5.iloc[-1])
    # print(emov10.iloc[-1])

    # import matplotlib.pyplot as plt
    # if goog_data['MomentumFromPrice20DaysAgo'].iloc[-1] > emov5.iloc[-1] and  emov5.iloc[-1] > emov10.iloc[-1]:
    #     fig = plt.figure()
    #     ax1 = fig.add_subplot(111, ylabel='Google price in $')
    #     goog_data['MomentumFromPrice20DaysAgo'].plot(ax=ax1, color='r', lw=2., legend=True)
    #     emov5.plot(ax=ax1, color='g', lw=2., legend=True)
    #     emov10.plot(ax=ax1, color='b', lw=2., legend=True)
    #     plt.show()

    return emov4.iloc[-1] > emov8.iloc[-1]
    #return goog_data['MomentumFromPrice20DaysAgo'].iloc[-1] >= emov3.iloc[-1] and emov3.iloc[-1] > emov7.iloc[-1]


