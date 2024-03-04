from datetime import datetime, timedelta
from pykrx import stock

import sys
n_args = 0

def rename_stock_column(df):
    new_column_names = {
        '시가': 'open_price',
        '고가': 'high_price',
        '저가': 'low_price',
        '종가': 'trade_price',
        '거래량': 'volume',
        '등락률': 'rate',
    }
    df.rename(columns=new_column_names, inplace=True)
    return df

def main():
    current_date = datetime.now()
    result_date = current_date - timedelta(days=900)

    if n_args > 1:
    # 첫 번째 인자부터 출력
        code = sys.argv[1]
        df = stock.get_market_ohlcv_by_date(result_date, current_date, code)
        df.index.name = 'date'
        df = df.drop('거래대금',axis=1)
        df = rename_stock_column(df)
        
        df.to_csv('output.csv', index=True)
    else:
        print("please input stock code")

    

if __name__ == "__main__":
    # execute only if run as a script
    n_args = len(sys.argv)
    main()
