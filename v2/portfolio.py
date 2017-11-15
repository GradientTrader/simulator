import numpy as np
from enum import Enum

class Action(Enum):
    HOLD=0
    BUY=1
    SELL=2

'''
from env import *
env = Environment(coin_name="ethereum")
p = Portfolio(env)

print env.getStates() ## initial step
p._buy(10)
print env.step()
print p.getCurrentHoldings()
'''
class Portfolio:
    def __init__(self, env, portfolio_cash=1000.0, num_coins_per_order=10.0):
        self.starting_cash = portfolio_cash
        self.portfolio_coin = 0.0
        self.portfolio_cash = portfolio_cash
        self.env = env
        self.num_coins_per_order = num_coins_per_order

    def getCurrentValue(self):
        return self.portfolio_coin * self.env.getStates(["current_price"])[0] + \
            self.portfolio_cash

    def getReturnsPercent(self):
        return 100 * (self.getCurrentValue() - self.starting_cash) / self.starting_cash

    def getCurrentHoldings(self):
        return "%.2f coins, %.2f cash, %.2f current value, %.2f percent returns" \
                % (self.portfolio_coin, self.portfolio_cash, self.getCurrentValue(), self.getReturnsPercent())

    def apply_action(self, action):
        if action == Action.BUY:
            self._buy(self.num_coins_per_order)
        elif action == Action.SELL:
            self._sell(self.num_coins_per_order)

    def getActionSpaceSize(self):
        return len(list(Action))

    def _buy(self, coins_to_buy=0):
        current_price = self.env.getStates(["current_price"])[0]
        if not current_price:
            return 0
        amount_to_buy = min(self.portfolio_cash / current_price, coins_to_buy)
        self.portfolio_coin += amount_to_buy
        self.portfolio_cash -= amount_to_buy * current_price
        return amount_to_buy
    
    def _sell(self, coins_to_sell=0):
        current_price = self.env.getStates(["current_price"])[0]
        if not current_price:
            return 0
        coin_to_sell = min(coins_to_sell, self.portfolio_coin)
        self.portfolio_coin -= coin_to_sell
        self.portfolio_cash += coin_to_sell * current_price
        return coin_to_sell

    def reset(self):
    	self.__init__(self.env, portfolio_cash=self.starting_cash)

