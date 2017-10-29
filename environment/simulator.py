
# Cryptocurrency Market Simulator

from env import Coin
from portfolio import Portfolio
from random import randint


def enum(**enums): return type('Enum', (), enums)


class Simulator:

    Action = enum(HOLD=0, BUY=1, SELL=2)
    Num_Coins_Per_Order = 1

    def __init__(self, portfolio_cash=1000.0, coin=Coin("ethereum")):
        self.coin = coin
        self.portfolio = Portfolio(portfolio_cash=portfolio_cash, coin=coin)

    def get_ran_action(self):
        return randint(self.Action.HOLD, self.Action.SELL)

    def step(self, action):
        if action == self.Action.BUY:
            self.portfolio.executeOrder(coins_to_buy=self.Num_Coins_Per_Order)
        elif action == self.Action.SELL:
            self.portfolio.executeOrder(coins_to_buy=self.Num_Coins_Per_Order * -1)
        else:
            self.portfolio.executeOrder(coins_to_buy=0)

        if self.portfolio.step() is False:
            return [None, 0]

        state = self.portfolio.getCurrentState()
        reward = self.portfolio.getReturnsPercent()

        return [state, reward]
