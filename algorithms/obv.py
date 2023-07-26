import pandas as pd
from pandas_datareader import data

def obv(pd_dataframe):
    # obv가 저장될 pandas series를 생성
    pd_dataframe['obv'] = pd.Series(index=pd_dataframe['trade_price'].index)
    pd_dataframe['obv'].iloc[0] = pd_dataframe['candle_acc_trade_volume'].iloc[0]
    
    # OBV 산출공식을 구현
    # pd.Series 구조를 연산에 직접 사용
    for i in range(1,len(pd_dataframe)):
        if pd_dataframe['trade_price'].iloc[i] > pd_dataframe['trade_price'].iloc[i-1] : 
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] + pd_dataframe['candle_acc_trade_volume'].iloc[i]
            
        elif pd_dataframe['trade_price'].iloc[i] < pd_dataframe['trade_price'].iloc[i-1] :
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] - pd_dataframe['candle_acc_trade_volume'].iloc[i]
            
        else:
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1]

    return pd_dataframe['obv']

def obv_is_good(pd_dataframe):
    # obv가 저장될 pandas series를 생성
    pd_dataframe['obv'] = pd.Series(index=pd_dataframe['trade_price'].index)
    pd_dataframe['obv'].iloc[0] = pd_dataframe['trade_volume'].iloc[0]
    
    # OBV 산출공식을 구현
    # pd.Series 구조를 연산에 직접 사용
    for i in range(1,len(pd_dataframe)):
        if pd_dataframe['trade_price'].iloc[i] > pd_dataframe['trade_price'].iloc[i-1] : 
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] + pd_dataframe['trade_volume'].iloc[i]
            
        elif pd_dataframe['trade_price'].iloc[i] < pd_dataframe['trade_price'].iloc[i-1] :
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] - pd_dataframe['trade_volume'].iloc[i]
            
        else:
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1]

    pd_dataframe['obv_ema'] = pd_dataframe['obv'].ewm(com=10).mean()

    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, ylabel='Google price in $')
    # pd_dataframe['obv'].plot(ax=ax1, color='g', lw=2., legend=True)
    # pd_dataframe['obv_ema'] .plot(ax=ax1, color='b', lw=2., legend=True)
    # plt.show()

    return pd_dataframe['obv'].iloc[-1] > pd_dataframe['obv_ema'].iloc[-1]

def get_obv(pd_dataframe, period):
    # obv가 저장될 pandas series를 생성
    pd_dataframe['obv'] = pd.Series(index=pd_dataframe['trade_price'].index)
    pd_dataframe['obv'].iloc[0] = pd_dataframe['trade_volume'].iloc[0]
    
    # OBV 산출공식을 구현
    # pd.Series 구조를 연산에 직접 사용
    for i in range(1,len(pd_dataframe)):
        if pd_dataframe['trade_price'].iloc[i] > pd_dataframe['trade_price'].iloc[i-1] : 
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] + pd_dataframe['trade_volume'].iloc[i]
            
        elif pd_dataframe['trade_price'].iloc[i] < pd_dataframe['trade_price'].iloc[i-1] :
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1] - pd_dataframe['trade_volume'].iloc[i]
            
        else:
            pd_dataframe['obv'].iloc[i] = pd_dataframe['obv'].iloc[i-1]

    pd_dataframe['obv_ema'] = pd_dataframe['obv'].ewm(com=period).mean()
    return pd_dataframe['obv'], pd_dataframe['obv_ema']

    #return pd_dataframe['obv'].iloc[-1] > pd_dataframe['obv_ema'].iloc[-1]