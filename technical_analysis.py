from . import algorithms

def pattern1_check(daily_df, weekly_df, monthly_df):
    monthly_sma = algorithms.sma(monthly_df, 10)
    if monthly_sma.iloc[-1] <= monthly_df['trade_price'].iloc[-1]:
        slow_k, slow_d = algorithms.stc_slow(weekly_df, 9, 3, 3)
        if slow_d.iloc[-1] < 35 :
            daily_sma = algorithms.sma(daily_df, 20)
            if daily_sma.iloc[-1] < daily_sma['trade_price'].iloc[-1]:
                return True
    return False
    