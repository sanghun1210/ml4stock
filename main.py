# pip3 install pykrx
from pykrx import stock
from pykrx import bond
from datetime import datetime

def is_fundamental_pbr_good(stock_code):
    try:
        now = datetime.now()
        # 날짜를 문자열로 변환 (YYYY-MM-DD 형식)
        date_string = now.strftime("%Y-%m-%d")
        df = stock.get_market_fundamental(date_string, date_string, stock_code)
        return df['PBR'].iloc[0] < 3
    except Exception as e:    
        return False

def get_stock_data(stock_code, start_date, end_date):
    # stock_code: 종목 코드 (e.g., '005930' for 삼성전자)
    # start_date: 데이터 시작일 (YYYY-MM-DD 형식)
    # end_date: 데이터 종료일 (YYYY-MM-DD 형식)
    
    # 주식 데이터 가져오기
    df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
    return df

def main():
    try:
        tickers = stock.get_market_ticker_list(market="KOSDAQ")
        tickers.append(stock.get_market_ticker_list(market="KOSPI"))

        for ticker in tickers :
            print(ticker)
            if is_fundamental_pbr_good(ticker): 
                break
            else:
                print('fundatmental error')
        
    except Exception as e:    
        print("raise error ", e)

if __name__ == "__main__":
    # execute only if run as a script
    main()