import pandas as pd
import datetime
import requests
import math
from io import StringIO

class InvestorTrends():
    def __init__(self, ticker):
        self.df = None
        self.init_ts(ticker)

    def init_ts(self, ticker) :
        try:

            url = f'https://finance.naver.com/item/frgn.naver?code={ticker}'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            self.df = pd.read_html(StringIO(res.text))[2]
            self.df.columns = self.df.columns.droplevel(1)
            self.df = self.df.dropna(subset=['날짜'])
        except Exception as e:
            print("raise error ", e)

    def get_cumulative_trading_volume_agency(self, period):
        try:
            df = self.df.iloc[:, :-2]
            sum = df.iloc[0:period, df.columns.get_loc('기관')].sum()
            return sum
            
        except Exception as e:
            print("raise error ", e)
            return 0

    def get_cumulative_trading_volume_foreigner(self, period):
        try:
            # 불필요한 컬럼 제거
            df = self.df.iloc[:, :-2]
            df.to_csv('abc')
            sum = df.iloc[0:period, df.columns.get_loc('외국인')].sum()
            return sum
        except Exception as e:
            print("raise error ", e)
            return 0

    def get_buy_day_count_foreigner(self, period):
        try:
            item_len = len(self.df)
            print(self.df)
            pds = pd.Series(self.df['외국인'].items())
            sum = 0
            count = 0
            for row in pds[0][1]:
                sale_volume = row
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue

                if float(sale_volume) > 0:
                    sum += 1
                
                count += 1
                if count == period:
                    break
            return sum
        except Exception as e:
            print("raise error ", e)
            return 0

    def get_buy_day_count_agency(self, period):
        try:
            item_len = len(self.df)
            sum = 0
            count = 0
            for i in range(0, item_len):
                sale_volume = self.df['기관'].iloc[i]
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue

                if float(sale_volume) > 0:
                    sum += 1
                count += 1
                if count == period:
                    break
            return sum
        except Exception as e:
            print("raise error ", e)
            return 0

if __name__ == "__main__":
    fs = InvestorTrends('053290')
    print(fs.get_cumulative_trading_volume_agency(20))
    print(fs.get_cumulative_trading_volume_foreigner(20))







