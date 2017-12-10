
'''

### Cryptocurrency Trader Agent
### UCB MIDS 2017 Winter Capstone Project
### Ramsey Aweti, Shuang Chan, GuangZhi(Frank) Xie, Jason Xie

### Class: 
###        Portfolio
### Purpose: 
###        This is utility class used to maintain action, reward and internal state definitions.
###        
### Sample Usage:

from env import *
env = Environment(coin_name="ethereum")
p = Portfolio(env)

print env.getStates() ## initial step
p._buy(10)
print env.step()
print p.getCurrentHoldings()

'''

import math
import numpy as np
from enum import Enum

# action list
class Action(Enum):
    HOLD=0
    BUY=1
    SELL=2

# internal state
state_list = ["coin", "cash", "total_value", "is_holding_coin", "return_since_entry"]
spread = 0.01 # 1 bps

def _round_up(v):
    return (math.ceil(v*10000)/10000)

def _round_down(v):
    return (math.floor(v*10000)/10000)

class Portfolio:
    
    # initialize the portfolio variables
    def __init__(self, portfolio_cash=1000.0, num_coins_per_order=10.0, states=state_list, verbose=False, final_price=0.0):
        self.verbose = verbose
        self.final_price = final_price
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
        self.state_dict["is_holding_coin"] = 0
        self.state_dict["return_since_entry"] = 0
        
        self.bought_price = 0.0

    def __buy(self, current_price):
        if not current_price:
            return 0
        
        buy_price = current_price * (1 + spread)
        
        if self.num_coins_per_order == 0:
            coin_to_buy = _round_down(self.portfolio_cash / buy_price)
        else:
            coin_to_buy = min(_round_down(self.portfolio_cash / buy_price), self.num_coins_per_order)
        
        if self.verbose:
            print "original coin", self.portfolio_coin, "original cash", self.portfolio_cash, "price", buy_price   
            
        self.portfolio_coin += coin_to_buy
        self.portfolio_cash -= coin_to_buy * buy_price
        
        if self.verbose:
            print "coin to buy", coin_to_buy, "coin now", self.portfolio_coin, "cash now", self.portfolio_cash
        
        return coin_to_buy, buy_price
    
    def __sell(self, current_price):
        if not current_price:
            return 0
        
        sell_price = current_price * (1 - spread)
        
        if self.num_coins_per_order == 0:
            coin_to_sell = self.portfolio_coin
        else:
            coin_to_sell = min(self.num_coins_per_order, self.portfolio_coin)
        
        if self.verbose:
            print "original coin", self.portfolio_coin, "original cash", self.portfolio_cash, "price", sell_price
        
        self.portfolio_coin -= coin_to_sell
        self.portfolio_cash += coin_to_sell * sell_price
        
        if self.verbose:
            print "coin to sell", coin_to_sell, "coin now", self.portfolio_coin, "cash now", self.portfolio_cash
        
        return coin_to_sell, sell_price
    
    # reset portfolio
    def reset(self):
        self.__init__(portfolio_cash=self.starting_cash, num_coins_per_order=self.num_coins_per_order, 
                      states=self.states, verbose=self.verbose)
        
    # return internal state    
    def getStates(self, states=None):
        if not states:
            states = self.states
        return [self.state_dict[state] for state in states]
    
    # reward defintion
    def getReward(self):
        return self.reward

    # apply action (buy, sell or hold) to the portfolio
    # update the internal state after the action
    def apply_action(self, current_price, action):
        self.reward = self.getCurrentValue(current_price) - self.state_dict["total_value"] # Reward for HOLD
        self.state_dict["total_value"] = self.getCurrentValue(current_price)
        if self.verbose:
            print "Action start", action, "Total value before action", self.state_dict["total_value"]           
        
        if action == Action.BUY:
            coin_to_buy, buy_price = self.__buy(current_price)
            if coin_to_buy > 0:
                self.bought_price = buy_price
                self.reward = -spread * current_price * coin_to_buy # Reward for BUY
            else:
                action = Action.HOLD
                
        elif action == Action.SELL:
            coin_to_sell, sell_price = self.__sell(current_price)
            if coin_to_sell > 0:
                self.reward = (sell_price - self.bought_price) * coin_to_sell # Reward for SELL
            else:
                action = Action.HOLD
        
        # Update states
        self.state_dict["coin"] = self.portfolio_coin
        self.state_dict["cash"] = self.portfolio_cash
        self.state_dict["total_value"] = self.getCurrentValue(current_price)
        self.state_dict["is_holding_coin"] = (self.portfolio_coin > 0)*1
        self.state_dict["return_since_entry"] = self.getReturnsPercent(current_price)
        
        if self.verbose:
            print "Action end:", action, "Reward:", self.getReward()
            
        return action
        

    def getCurrentValue(self, current_price):
        sell_price = current_price * (1 - spread)
        return self.portfolio_coin * sell_price + self.portfolio_cash

    def getReturnsPercent(self, current_price):
        return 100 * (self.getCurrentValue(current_price) - self.starting_cash) / self.starting_cash

    def getCurrentHoldings(self, current_price):
        return "%.2f coins, %.2f cash, %.2f current value, %.2f percent returns" \
                % (self.portfolio_coin, self.portfolio_cash, self.getCurrentValue(current_price), 
                   self.getReturnsPercent(current_price))
        
    def getActionSpaceSize(self):
        return len(list(Action))
    
    def getStateSpaceSize(self):
        return len(self.states)



