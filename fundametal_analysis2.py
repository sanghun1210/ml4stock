from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import math


class FundamentalAnalysis2(object):
    def __init__(self, ticker):
        self.current_eps = 0
        self.current_per = 0
        self.current_bps = 0
        self.current_pbr = 0
        self.current_roe = 0
        self.sector = None
        self.annual_date = None
        self.quater_date = None
        self.df = None
        self.table_token = None
        self.soup = None
        self.get_data_from_fnguide(ticker)
        
    def is_sequentially_increasing(self, lst):
        # 리스트의 길이가 1 이하면, 자동으로 순차적으로 커지는 것으로 간주
        if len(lst) <= 1:
            return True
        
        # 리스트의 각 요소를 순회하면서 이전 요소와 비교
        for i in range(1, len(lst)):
            # 현재 요소가 이전 요소보다 작으면, 순차적으로 커지지 않음
            if lst[i] < lst[i-1]:
                return False
        
        # 모든 검사를 통과하면 순차적으로 커지는 것임
        return True
    
    def is_last_item_largest(self,lst):
        # 리스트가 비어있거나 하나의 요소만 있는 경우를 처리
        if not lst or len(lst) == 1:
            return True
        # 리스트의 마지막 요소가 리스트 내의 모든 요소 중 가장 큰지 확인
        return lst[-1] == max(lst)
    
    def is_last_item_smallest(self, lst):
        # 리스트가 비어있거나 하나의 요소만 있는 경우를 처리
        if not lst or len(lst) == 1:
            return True
        # 리스트의 마지막 요소가 리스트 내의 모든 요소 중 가장 작은지 확인
        return lst[-1] == min(lst)
    
    def check_increase_by_10_percent(self, values):
        # 리스트의 길이가 2 이상인지 확인
        if len(values) < 2:
            return False
        
        # 마지막 항목과 그 이전 항목을 추출
        last_item = values[-1]
        second_last_item = values[-2]
        
        # 마지막 항목이 이전 항목보다 10% 이상 증가했는지 확인
        if last_item > second_last_item * 1.10:
            return True
        else:
            return False

    def get_data_from_fnguide(self, ticker):
        try:
            url = f'https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=701'
                    #req.add_header('User-Agent', 'Mozilla/5.0')
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            self.soup = BeautifulSoup(res.text, 'html.parser')

            cop = self.soup.select_one('#highlight_D_A > table')
            self.df = pd.read_html(cop.prettify())[0]
            self.table_token = self.df.columns[0][0]
        except Exception as e:
            self.table_token = None
            # skip_string = "'NoneType' object has no attribute 'prettify'"
            # if skip_string not in e:
            #     print("Error : ", e)   
            # self.table_token = None
        #print(self.df.columns[0][0])
        #print(self.df.iloc[0].iloc[0])

    def get_eps_list_frequency_annual(self):
        try:
            if self.table_token == None:
                return None
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="EPS  (원)"]
            data = eps_df['Annual']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None

    def get_eps_list_frequency_quarter(self):
        try:
            if self.table_token == None:
                return None
            
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="EPS  (원)"]
            data = eps_df['Net Quarter']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None
        
    def get_roe_list_frequency_annual(self):
        try:
            if self.table_token == None:
                return None
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="ROE"]
            data = eps_df['Annual']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None

    def get_roe_list_frequency_quarter(self):
        try:
            if self.table_token == None:
                return None
            
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="ROE"]
            data = eps_df['Net Quarter']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None
        
    #부채비율 
    def get_dte_list_frequency_annual(self):
        try:
            if self.table_token == None:
                return None
            
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="부채비율"]
            data = eps_df['Annual']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None
        
    #부채비율 
    def get_dte_list_frequency_quarter(self):
        try:
            if self.table_token == None:
                return None
            
            field_names = self.df[self.table_token]
            eps_df = self.df.loc[field_names[self.table_token]=="부채비율"]
            data = eps_df['Net Quarter']

            #특정 열에서 결측값 제거
            data.dropna(axis=1)
            return [x for x in data.iloc[0].tolist() if not math.isnan(x)]
        except Exception as e:
            print("Error : ", e)   
            return None

    # 업종 eps 가져오기    
    def get_biz_category_eps(self):
        cop = self.soup.select_one('#upTabDivD')
        df = pd.read_html(cop.prettify())[0]

        table_token = df.columns[0]
        eps_df = df.loc[df[table_token ]=="EPS  (원)"]
        return eps_df.iloc[0,2]
    
    # ROE는 꾸준히 높은것이 좋다.
    # 업종 ROE 보다 높아야 한다.
    def get_biz_category_roe(self):
        cop = self.soup.select_one('#upTabDivD')
        df = pd.read_html(cop.prettify())[0]

        table_token = df.columns[0]
        eps_df = df.loc[df[table_token ]=="ROE"]
        return eps_df.iloc[0,2]
    
    # 종합 점수 계산 함수
    def calculate_weighted_score(self, data, weights):
        score = 0
        for key in data:
            # 부채비율은 점수가 낮을수록 좋으므로 부채비율의 경우 점수를 반전시킴
            if '부채비율' in key:
                score += (100 - data[key]) * weights[key]
            else:
                score += data[key] * weights[key]
        return score
    
    def get_eps_score(self, lst):
        score = 0
        if self.is_last_item_largest(lst) :
            score += 50
        if self.check_increase_by_10_percent(lst) :
            score += 50
        return score
    
    def get_roe_score(self, lst):
        score = 0
        if self.is_last_item_largest(lst) :
            score += 50
        if self.is_sequentially_increasing(lst):
            score += 50
        return score
    
def main():
    # current_date = datetime.now()
    # result_date = current_date - timedelta(days=450)

    # end_date = current_date.strftime('%Y-%m-%d')
    # start_date = result_date.strftime('%Y-%m-%d')

    # #fs = FundamentalSector(end_date)
    # #fs.print_kospi_data()
    # fa = FundamentalAnalysis('365550', start_date, end_date)
    # fa.get_same_industry_pbr()
    # # fa.get_data_from_naver()
    # # roe = fa.get_current_roe_from_naver()
    # # print(roe)

    test=FundamentalAnalysis2("263810")
    dte_annual_lst = test.get_dte_list_frequency_annual()
    dte_quater_lst = test.get_dte_list_frequency_quarter()
    eps_annual_lst = test.get_eps_list_frequency_annual()
    eps_quater_lst = test.get_eps_list_frequency_quarter()
    roe_annual_lst = test.get_roe_list_frequency_annual()
    roe_quater_lst = test.get_roe_list_frequency_quarter()

    print(dte_annual_lst)
    print(dte_quater_lst)
    print(eps_annual_lst)
    print(eps_quater_lst)
    print("roe annual list :", roe_annual_lst)
    print("roe quater list :", roe_quater_lst)

    print(test.get_biz_category_eps())

    eps_annual_score = test.get_eps_score(eps_annual_lst)
    eps_quater_score = test.get_eps_score(eps_quater_lst)

    roe_annual_score = test.get_roe_score(roe_annual_lst)
    roe_quater_score = test.get_roe_score(roe_quater_lst)

    eps_category_score = 0
    if (test.get_biz_category_eps() < eps_annual_lst[-1]):
        eps_category_score += 100

    roe_category_score = 0
    if (test.get_biz_category_roe() < roe_annual_lst[-1]):
        roe_category_score += 80

    print("eps : ", eps_annual_score, eps_quater_score, eps_category_score)
    print("roe : ", roe_annual_score, roe_quater_score, roe_category_score)
    data = {'업종EPS비교' : eps_category_score, 
         '연간EPS' : eps_annual_score, 
         '분기EPS' : eps_quater_score,
         '업종ROE비교' : roe_category_score, 
         '연간ROE' : roe_annual_score,
         '분기ROE' : roe_quater_score
        }
    
    weights = {
        '업종EPS비교': 0.3,
        '연간EPS': 0.2,
        '분기EPS': 0.4,
        '업종ROE비교': 0.3,
        '연간ROE': 0.15,
        '분기ROE': 0.25,
        '연간부채비율': -0.1,  # 부채비율은 낮을수록 좋으므로 가중치를 음수로 설정
        '분기별부채비율': -0.15
    }
    print(test.calculate_weighted_score(data,weights))
         
    


if __name__ == "__main__":
    # execute only if run as a script
    main()



    