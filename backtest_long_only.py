from back_test_base import BackTestBase
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor

class BacktestLongOnly(BackTestBase):
    def __init__(self, symbol, data, amount, ftc = 0.0, ptc = 0.0, verbose=True):
        super().__init__(symbol, data, amount, ftc, ptc, verbose)
        self.long_only = True

    def run_sma_strategy(self, SMA1, SMA2):
        msg = f'\n\nRunning SMA strategy with SMA1 = {SMA1} and SMA2 = {SMA2}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 50)

        self.position = 0
        self.trades = 0
        
        self.amount = self.initial_amount
        self.data['SMA1'] = self.data['trade_price'].rolling(SMA1).mean()
        self.data['SMA2'] = self.data['trade_price'].rolling(SMA2).mean()

        for bar in range(SMA2, len(self.data)):
            if self.data['SMA1'][bar] > self.data['SMA2'][bar] and self.position == 0:
                self.place_buy_order(bar, amount=self.amount)
                self.position = 1
            elif self.data['SMA1'][bar] < self.data['SMA2'][bar] and self.position == 1:
                self.place_sell_order(bar, amount=self.amount)
                self.position = 0
        self.close_out(bar)

    def run_momentum_strategy(self, momentum):
        msg = f'\n\nRunning momentum strategy with momentum = {momentum}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 50)

        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount
        self.data['momentum'] = self.data['trade_price'].rolling(momentum).mean()

        for bar in range(momentum, len(self.data)):
            if self.data['momentum'][bar] > 0 and self.position == 0:
                self.place_buy_order(bar, amount=self.amount)
                self.position = 1
            elif self.data['momentum'][bar] < 0 and self.position == 1:
                self.place_sell_order(bar, amount=self.amount)
                self.position = 0
        self.close_out(bar)

    def run_mean_reversion_strategy(self, SMA, threshold):
        msg = f'\n\nRunning mean reversion strategy '
        msg += f'SMA={SMA} | threshold={threshold}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 50)

        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount
        self.data['SMA'] = self.data['trade_price'].rolling(SMA).mean()

        for bar in range(SMA, len(self.data)):
            if self.position == 0 :
                if(self.data['trade_price'].iloc[bar] < self.data['SMA'].iloc[bar] - threshold):
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if(self.data['trade_price'].iloc[bar] > self.data['SMA'].iloc[bar] + threshold):
                    self.place_sell_order(bar, amount=self.amount)
                    self.position = 0
        self.close_out(bar)

    def create_train_split_group(X,Y, split_ratio=0.8):
        return train_test_split(X,Y, shuffle=False, train_size=split_ratio)

    def run_random_forest_strategy(self, momentum):
        msg = f'\n\nRunning momentum strategy with momentum = {momentum}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 50)

        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount
        self.data['momentum'] = self.data['trade_price'].rolling(momentum).mean()
        self.data['Open-Close'] = (self.data['open_price'] - self.data['trade_price'])/self.data['open_price']
        self.data['High-Low'] = (self.data['high_price'] - self.data['low_price'])/self.data['low_price']
        self.data['percent_change'] = self.data['trade_price'].pct_change()

        self.data.dropna(inplace=True)

        # X is the input variable
        X = self.data[['Open-Close', 'High-Low', 'volume', 'momentum']]

        # 미래와 비교 
        # 다음날 올랐는지 여부
        Y = np.where(self.data['trade_price'].shift(-1) > self.data['trade_price'], 1, -1) 

        split_ratio=0.8
        split_value=int(split_ratio * len(self.data))
        X_train=X[:split_value]
        Y_train=Y[:split_value]
        X_test=X[split_value:]
        Y_test=Y[split_value:]

        reg = RandomForestRegressor(n_estimators = 1000, max_depth=200, random_state = 42)
        reg.fit(X_train, Y_train)

        relation_sqare = reg.score(X_train, Y_train)
        print(relation_sqare)

        from sklearn.metrics import mean_squared_error, r2_score

        print('Mean sqared error: %.2f' % mean_squared_error(Y_train, reg.predict(X_train)))
        print('Variance score: %.2f' % r2_score(Y_train, reg.predict(X_train)))
        print('Mean sqared error: %.2f' % mean_squared_error(Y_test, reg.predict(X_test)))
        print('Variance score: %.2f' % r2_score(Y_test, reg.predict(X_test)))

        print(len(self.data), len(reg.predict(X_train)), len(reg.predict(X_test)))

        self.data['predict'] = reg.predict(X)
        # print(self.data.tail(30))

        for bar in range(momentum, len(self.data)):
            if self.data['predict'][bar] > 0 and self.position == 0:
                self.place_buy_order(bar, amount=self.amount)
                self.position = 1
            elif self.data['predict'][bar] < 0 and self.position == 1:
                self.place_sell_order(bar, amount=self.amount)
                self.position = 0
        self.close_out(bar)

    def run_random_forest_strategy_v2(self, momentum):
        # msg = f'\n\nRunning momentum strategy with momentum = {momentum}'
        # msg += f'\nfixed costs {self.ftc} | '
        # msg += f'proportional costs {self.ptc}'
        # print(msg)

        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount
        self.data['momentum'] = self.data['trade_price'].rolling(momentum).mean()
        self.data['Open-Close'] = (self.data['open_price'] - self.data['trade_price'])/self.data['open_price']
        self.data['High-Low'] = (self.data['high_price'] - self.data['low_price'])/self.data['low_price']
        self.data['percent_change'] = self.data['trade_price'].pct_change()

        self.data.dropna(inplace=True)

        # X is the input variable
        X = self.data[['Open-Close', 'High-Low', 'volume', 'momentum']]

        # 미래와 비교 
        # 다음날 올랐는지 여부
        Y = np.where(self.data['trade_price'].shift(-1) > self.data['trade_price'], 1, -1) 

        split_ratio=0.8
        split_value=int(split_ratio * len(self.data))
        X_train=X[:split_value]
        Y_train=Y[:split_value]
        X_test=X[split_value:]
        Y_test=Y[split_value:]

        reg = RandomForestRegressor(n_estimators = 1000, max_depth=200, random_state = 42)
        reg.fit(X_train, Y_train)

        relation_sqare = reg.score(X_train, Y_train)
        # print(relation_sqare)

        # from sklearn.metrics import mean_squared_error, r2_score

        # print('Mean sqared error: %.2f' % mean_squared_error(Y_train, reg.predict(X_train)))
        # print('Variance score: %.2f' % r2_score(Y_train, reg.predict(X_train)))
        # print('Mean sqared error: %.2f' % mean_squared_error(Y_test, reg.predict(X_test)))
        # print('Variance score: %.2f' % r2_score(Y_test, reg.predict(X_test)))

        # print(len(self.data), len(reg.predict(X_train)), len(reg.predict(X_test)))

        self.data['predict'] = reg.predict(X)
        # print(self.data.tail(30))

        for bar in range(momentum, len(self.data)):
            if self.data['predict'][bar] > 0 and self.position == 0:
                self.place_buy_order(bar, amount=self.amount)
                self.position = 1
            elif self.data['predict'][bar] < 0 and self.position == 1:
                self.place_sell_order(bar, amount=self.amount)
                self.position = 0
        self.close_out(bar)


