from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import math
from io import StringIO

# 재무 분석에 사용할 주요 지표 3개
# 부채비율 (Debt to Equity Ratio): 기업이 자산 구매를 위해 얼마나 많은 부채를 사용하고 있는지를 나타냅니다. 
# 낮은 부채비율은 기업이 빚을 적게 지고 있으며, 재무적으로 안정적이라는 것을 의미합니다.

# 영업이익률 (Operating Margin): 매출액에서 영업이익이 차지하는 비율을 나타내며, 기업의 핵심 비즈니스가 얼마나 효율적으로 이익을 창출하고 있는지를 보여줍니다. 
# 높은 영업이익률은 기업이 비용을 효율적으로 관리하며, 본질적인 사업에서 좋은 성과를 내고 있음을 의미합니다.

# 자기자본이익률 (Return on Equity, ROE): 자기자본(주주 자본)으로부터 얻은 순이익의 비율을 나타냅니다. 
# ROE는 기업이 주주의 자본을 얼마나 효율적으로 이용하여 수익을 창출하고 있는지를 보여줍니다. 높은 ROE는 기업이 주주 자본을 효과적으로 사용하여 높은 수익을 내고 있음을 의미합니다.

# 저평가 분석에 사용할 주요 지표 3개
# 주가수익비율 (Price to Earnings Ratio, PER): 주가를 주당 순이익(EPS)으로 나눈 값입니다. 낮은 PER은 주가가 주당 이익에 비해 상대적으로 저평가되어 있을 가능성이 있음을 의미합니다.
# 주가순자산비율 (Price to Book Ratio, PBR): 주가를 주당 순자산가치(BPS)로 나눈 값입니다. PBR이 1 이하일 경우, 기업이 그의 순자산가치보다 낮게 거래되고 있으며, 이는 저평가되었을 가능성을 시사합니다.
# 배당수익률 (Dividend Yield): 주당 배당금을 현재 주가로 나눈 값입니다. 높은 배당수익률은 주가 대비 좋은 배당수익을 제공하며, 이는 기업이 저평가되었을 가능성이 있음을 나타낼 수 있습니다. 특히, 안정적인 배당을 지속적으로 제공하는 기업의 경우 더욱 그렇습니다.


class FundamentalAnalysis3(object):
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

            cop = self.soup.select_one('#highlight_D_A')
            self.df = pd.read_html(StringIO(cop.prettify()))[0]
            self.table_token = self.df.columns[0][0]

            if len(self.get_data_lst_by("Net Quarter", "EPS  (원)")) == 0:
                cop = self.soup.select_one('#highlight_B_A')
                self.df = pd.read_html(StringIO(cop.prettify()))[0]
                self.table_token = self.df.columns[0][0]

        except Exception as e:
            self.table_token = None
            # skip_string = "'NoneType' object has no attribute 'prettify'"
            # if skip_string not in e:
            #     print("Error : ", e)   
            # self.table_token = None
        #print(self.df.columns[0][0])
        #print(self.df.iloc[0].iloc[0])
            
    # 숫자로 변환 시도, 실패하면 예외 처리하여 무시
    def safe_float_convert(self, x):
        try:
            return float(x)
        except ValueError:
            return None

    def get_data_lst_by(self, target_cloumn, target_row):
        try:
            if self.table_token == None:
                return None
            field_names = self.df[self.table_token]
            df = self.df.loc[field_names[self.table_token]==target_row]
            data = df[target_cloumn]

            # 특정 열에서 추정치 제거
            # data = data[[col for col in data.columns if '(' not in col]]

            #특정 열에서 결측값 제거
            filtered_data = data.dropna(axis=1)
            filtered_list = []
            for x in filtered_data.iloc[0].tolist():
                converted_x = self.safe_float_convert(x)
                if converted_x != None:
                    filtered_list.append(converted_x)
            return filtered_list
        except Exception as e:
            print("Error : ", e)   
            return None

    # 업종 eps 가져오기    
    def get_biz_category_eps(self):
        cop = self.soup.select_one('#upTabDivD')
        df = pd.read_html(StringIO(cop.prettify()))[0]

        table_token = df.columns[0]
        eps_df = df.loc[df[table_token ]=="EPS  (원)"]
        return eps_df.iloc[0,2]
    
    # ROE는 꾸준히 높은것이 좋다.
    # 업종 ROE 보다 높아야 한다.
    def get_biz_category_roe(self):
        cop = self.soup.select_one('#upTabDivD')
        df = pd.read_html(StringIO(cop.prettify()))[0]

        table_token = df.columns[0]
        eps_df = df.loc[df[table_token ]=="ROE"]
        return eps_df.iloc[0,2]
    
    # 종합 점수 계산 함수
    def calculate_weighted_score(self, data, weights):
        score = 0
        for key in data:
            # 부채비율은 점수가 낮을수록 좋으므로 부채비율의 경우 점수를 반전시킴
            score += data[key] * weights[key]
        return score
    
    def get_eps_score(self, lst):
        score = 0
        if sum(lst) == 0:
            return 50
        
        average = sum(lst) / len(lst)
        if lst[-1] > average :
            score += 50
        if self.is_last_item_largest(lst) :
            score += 25
        if self.check_increase_by_10_percent(lst) :
            score += 25
        return score
    
    def get_roe_quater_score(self, lst):
        score = 0

        if sum(lst) <= 1:
            return 50

        if lst[-1] > lst[-2] :
            score += 50
        if self.is_last_item_largest(lst) :
            score += 25
        if self.check_increase_by_10_percent(lst) :
            score += 25
        return score
    
    def get_eps_quater_score(self, lst):
        score = 0

        if sum(lst) <= 1:
            return 50

        final_value = lst[-1]
        initial_value = lst[-2]

        percentage_increase = ((final_value - initial_value) / abs(initial_value)) * 100
        if percentage_increase > 300:
            return 100
        
        average = sum(lst) / len(lst)
        if lst[-1] > average :
            score += 50
        if self.is_last_item_largest(lst) :
            score += 25
        if self.check_increase_by_10_percent(lst) :
            score += 25
        return score
    
    def get_roe_stability(self, lst):
        if len(lst) < 2:  # 최소 2개 이상의 데이터 포인트가 필요
            return False  # 데이터가 충분하지 않아 안정성을 계산할 수 없음
    
        # 연속된 ROE 값들 간의 차이(변화량) 계산
        differences = [abs(lst[i] - lst[i-1]) for i in range(1, len(lst))]
        avg_difference = sum(differences) / len(differences)
        
        # 변화량의 평균으로부터의 편차 제곱의 평균(분산) 계산
        variance = sum((x - avg_difference) ** 2 for x in differences) / len(differences)
        return variance
    
    def get_roe_score(self, lst):
        score = 0

        if sum(lst) == 0:
            return 50
        
        average = sum(lst) / len(lst)
        if lst[-1] > average :
            score += 45

        if lst[-1] > lst[-2] :
            score += 30

        if self.is_sequentially_increasing(lst):
            score += 25
        return score
    
    def get_base_score(self, lst):
        score = 0

        if sum(lst) == 0:
            return 50
        
        if len(lst) == 1:
            return 50
        
        average = sum(lst) / len(lst)
        if lst[-1] > average :
            score += 50

        if lst[-1] > lst[-2] :
            score += 25

        if self.is_sequentially_increasing(lst):
            score += 25
        return score
    
    def caculate_roe_category_score(self, category_roe, stork_roe):
        if stork_roe < category_roe:
            return 0
        
        percent_difference = ((stork_roe - category_roe) / category_roe) * 100
        if percent_difference >= 20:
            return 100
        elif percent_difference >= 10:
            return 70
        else:
            return 50
        
    def get_biz_category(self):
        cop = self.soup.select_one('#upTabDivD')
        df = pd.read_html(StringIO(cop.prettify()))[0]
        str1 = df.columns[2]
        cop = self.soup.select_one('#compBody > div.section.ul_corpinfo > div.corp_group1 > p > span.stxt.stxt2')
        str2 = cop.get_text()
        return str1 + ' | ' + str2
    
    def debt_to_score(self,lst):
        score = 0
        average = sum(lst) / len(lst)
        if lst[-1] < average :
            score += 30

        if lst[-1] > average :
            score += -50

        if self.is_last_item_largest(lst):
            score += -50
            

        # if lst[-1] < 25:
        #     score += 75
        # elif 25 <= lst[-1] and lst[-1] < 50:
        #     score += 50
        # elif 50 <= lst[-1] and lst[-1] < 80:
        #     score -= 25
        # elif 80 <= lst[-1] and lst[-1] < 150 :
        #     score -= 50
        # else : 
        #     score = -300

        return score
    
    def find_pbr_score(self):
        try:
            cop = self.soup.select_one('#corp_group2 > dl:nth-child(4) > dd')
            pbr = float(cop.get_text())
            if pbr <= 1 : 
                return 100
            elif pbr <= 1.5:
                return 50
            else:
                eps_annual_lst = self.get_data_lst_by("Annual", "EPS  (원)")
                eps_quater_lst = self.get_data_lst_by("Net Quarter", "EPS  (원)")
                eps_annual_score = self.get_eps_score(eps_annual_lst)
                eps_quater_score = self.get_eps_quater_score(eps_quater_lst)
                if eps_annual_score + eps_quater_score >= 140:
                    return 80
                else:
                    return 20

        except Exception as e:
            print('find_pbr : ', e)
            return None
        

    def find_per(self):
        cop = self.soup.select_one('#corp_group2 > dl:nth-child(1) > dd')
        str = cop.get_text()
        return self.safe_float_convert(str)

    def find_category_per(self):
        cop = self.soup.select_one('#corp_group2 > dl:nth-child(3) > dd')
        str = cop.get_text()
        return self.safe_float_convert(str)


        #corp_group2 > dl:nth-child(4) > dd
    

    #eps가 높고, roe가 높은 주식
    def estimate_basic_measure(self):
        eps_annual_lst = self.get_data_lst_by("Annual", "EPS  (원)")
        eps_quater_lst = self.get_data_lst_by("Net Quarter", "EPS  (원)")
        roe_annual_lst = self.get_data_lst_by("Annual", "ROE")
        roe_quater_lst = self.get_data_lst_by("Net Quarter", "ROE")
        dte_annual_lst = self.get_data_lst_by("Annual", "부채비율")
        dte_quater_lst = self.get_data_lst_by("Net Quarter", "부채비율")

        if eps_annual_lst == None or len(eps_annual_lst) == 0:
            return 0

        print(dte_annual_lst)
        print(dte_quater_lst)
        print(eps_annual_lst)
        print(eps_quater_lst)
        print("roe annual list :", roe_annual_lst)
        print("roe quater list :", roe_quater_lst)

        # print(self.get_biz_category_eps())
        # print(self.get_biz_category())

        eps_annual_score = self.get_eps_score(eps_annual_lst)
        eps_quater_score = self.get_eps_quater_score(eps_quater_lst)
        roe_annual_score = self.get_roe_score(roe_annual_lst)
        roe_quater_score = self.get_roe_quater_score(roe_quater_lst)

        eps_category_score = 0
        if (self.get_biz_category_eps() < eps_annual_lst[-1]):
            eps_category_score += 100

        roe_category_score = 0
        # print("roe_ categroy : ", self.get_biz_category_roe())
        # print("roe_ annual [-1] : ", roe_annual_lst[-1])
        roe_category_score = self.caculate_roe_category_score(self.get_biz_category_roe(), roe_annual_lst[-1])

        if eps_category_score == 0 :
            eps_category_score = self.find_pbr_score()

        print("eps annal, quater, category : ", eps_annual_score, eps_quater_score, eps_category_score)
        print("roe annal, quater, category : ", roe_annual_score, roe_quater_score, roe_category_score)
        print("dept annal : ", self.debt_to_score(dte_annual_lst))
        print("dept quater : ", self.debt_to_score(dte_quater_lst))
        data = {'업종EPS비교' : eps_category_score, 
            '연간EPS' : eps_annual_score, 
            '분기EPS' : eps_quater_score,
            '업종ROE비교' : roe_category_score, 
            '연간ROE' : roe_annual_score,
            '분기ROE' : roe_quater_score,
            '연간부채비율': self.debt_to_score(dte_annual_lst), # 부채비율은 낮을수록 좋으므로 가중치를 음수로 설정
            '분기별부채비율': self.debt_to_score(dte_quater_lst)
            }
        
        weights = {
            '업종EPS비교': 0.2,
            '연간EPS': 0.2,
            '분기EPS': 0.3,
            '업종ROE비교': 0.2,
            '연간ROE': 0.2,
            '분기ROE': 0.27,
            '연간부채비율': 0.05,  
            '분기별부채비율': 0.05
        }
        return self.calculate_weighted_score(data,weights)
    
    def get_financial_analysis_score(self):
        roe_annual_lst = self.get_data_lst_by("Annual", "ROE")
        roe_quater_lst = self.get_data_lst_by("Net Quarter", "ROE")
        om_annual_lst = self.get_data_lst_by("Annual", "영업이익")
        om_quater_lst = self.get_data_lst_by("Net Quarter", "영업이익")
        dte_annual_lst = self.get_data_lst_by("Annual", "부채비율")
        dte_quater_lst = self.get_data_lst_by("Net Quarter", "부채비율")
        eps_quater_lst = self.get_data_lst_by("Net Quarter", "EPS  (원)")

        if roe_annual_lst == None or len(roe_annual_lst) == 0:
            return 0

        # print(dte_annual_lst)
        print(dte_quater_lst)
        # print(om_annual_lst)
        # print(om_quater_lst)
        # print("roe annual list :", roe_annual_lst)
        # print("roe quater list :", roe_quater_lst)
        # print("eps quater list :", eps_quater_lst)

        # print(self.get_biz_category_eps())
        # print(self.get_biz_category())

        roe_annual_score = self.get_base_score(roe_annual_lst)
        roe_quater_score = self.get_base_score(roe_quater_lst)
        om_annual_score = self.get_base_score(om_annual_lst)
        om_quater_score = self.get_base_score(om_quater_lst)
        dte_annual_score = self.debt_to_score(dte_annual_lst)
        dte_quater_score = self.debt_to_score(dte_quater_lst)
        eps_quater_score = self.get_eps_quater_score(eps_quater_lst)

        roe_category_score = 0
        roe_category_score = self.caculate_roe_category_score(self.get_biz_category_roe(), roe_annual_lst[-1])

        data = {'연간영업이익' : om_annual_score, 
            '분기영업이익' : om_quater_score,
            '업종ROE비교' : roe_category_score, 
            '연간ROE' : roe_annual_score,
            '분기ROE' : roe_quater_score,
            '연간부채비율': dte_annual_score,
            #'분기별부채비율': dte_quater_score,
            '분기EPS': eps_quater_score
            }

        #print(data)
        
        weights = {
            '연간영업이익': 0.2,
            '분기영업이익': 0.25,
            '업종ROE비교': 0.2,
            '분기EPS': 0.25,
            '연간ROE': 0.2,
            '분기ROE': 0.2,
            '연간부채비율': 0.05,  
            '분기별부채비율': 0.05
        }
        return self.calculate_weighted_score(data,weights)
    
    def get_per_score(self):
        per = self.find_per()
        per_category = self.find_category_per()

        if per == None or per_category == None:
            return 50

        if per >= per_category:
            return 0
        else:
            return 100

    def get_undervalued_analysis_analysis_score(self):
        pbr_score = self.find_pbr_score()
        per = self.find_per()
        per_category = self.find_category_per()
        per_score = self.get_per_score()

        data = {'PBR' : pbr_score, 
            'PER' : per_score,
            }
        
        #print(data)

        weights = {
            'PBR': 0.5,
            'PER': 0.5
        }
        return self.calculate_weighted_score(data,weights)

        
    
def main():
    test=FundamentalAnalysis3("058220")
    #print(test.estimate_basic_measure())

    print(test.get_financial_analysis_score())
    print(test.get_undervalued_analysis_analysis_score())

if __name__ == "__main__":
    # execute only if run as a script
    main()



    