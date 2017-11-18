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

state_list = ["coin", "cash", "total_value"]

class Portfolio:
    def __init__(self, portfolio_cash=1000.0, num_coins_per_order=10.0, states=state_list):
        self.starting_cash = portfolio_cash
        self.portfolio_coin = 0.0
        self.portfolio_cash = portfolio_cash
        self.num_coins_per_order = num_coins_per_order
        self.states = states
        
        ### Mapping states to their names
        self.state_dict = {}
        self.state_dict["coin"] = self.portfolio_coin
        self.state_dict["cash"] = self.portfolio_cash
        self.state_dict["total_value"] = self.portfolio_cash
        
        
    def getStates(self, states=None):
        if not states:
            states = self.states
        return [self.state_dict[state] for state in states]
    
    def getStateSpaceSize(self):
        return len(self.states)
    

    def getCurrentValue(self, current_price):
        return self.portfolio_coin * current_price + self.portfolio_cash

    def getReturnsPercent(self, current_price):
        return 100 * (self.getCurrentValue(current_price) - self.starting_cash) / self.starting_cash

    def getCurrentHoldings(self, current_price):
        return "%.2f coins, %.2f cash, %.2f current value, %.2f percent returns" \
                % (self.portfolio_coin, self.portfolio_cash, self.getCurrentValue(current_price), self.getReturnsPercent())

    def apply_action(self, current_price, action):
        if action == Action.BUY:
            self.__buy(current_price, self.num_coins_per_order)
        elif action == Action.SELL:
            self.__sell(current_price, self.num_coins_per_order)
            
        # Update states
        self.state_dict["coin"] = self.portfolio_coin
        self.state_dict["cash"] = self.portfolio_cash
        self.state_dict["total_value"] = self.getCurrentValue(current_price)

    def getActionSpaceSize(self):
        return len(list(Action))

    def __buy(self, current_price, coins_to_buy=0):
        if not current_price:
            return 0
        amount_to_buy = min(self.portfolio_cash / current_price, coins_to_buy)
        self.portfolio_coin += amount_to_buy
        self.portfolio_cash -= amount_to_buy * current_price
        return amount_to_buy
    
    def __sell(self, current_price, coins_to_sell=0):
        if not current_price:
            return 0
        coin_to_sell = min(coins_to_sell, self.portfolio_coin)
        self.portfolio_coin -= coin_to_sell
        self.portfolio_cash += coin_to_sell * current_price
        return coin_to_sell

    def reset(self):
    	self.__init__(portfolio_cash=self.starting_cash)

