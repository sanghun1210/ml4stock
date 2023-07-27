# !pip install prophet
from prophet import Prophet
import algorithms

def pattern1_check(daily_df, weekly_df, monthly_df):
    monthly_sma = algorithms.sma(monthly_df, 10)
    if monthly_sma.iloc[-1] <= monthly_df['trade_price'].iloc[-1]:
        slow_k, slow_d = algorithms.stc_slow(weekly_df, 9, 3, 3)
        if slow_d.iloc[-1] < 40 :
            daily_sma = algorithms.sma(daily_df, 20)
            if algorithms.macd_line_over_than_signal2(daily_df, 12, 26, 9) :
                return True
    return False


def prophet_check(daily_df, weekly_df, monthly_df):
    # Prophet 모델 초기화
    model = Prophet()

    # 모델 훈련
    model.fit(daily_df)

    # 향후 365일 동안의 예측 생성
    future = model.make_future_dataframe(periods=100)
    forecast = model.predict(future)
    