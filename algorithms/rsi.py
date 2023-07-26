import pandas as pd

from pandas_datareader import data

import statistics as stats

def rsi(pd_dataframe ,period):
    close = pd_dataframe['trade_price']
    time_period = period # look back period to compute gains & losses
    gain_history = [] # history of gains over look back period (0 if no gain, magnitude of gain if gain)
    loss_history = [] # history of losses over look back period (0 if no loss, magnitude of loss if loss)
    avg_gain_values = [] # track avg gains for visualization purposes
    avg_loss_values = [] # track avg losses for visualization purposes
    rsi_values = [] # track computed RSI values
    last_price = 0 # current_price - last_price > 0 => gain. current_price - last_price < 0 => loss.

    for close_price in close:
        if last_price == 0:
            last_price = close_price

        gain_history.append(max(0, close_price - last_price))
        loss_history.append(max(0, last_price - close_price))
        last_price = close_price

        if len(gain_history) > time_period: # maximum observations is equal to lookback period
            del (gain_history[0])
            del (loss_history[0])

        avg_gain = stats.mean(gain_history) # average gain over lookback period
        avg_loss = stats.mean(loss_history) # average loss over lookback period

        avg_gain_values.append(avg_gain)
        avg_loss_values.append(avg_loss)

        rs = 0
        if avg_loss > 0: # to avoid division by 0, which is undefined
            rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(RelativeStrengthAvgGainOver20Days=pd.Series(avg_gain_values, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(RelativeStrengthAvgLossOver20Days=pd.Series(avg_loss_values, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(RelativeStrengthIndicatorOver20Days=pd.Series(rsi_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    rs_gain = pd_dataframe['RelativeStrengthAvgGainOver20Days']
    rs_loss = pd_dataframe['RelativeStrengthAvgLossOver20Days']
    rsi = pd_dataframe['RelativeStrengthIndicatorOver20Days']
    return rsi

    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(311, ylabel='Google price in $')
    # close_price.plot(ax=ax1, color='black', lw=2., legend=True)
    # ax2 = fig.add_subplot(312, ylabel='RS')
    # rs_gain.plot(ax=ax2, color='g', lw=2., legend=True)
    # rs_loss.plot(ax=ax2, color='r', lw=2., legend=True)
    # ax3 = fig.add_subplot(313, ylabel='RSI')
    # rsi.plot(ax=ax3, color='b', lw=2., legend=True)
    # plt.show()

def get_current_rsi(pd_dataframe, period):
        price_list = []
        rsi_list = []
        price_list = pd_dataframe['trade_price']        
        rsi_list.append(rsi_calculate(price_list, period, int(len(price_list))))
        return rsi_list[0]

#RSI계산 함수
def rsi_calculate( l, n, sample_number): #l = price_list, n = rsi_number
    
    diff=[]
    au=[]
    ad=[]

    if len(l) != sample_number: #url call error
        return -1 
    for i in range(len(l)-1):
        diff.append(l[i+1]-l[i]) #price difference
    
    au = pd.Series(diff) #list to series
    ad = pd.Series(diff)

    au[au<0] = 0 #remove ad
    ad[ad>0] = 0 #remove au

    _gain = au.ewm(com = n, min_periods = sample_number -1).mean() #Exponentially weighted average
    _loss = ad.abs().ewm(com = n, min_periods = sample_number -1).mean()
    RS = _gain/_loss

    rsi = 100-(100 / (1+RS.iloc[-1]))

    return rsi
