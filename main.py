# pip3 install pykrx
from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd

from .technical_analysis import pattern1_check

def is_fundamental_pbr_good(stock_code):
    try:
        now = datetime.now()
        # 날짜를 문자열로 변환 (YYYY-MM-DD 형식)
        date_string = now.strftime("%Y-%m-%d")
        df = stock.get_market_fundamental(date_string, date_string, stock_code)
        return df['PBR'].iloc[0] < 3
    except Exception as e:    
        return False

def get_daily_data(stock_code):
    try:
        # 현재 날짜 구하기
        current_date = datetime.now()
        result_date = current_date - timedelta(days=365)

        current_date_string = current_date.strftime('%Y-%m-%d')
        result_date_string = result_date.strftime('%Y-%m-%d')

        df = stock.get_market_ohlcv_by_date(result_date_string, current_date_string, stock_code)
        return df
    except:
        empty_df = pd.DataFrame()
        return empty_df

# 데이터프레임이 비어있는지 체크하는 함수
def is_dataframe_empty(df):
    return df.empty

def rename_stock_column(df):
    new_column_names = {
        '시가': 'open_price',
        '고가': 'high_price',
        '저가': 'low_price',
        '종가': 'trade_price',
        '거래량': 'volume',
    }
    df.rename(columns=new_column_names, inplace=True)
    return df

def resample_to_week(df):
    resampled_data = {
    'open_price': 'first',
    'high_price': 'max',
    'low_price': 'min',
    'trade_price': 'last',
    'volume': 'sum',
    }

    df_weekly = df.resample('W').agg(resampled_data)
    return df_weekly

def resample_to_month(df):
    resampled_data = {
    'open_price': 'first',
    'high_price': 'max',
    'low_price': 'min',
    'trade_price': 'last',
    'volume': 'sum',
    }

    df_monthly = df.resample('M').agg(resampled_data)
    return df_monthly


def main():
    try:
        tickers = stock.get_market_ticker_list(market="KOSDAQ")
        tickers.append(stock.get_market_ticker_list(market="KOSPI"))

        for ticker in tickers :
            print(ticker)
            if is_fundamental_pbr_good(ticker) == False: 
                continue

            df = get_daily_data(ticker)
            if is_dataframe_empty(df) == False:
                daily_df = rename_stock_column(df)
                weekly_df = resample_to_week(daily_df)  
                monthly_df = resample_to_month(daily_df)
                if pattern1_check(daily_df, weekly_df, monthly_df) : 
                    print('wow :' , ticker)

    except Exception as e:    
        print("raise error ", e)

if __name__ == "__main__":
    # execute only if run as a script
    main()