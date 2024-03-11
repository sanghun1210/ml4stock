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
from fundametal_analysis2 import FundamentalAnalysis2

import logging

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

# 높은 ROE와 EPS
# 수익성 및 효율성: 높은 ROE는 기업이 자본을 효율적으로 사용하여 높은 수익을 창출하고 있음을 의미합니다. 
# 또한, 높은 EPS는 기업이 주당 높은 순이익을 기록하고 있음을 나타내며, 이는 강력한 수익성의 지표입니다.
def get_fund_score(ticker):
    logger = logging.getLogger('get_fund_score()')
    logger.setLevel(logging.INFO)
    fa=FundamentalAnalysis2(ticker)
    w_score = fa.estimate_basic_measure()
    if w_score == 0:
        return 0, None
    
    logger.info("weighted_scroe : " + str(w_score))
    return w_score, fa.get_biz_category()

def run_strategies(ticker, result_list):
    try:
        logger = logging.getLogger('run_strategies()')
        logger.setLevel(logging.INFO)
        score, biz_category = get_fund_score(ticker)
        print(score)
        if score < 95 :
            return
        
        start, end = get_period()
        data_handler = StockDataHandler(ticker, start, end)
        if data_handler.check_valid_data() == False:
            return 
        
        if technical_analysis.pattern4_check(data_handler.get_weekly_data()) :
            logger.info("pattern4_check ok")
            if technical_analysis.pattern5_check(data_handler.get_daily_data()) :
                logger.info("pattern5_check pass")
                name = stock.get_market_ticker_name(ticker)
                #print(ticker + ' p1 : ' + name + ' next_week : ' + str(ret_next_week) + ' next_month : ' + str(ret_next_week5))
                result_list.append(ticker + ' : ' + name + ' [' + biz_category + ']')
                print('p1 pass')
    except Exception as e:
        print(e)

def get_period():
    current_date = datetime.now()
    result_date = current_date - timedelta(days=500)

    end_date = current_date.strftime('%Y-%m-%d')
    start_date = result_date.strftime('%Y-%m-%d')
    return start_date, end_date

def main():
    try:
        current_date = datetime.now()
        current_date_string = current_date.strftime('%Y-%m-%d')
        log_file_name = 'log_daybase' + current_date_string
        logging.basicConfig(filename=log_file_name, encoding='utf-8', filemode='w', level=logging.INFO)
        kospi_tickers = get_tickers('KOSPI')
        if kospi_tickers == None:
            kospi_tickers = get_tickers_from_csv('KOSPI')

        kosdaq_tickers = get_tickers('KOSDAQ')
        if kosdaq_tickers == None:
            kosdaq_tickers = get_tickers_from_csv('KOSDAQ')
        
        print('kospi tickers count : ', len(kospi_tickers) )
        print('kosdaq tickers count : ', len(kosdaq_tickers) )
        print('total tickers count : ', len(kosdaq_tickers) + len(kospi_tickers))

        logger = logging.getLogger('main()')
        logger.setLevel(logging.INFO)

        result_list = []
        count =0
        start, end = get_period()
        for ticker in kospi_tickers :
            count+=1
            print('[' + str(count) + '] : ' + ticker + ' ...')  
            logger.info('[' + str(count) + '] : ' + ticker + ' ...')
            run_strategies(ticker, result_list)

        for ticker in kosdaq_tickers :
            count+=1
            print('[' + str(count) + '] : ' + ticker + ' ...')  
            logger.info('[' + str(count) + '] : ' + ticker + ' ...')
            run_strategies(ticker, result_list)
                
        msg = '\r\n'.join(result_list)
        send_mail(msg, "중단기 지표-부채비율 및 업종 PBR 고려 필요")
    except Exception as e:    
        print("raise error ", e)


if __name__ == "__main__":
    # execute only if run as a script
    main()
