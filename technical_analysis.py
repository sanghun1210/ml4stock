# !pip install prophet
#from prophet import Prophet
import algorithms

def pattern1_check(daily_df, weekly_df, monthly_df):
    monthly_sma = algorithms.sma(monthly_df, 10)
    if monthly_sma.iloc[-1] <= monthly_df['trade_price'].iloc[-1]:
        slow_k, slow_d = algorithms.stc_slow(weekly_df, 9, 3, 3)
        if slow_d.iloc[-1] < 35 :
            daily_sma = algorithms.sma(daily_df, 20)
            if algorithms.macd_line_over_than_signal2(daily_df, 12, 26, 9) :
                return True
    return False

def pattern2_check(daily_df, weekly_df, monthly_df):
    res = algorithms.adx(weekly_df['high_price'], weekly_df['low_price'], weekly_df['trade_price'], 14)
    cci14 = algorithms.get_current_cci(weekly_df, 14)
    if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and \
        res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] and \
        algorithms.macd_line_over_than_signal2(weekly_df, 12, 26, 9) and \
        cci14 < 20 :
        slow_k, slow_d = algorithms.stc_slow(daily_df, 7, 3, 3)
        if slow_d.iloc[-1] < 45 and slow_k.iloc[-1] < slow_d.iloc[-1] :
            return True
    return False




    

# def prophet_check(daily_df, weekly_df, monthly_df):
#     df = daily_df.copy()
#     # Prophet 입력 형식에 맞게 데이터 전처리
#     df = df.reset_index()
#     df = df.rename(columns={"날짜": "ds", "trade_price": "y"})
#     # Prophet 모델 초기화
#     print(df)
#     model = Prophet()

#     # 모델 훈련
#     model.fit(df)

#     # 향후 365일 동안의 예측 생성
#     future = model.make_future_dataframe(periods=100)
#     forecast = model.predict(future)
    