from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd

class FundamentalSector(object):
    def __init__(self, date):
        self.df_kosdaq = None
        self.df_kospi = None
        self.date = date
        self.get_kospi_data()
        self.get_kosdaq_data()

    def get_kospi_data(self):
        if self.df_kospi is None:
            self.df_kospi = stock.get_index_fundamental(self.date, market="KOSPI")
        return self.df_kosdaq, self.df_kospi
    
    def get_kosdaq_data(self):
        if self.df_kosdaq is None:
            self.df_kosdaq = stock.get_index_fundamental(self.date, market="KOSDAQ")
        return self.df_kosdaq
    
    def print_kospi_data(self):
        print(self.df_kospi)

    def print_kosdaq_data(self):
        print(self.df_kosdaq)

class FundamentalAnalysis(object):
    def __init__(self, ticker, start, end):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.get_data()

    def get_data(self):
        '''종목코드의 재무데이터를 조회한다.'''
        self.data = stock.get_market_fundamental(self.start, self.end, self.ticker)

    def print_fundamental(self):
        print(self.data.tail())

    # def is_fundamental_pbr_is_higher(stock_code):
    #     try:
    #         now = datetime.now()
    #         # 날짜를 문자열로 변환 (YYYY-MM-DD 형식)
    #         date_string = now.strftime("%Y-%m-%d")
            
    #         print(df)
    #         is_pbr_higher = df['PBR'].iloc[0] >= 3.2 
    #         if is_pbr_higher : 
    #             raise Exception('pbr is higher')  
    #         return is_pbr_higher
    #     except Exception as e:    
    #         print("error :  ", e) 
    #         return True

def main():
    current_date = datetime.now()
    result_date = current_date - timedelta(days=450)

    end_date = current_date.strftime('%Y-%m-%d')
    start_date = result_date.strftime('%Y-%m-%d')

    fs = FundamentalSector(end_date)
    fs.print_kosdaq_data()
    fa = FundamentalAnalysis('016100', start_date, end_date)
    fa.print_fundamental()


if __name__ == "__main__":
    # execute only if run as a script
    main()


    