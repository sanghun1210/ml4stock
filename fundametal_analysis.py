from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import math

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
        self.start = start
        self.end = end
        self.ticker = ticker
        self.current_eps = 0
        self.current_per = 0
        self.current_bps = 0
        self.current_pbr = 0
        self.current_roe = 0
        self.sector = None
        self.annual_date = None
        self.quater_date = None
        self.naver_df = None
        self.is_empty = True
        self.get_data()
        

    def get_data(self):
        '''종목코드의 재무데이터를 조회한다.'''
        self.data = stock.get_market_fundamental(self.start, self.end, self.ticker, freq='m')
        if self.data.empty:
            return 
         
        self.current_bps = self.data['BPS'].iloc[-1]
        self.current_per = self.data['PER'].iloc[-1]
        self.current_eps = self.data['EPS'].iloc[-1]
        self.current_pbr = self.data['PBR'].iloc[-1]

        if self.current_per == 0: self.current_per = self.get_current_quater_data_from_naver('PER')
        if self.current_eps == 0: self.current_eps = self.get_current_quater_data_from_naver('EPS') 
        if self.current_pbr == 0: self.current_pbr = self.get_current_quater_data_from_naver('PBR') 
        if self.current_roe == 0: self.current_roe = self.get_current_quater_data_from_naver('ROE') 

        self.get_sector_from_naver()
        self.is_empty = False

    # def get_data(self):
    #     '''종목코드의 재무데이터를 조회한다.'''
    #     try:
    #         self.current_per = self.get_current_quater_data_from_naver('PER')
    #         self.current_eps = self.get_current_quater_data_from_naver('EPS') 
    #         self.current_pbr = self.get_current_quater_data_from_naver('PBR') 
    #         self.get_sector_from_naver()
    #         self.is_empty = False
    #     except Exception as e:
    #         print("Error get_data : ", e)

    def print_fundamental(self):
        print(self.data.tail(50))

    def get_data_from_naver(self):
        try:
            url = f'https://finance.naver.com/item/main.nhn?code={self.ticker}'
            #req.add_header('User-Agent', 'Mozilla/5.0')
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            cop = soup.select_one('#content > div.section.cop_analysis')

            df = pd.read_html(cop.prettify())[0]
            df.set_index(df.columns[0], inplace=True)
            df.index.rename('주요재무정보', inplace=True)
            #print(df)

            # 'IFRS연결' 행 버림
            df.columns = df.columns.droplevel(2)
            #print(df.head(10))

            self.annual_date = df['최근 연간 실적']
            self.quater_date = df['최근 분기 실적']
        except Exception as e:
            print("Error get_data_from_naver : ", e)

    def get_current_quater_data_from_naver(self, index_string):
        import re
        if self.naver_df is None:
            self.get_data_from_naver()
        try:
            search_pattern = index_string
            matching_indices = self.quater_date[self.quater_date.index.to_series().str.contains(search_pattern, flags=re.IGNORECASE)]
            desired_row = matching_indices.iloc[0]
            row_as_list = desired_row.tolist()
            for item in reversed(row_as_list):
                if math.isnan(float(item)):
                    continue
                break
            return item

        except Exception as e:
            print("Error get_current_quater_data_from_naver : ", e)
            return -1
    
    
    def get_sector_from_naver(self):
        # 종목 페이지 URL 생성
        try:
            url = f'https://finance.naver.com/item/main.nhn?code={self.ticker}'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 업종명 추출
            industry_name = soup.select_one('#content > div.section.trade_compare > h4 > em > a')
            self.sector = industry_name.text
        except Exception as e:
            print("Error get_sector_from_naver : ", e)

    def print_data(self):
        print('bps: ', self.current_bps)
        print('per: ', self.current_per)
        print('eps: ', self.current_eps)
        print('pbr: ', self.current_pbr)
        print('roe: ', self.current_roe)
        print('sector: ', self.sector)

    def get_same_industry_per(self):
        try:
            url = f'https://finance.naver.com/item/main.nhn?code={self.ticker}'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 업종명 추출
            industry_per = soup.select_one('#tab_con1 > div:nth-child(6) > table') 
            #print(industry_pbr.find('em').get_text())
            return float(industry_per.find('em').get_text())
        except Exception as e:
            print("Error get_same_industry_per : ", e)
            return 0
        
    def is_good_per_to_buy(self):
        if float(self.current_per) < self.get_same_industry_per() and float(self.current_per) < 25:
            return True
        else:
            return False
        
    def get_good_stock_value(self):
        return self.current_eps * self.current_roe

def main():
    current_date = datetime.now()
    result_date = current_date - timedelta(days=450)

    end_date = current_date.strftime('%Y-%m-%d')
    start_date = result_date.strftime('%Y-%m-%d')

    #fs = FundamentalSector(end_date)
    #fs.print_kospi_data()
    fa = FundamentalAnalysis('365550', start_date, end_date)
    fa.get_same_industry_pbr()
    # fa.get_data_from_naver()
    # roe = fa.get_current_roe_from_naver()
    # print(roe)

if __name__ == "__main__":
    # execute only if run as a script
    main()


    