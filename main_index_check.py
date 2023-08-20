# pip3 install pykrx
from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd

import technical_analysis
from mail import send_mail
import csv

from data_handler import StockDataHandler
from backtest_long_only import BacktestLongOnly
from fundametal_analysis import FundamentalAnalysis, FundamentalSector



def get_tickers_from_csv(market):
    tickers = []
    with open('{0}_tickers.csv'.format(market), mode='r', encoding='cp949') as target_csv:
        df = csv.DictReader(target_csv, delimiter=',')
        for n, row in enumerate(df):
            if not n:#skip header
                continue
            tickers.append(row)
    return tickers

def get_tickers(market):
    try:
        tickers = stock.get_market_ticker_list(market=market)
        with open('{0}_tickers.csv'.format(market),'w') as file :
            write = csv.writer(file)
            write.writerow(tickers)
        return tickers
    except Exception as e:    
        print("raise error ", e)

def run_strategies(ticker, result_list):
    try:
        start, end = get_period()
        data_handler = StockDataHandler(ticker, start, end, True)
        if data_handler.check_valid_data() == False:
            return 
        
        print('    - check_valid_data pass')
        return technical_analysis.pattern_index_check(data_handler.get_daily_data(), data_handler.get_weekly_data())
    except Exception as e:
        print("Error : ", e)
        return False


def get_period():
    current_date = datetime.now()
    result_date = current_date - timedelta(days=600)

    end_date = current_date.strftime('%Y-%m-%d')
    start_date = result_date.strftime('%Y-%m-%d')
    return start_date, end_date

def main():
    try:
        kospi_tickers = stock.get_index_ticker_list(market='KOSPI')
        kosdaq_tickers = stock.get_index_ticker_list(market='KOSDAQ')
        
        print('kospi tickers count : ', len(kospi_tickers) )
        print('kosdaq tickers count : ', len(kosdaq_tickers) )
        print('total tickers count : ', len(kosdaq_tickers) + len(kospi_tickers))

        result_list = []
        count =0
        start, end = get_period()
        for ticker in kosdaq_tickers :
            count+=1
            print('[' + str(count) + '] : ' + ticker + ' ...')  
            if run_strategies(ticker, result_list) : 
                print('wow')
                name = stock.get_index_ticker_name(ticker)
                result_list.append(ticker + ' KOSDAQ : ' + name)

        for ticker in kospi_tickers :
            count+=1
            print('[' + str(count) + '] : ' + ticker + ' ...')  
            if run_strategies(ticker, result_list) : 
                print('wow')
                name = stock.get_index_ticker_name(ticker)
                result_list.append(ticker + ' KOSPI : ' + name)

        msg = '\r\n'.join(result_list)
        send_mail(msg, "check stock result")
    except Exception as e:    
        print("raise error ", e)


if __name__ == "__main__":
    # execute only if run as a script
    main()
