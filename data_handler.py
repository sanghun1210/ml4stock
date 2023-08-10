from pykrx import stock
from pykrx import bond
import pandas as pd

class StockDataHandler(object):
    def __init__(self, stock_code, start_date, end_date):
        self.stock_code = stock_code
        self.start_date = start_date
        self.end_date = end_date
        self.daily_data = pd.DataFrame()
        self.weekly_data = pd.DataFrame()
        self.get_data()

    def rename_stock_column(self, df):
        new_column_names = {
            '시가': 'open_price',
            '고가': 'high_price',
            '저가': 'low_price',
            '종가': 'trade_price',
            '거래량': 'volume',
        }
        df.rename(columns=new_column_names, inplace=True)
        return df

    def get_data(self):
        try:
            df = stock.get_market_ohlcv_by_date(self.start_date, self.end_date, self.stock_code)
            self.daily_data = self.rename_stock_column(df)
        except:
            self.daily_data = pd.DataFrame()
    
    def resample_to_week(self, df):
        resampled_data = {
        'open_price': 'first',
        'high_price': 'max',
        'low_price': 'min',
        'trade_price': 'last',
        'volume': 'sum',
        }
        df_weekly = df.resample('W').agg(resampled_data)
        return df_weekly

    def resample_to_month(self, df):
        resampled_data = {
        'open_price': 'first',
        'high_price': 'max',
        'low_price': 'min',
        'trade_price': 'last',
        'volume': 'sum',
        }
        df_monthly = df.resample('M').agg(resampled_data)
        return df_monthly

    def get_daily_data(self):
        return self.daily_data
    
    def get_weekly_data(self):
        if self.weekly_data.empty:
            self.weekly_data = self.resample_to_week(self.daily_data) 
        return self.weekly_data
    
    def check_valid_data(self):
        if self.daily_data.empty:
            return False
        if len(self.daily_data) < 200:
            return False
        return True