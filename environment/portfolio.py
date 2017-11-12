
#Portfolio Class

import numpy as np


class Portfolio:

    def __init__(self, portfolio_cash=1000.0, coin=None):
        self.starting_cash = portfolio_cash
        # note this is a coin obj
        self.coin = coin
        self.portfolio_coin = 0
        self.portfolio_cash = portfolio_cash
        self.latest_coin_value = self.coin.getCurrentValue()

        # store daily returns
        self.daily_returns = np.array([0.0])

    def getCurrentValue(self):
        return self.portfolio_coin * self.coin.getCurrentValue() + self.portfolio_cash

    def getReturnsPercent(self):
        return 100 * (self.getCurrentValue() - self.starting_cash) / self.starting_cash

    def getCurrentHoldings(self):
        return "%.2f coins, %.2f cash, %.2f current value, %.2f percent returns" \
                % (self.portfolio_coin, self.portfolio_cash, self.getCurrentValue(), self.getReturnsPercent())

    def buy(self, coins_to_buy=0):
        current_price = self.coin.getCurrentValue()
        if not current_price:
            return 0
        amount_to_buy = min(self.portfolio_cash / current_price, coins_to_buy)
        self.portfolio_coin += amount_to_buy
        self.portfolio_cash -= amount_to_buy * current_price
        return amount_to_buy
    
    def sell(self, coins_to_sell=0):
        current_price = self.coin.getCurrentValue()
        if not current_price:
            return 0
        coin_to_sell = min(coins_to_sell, self.portfolio_coin)
        self.portfolio_coin -= coin_to_sell
        self.portfolio_cash += coin_to_sell * current_price
        return coin_to_sell

    def step(self):
        # get current port value
        current_value = self.getCurrentValue()
        
        # step to next day
        if self.coin.advance() is None:
            return False

        # get new port value
        new_value = self.getCurrentValue()

        # compute daily return
        daily_return = (new_value - current_value) / current_value

        # add to daily return list
        self.daily_returns = np.append(self.daily_returns, [daily_return])

        return True

    def getCurrentState(self):
        # state is represented by a feature vector
        # [avg_daily_return, sd_daily_return, sharpe_ratio, check_upper_band, check_lower_band]

        avg_daily_return = self.daily_returns.mean()
        sd_daily_return = self.daily_returns.std()

        # assume risk-free return to be 0%
        if sd_daily_return == 0:
            sharpe_ratio = 0
        else:
            sharpe_ratio = np.sqrt(252) * (avg_daily_return / sd_daily_return)

        # check if the price is outside the Bollinger Bands
        check_upper_band, check_lower_band = self.coin.checkBollingerBands()

        return [self.getCurrentValue(), self.coin.getCurrentValue(), sharpe_ratio, check_upper_band, check_lower_band]
    
    
    def reset(self):
        self.coin.reset()
        self.portfolio_coin = 0
        self.portfolio_cash = self.starting_cash
        self.latest_coin_value = self.coin.getCurrentValue()
        self.daily_returns = np.array([0.0])
        