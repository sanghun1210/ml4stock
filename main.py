# pip3 install pykrx
from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd
import multiprocessing

import technical_analysis
from mail import send_mail
import csv

def is_fundamental_pbr_is_higher(stock_code):
    try:
        now = datetime.now()
        # 날짜를 문자열로 변환 (YYYY-MM-DD 형식)
        date_string = now.strftime("%Y-%m-%d")
        df = stock.get_market_fundamental(date_string, date_string, stock_code)
        print(df)
        is_pbr_higher = df['PBR'].iloc[0] >= 3.2 
        if is_pbr_higher : 
            raise Exception('pbr is higher')  
        return is_pbr_higher
    except Exception as e:    
        print("error :  ", e) 
        return True

def get_daily_data(stock_code):
    try:
        # 현재 날짜 구하기
        current_date = datetime.now()
        result_date = current_date - timedelta(days=400)

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

def is_contain_zero_data(df):
    if (df['trade_price'] == 0).any() or \
        (df['high_price'] == 0).any() or \
        (df['low_price'] == 0).any() or \
        (df['open_price'] == 0).any() :
        return True
    return False

def process_list_part(part_tickers, result_queue):
    curr_proc = multiprocessing.current_process()
    for ticker in part_tickers :
        print(curr_proc._identity, ticker, end=" ")
        if is_fundamental_pbr_is_higher(ticker) == False:
            continue

        df = get_daily_data(ticker)
        if is_dataframe_empty(df) == False:
            daily_df = rename_stock_column(df)
            weekly_df = resample_to_week(daily_df)  
            monthly_df = resample_to_month(daily_df)

            if is_contain_zero_data(weekly_df) :
                print('weekly data contain 0')
                continue

            if len(daily_df) < 200 : 
                print('too short data')
                continue

            if technical_analysis.pattern1_check(daily_df, weekly_df, monthly_df) : 
                print('****** nice pattern ******')
                name = stock.get_market_ticker_name(ticker)
                result_queue.put(ticker + ' p1 : ' + name)
            if technical_analysis.pattern2_check(daily_df, weekly_df, monthly_df) : 
                print('****** nice pattern ******')
                name = stock.get_market_ticker_name(ticker)
                result_queue.put(ticker + ' p2 : ' + name)
            else :
                print('bad pattern')    

def process_list(part_tickers, result_list):
    for ticker in part_tickers :
        print(ticker, end=" ")
        if is_fundamental_pbr_is_higher(ticker) :
            continue

        df = get_daily_data(ticker)
        if is_dataframe_empty(df) == False:
            daily_df = rename_stock_column(df)
            weekly_df = resample_to_week(daily_df)  
            monthly_df = resample_to_month(daily_df)

            if is_contain_zero_data(weekly_df) :
                print('weekly data contain 0')
                continue

            if len(daily_df) < 200 : 
                print('too short data')
                continue

            if technical_analysis.pattern1_check(daily_df, weekly_df, monthly_df) : 
                print('****** nice pattern p1 ******')
                name = stock.get_market_ticker_name(ticker)
                result_list.append(ticker + ' p1 : ' + name)
            if technical_analysis.pattern2_check(daily_df, weekly_df, monthly_df) : 
                print('****** nice pattern p2 ******')
                name = stock.get_market_ticker_name(ticker)
                result_list.append(ticker + ' p2 : ' + name)
            else :
                print('bad pattern')   

def get_tickers_from_csv():
    tickers = []
    with open('test.csv', mode='r', encoding='cp949') as target_csv:
        df = csv.DictReader(target_csv, delimiter=',')
        for n, row in enumerate(df):
            if not n:#skip header
                continue

            # if row['Industry'].isspace() or row['Industry'] == '':
            #     continue

            tickers.append(row)
    return tickers

def get_tickers():
    try:
        tickers = stock.get_market_ticker_list(market="KOSDAQ")
        print('KOSDAQ count : ', len(tickers), end=" ")
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
        tickers.extend(kospi_tickers)
        print('KOSPI count : ', len(kospi_tickers))
        print('total tickers count : ', len(tickers) )

        with open('ticker_list.csv','w') as file :
            write = csv.writer(file)
            write.writerows(tickers)
        return tickers
    except Exception as e:    
        print("raise error ", e)


# def main():
#     try:
#         tickers = get_tickers()

#         nice_tickers = []
#         #tickers 리스트를 세 개의 부분으로 나누기
#         num_processes = 3

#         list_parts = [tickers[i::num_processes] for i in range(num_processes)]

#         # 프로세스 결과를 저장할 큐
#         result_queue = multiprocessing.Queue()

#         # 프로세스 리스트
#         processes = []
#         for part in list_parts:
#             process = multiprocessing.Process(target=process_list_part, args=(part, result_queue))
#             processes.append(process)

#         # 프로세스 실행
#         for process in processes:
#             process.start()

#         # 모든 프로세스가 종료될 때까지 대기
#         for process in processes:
#             process.join()

#         # 결과를 저장할 리스트
#         results = []

#         # 결과 큐에서 결과 가져오기
#         while not result_queue.empty():
#             results.append(result_queue.get())

#         msg = '\r\n'.join(results)
#         send_mail(msg, "check stock result")

#     except Exception as e:    
#         print("raise error ", e)

def main():
    try:
        tickers = get_tickers()

        nice_tickers = []

        # 결과를 저장할 리스트
        results = []

        process_list(tickers, results)

        msg = '\r\n'.join(results)
        send_mail(msg, "check stock result")

    except Exception as e:    
        print("raise error ", e)



if __name__ == "__main__":
    # execute only if run as a script
    main()