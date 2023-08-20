import numpy as np
import pandas as pd

from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta

class BackTestBase(object) :
    '''거래 전략을 가지고 이벤트 기반 백테스트를 하기 위한 기저 클래스'''
    # 거래당 고정 거래비용
    # ptc 거래당 비례 거래비용
    def __init__(self, symbol, data, amount, 
                 ftc= 0.0, ptc = 0.0, verbose=True):
        self.symbol = symbol
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.verbose = verbose
        self.position = 0
        self.trades = 0
        self.units = 0 
        self.data = data
        self.data['return'] = np.log(self.data['trade_price'] / self.data['trade_price'].shift(1))
        self.data = self.data.dropna()
        
    def plot_data(self, cols=None):
        '''종목코드의 종가를 표시한다.'''
        if cols is None:
            cols = ['trade_price']
        self.data['trade_price'].plot(figsize=(10, 6), title=self.symbol)

    def get_date_price(self, bar):
        '''봉에 대한 일자와 가격을 반환한다.'''
        date = str(self.data.index[bar].strftime('%Y-%m-%d')[:10])
        price = self.data['trade_price'][bar]
        return date, price
    
    def print_balance(self, bar):
        '''현재 현금 잔고 정보를 프린트한다.'''
        date, price = self.get_date_price(bar)
        print(date, price, self.amount)

    def print_net_wealth(self, bar):
        date, price = self.get_date_price(bar)
        net_wealth = self.amount + self.position * price
        print(date, price, net_wealth)

    def place_buy_order(self, bar, units=None, amount=None):
        ''' 매수 주문을 넣는다. '''
        date, price = self.get_date_price(bar)
        if units is None:
            units = int(amount / price)
        self.amount -= (units * price) * (1+self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        if self.verbose:
            print(date, price, units, self.amount)
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def place_sell_order(self, bar, units=None, amount=None):
        '''매도 주문을 넣는다.'''
        date, price = self.get_date_price(bar)
        if units is None:
            units = self.units
        self.amount += (units * price) * (1-self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(date, price, units, self.amount)
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def close_out(self, bar):
        '''롱 포지션이나 숏 포지션을 닫는다. '''
        date, price = self.get_date_price(bar)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(date, price, self.units, self.amount)
            print('=' * 50)
        print('Final balance     [$] {:.2f}'.format(self.amount))
        perf = ((self.amount - self.initial_amount) / self.initial_amount) * 100
        print('Net Performance [%] {:.2f}'.format(perf))
        print('Trades           [#] {}'.format(self.trades))
        print('=' * 50)

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
    





