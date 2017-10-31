
# Cryptocurrency Market Simulator

from env import Coin
from portfolio import Portfolio
from random import randint


def enum(**enums): return type('Enum', (), enums)


class Simulator:

    Action = enum(HOLD=0, BUY=1, SELL=2)

    def __init__(self, num_coins_per_order=1, portfolio_cash=1000.0, coin=Coin("ethereum")):
        self.num_coins_per_order = num_coins_per_order
        self.coin = coin
        self.portfolio = Portfolio(portfolio_cash=portfolio_cash, coin=coin)
        
    
    def get_current_state(self):
        return self.portfolio.getCurrentState()
    
    
    def get_current_holdings(self):
        return self.portfolio.getCurrentHoldings()
    

    def get_ran_action(self):
        return randint(self.Action.BUY, self.Action.HOLD, self.Action.SELL)

    
    def take_action_and_step(self, action):
        #print 'Taking action:', action
        if action == self.Action.BUY:
            self.portfolio.buy(self.num_coins_per_order)
        elif action == self.Action.SELL:
            self.portfolio.sell(self.num_coins_per_order)

        if self.portfolio.step() is False:
            return [None, 0]

        state = self.portfolio.getCurrentState()
        reward = self.portfolio.getReturnsPercent()

        return [state, reward]

    