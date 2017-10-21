import pandas as pd 
import numpy as np


class Portfolio:
	def __init__(self, portfolio_cash=1000.0, coin=None):
		self.starting_cash = portfolio_cash
		self.coin = coin # note this is a coin obj
		self.portfolio_coin = 0
		self.portfolio_cash = portfolio_cash
		self.latest_coin_value = self.coin.getCurrentValue()

	def getCurrentValue(self):
		return self.portfolio_coin * self.coin.getCurrentValue() + self.portfolio_cash

	def getReturnsPercent(self):
		return 100 * (self.getCurrentValue() - self.starting_cash) / self.starting_cash

	def getCurrentHoldings(self):
		return "%.2f coins, %.2f cash, %.2f current value, %.2f percent returns" % (self.portfolio_coin, self.portfolio_cash, self.getCurrentValue(), self.getReturnsPercent())

	def executeOrder(self, coins_to_buy=0):
		future_value = self.coin.getFutureValue()
		if not future_value:
			return 0
		amount_to_buy = min(self.portfolio_cash / future_value, coins_to_buy)
		self.portfolio_coin += amount_to_buy
		self.portfolio_cash -= amount_to_buy * future_value
		return amount_to_buy
