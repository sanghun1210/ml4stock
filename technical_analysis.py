# !pip install prophet
# pip install -U scikit-learn
#from prophet import Prophet
import matplotlib.pyplot as plt
import algorithms
import numpy as np

def pattern1_check(daily_df, weekly_df):
    daily_df['SMA1'] = daily_df['trade_price'].rolling(window=42).mean()
    daily_df['SMA2'] = daily_df['trade_price'].rolling(window=252).mean()
    daily_df['position'] = np.where(daily_df['SMA1'] > daily_df['SMA2'], 1, -1)

    cci252 = algorithms.get_current_cci(daily_df, 252)

    if daily_df['position'].iloc[-1] == 1 and cci252 < 50:
        slow_k, slow_d = algorithms.stc_slow(weekly_df, 9, 3, 3)
        if slow_d.iloc[-1] < 35 :
            daily_sma = algorithms.sma(daily_df, 20)
            if algorithms.macd_line_over_than_signal2(daily_df, 12, 26, 9) :
                return True
    return False

def pattern2_check(daily_df, weekly_df):
    res = algorithms.adx(weekly_df['high_price'], weekly_df['low_price'], weekly_df['trade_price'], 14)
    cci14 = algorithms.get_current_cci(weekly_df, 14)
    if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and \
        res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] and \
        algorithms.macd_line_over_than_signal2(weekly_df, 12, 26, 9) and \
        cci14 < 20 :
        res_day = algorithms.adx(daily_df['high_price'], daily_df['low_price'], daily_df['trade_price'], 14)
        if res_day['DMP_14'].iloc[-1] > res_day['DMN_14'].iloc[-1] and \
            res_day['ADX_14'].iloc[-1] < res_day['DMP_14'].iloc[-1] and \
            res_day['ADX_14'].iloc[-1] > res_day['ADX_14'].iloc[-5] :
            return True
    return False

def pattern3_check(weekly_df) :
    res = algorithms.adx(weekly_df['high_price'], weekly_df['low_price'], weekly_df['trade_price'], 14)
    cci14 = algorithms.get_current_cci(weekly_df, 14)
    if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and \
        res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] and cci14 < 50 :
        return True
    return False

def value_check(weekly_df, good_value) :
    print("trade_price : {0}, good_value : {1}".format(weekly_df['trade_price'].iloc[-1],good_value))
    return weekly_df['trade_price'].iloc[-1]< good_value

# sklearn logisticRegression by daily_df
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def logistic_regression(daily_df):
    daily_df['return'] = np.log(daily_df['trade_price'] / daily_df['trade_price'].shift(1))
    daily_df.dropna(inplace=True)
    lags = 3
    cols = []
    for lag in range(1, lags+1):
        col = f'lag_{lag}'
        daily_df[col] = daily_df['return'].shift(lag)
        cols.append(col)

    daily_df.dropna(inplace=True)
    
    lm = LogisticRegression(C=1e5, solver='lbfgs', multi_class='auto',  max_iter=1000)

    lm.fit(daily_df[cols], np.sign(daily_df['return']))
    print(lm.coef_)
    print(lm.intercept_)

    daily_df['pred'] = lm.predict(daily_df[cols])
    
    hits = (daily_df['pred'] == np.sign(daily_df['return'])).sum()
    print('hits : ', hits)

    print('accuracy : ', accuracy_score(daily_df['pred'], np.sign(daily_df['return'])))
    daily_df['strategy'] = daily_df['pred'] * daily_df['return']
    print(daily_df[['return', 'strategy','pred']].tail(50))
    daily_df[['return', 'strategy']].cumsum().apply(np.exp).plot(figsize=(10, 6))
    #print(daily_df.tail(50))
    #plt.show()


    
    