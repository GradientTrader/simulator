## to do: add side coin information! 

import os
import pandas as pd 
import numpy as np


available_coins = ["bitcoin_cash", "bitcoin", "bitconnect", "dash_price", "ethereum_classic", "ethereum", "iota", "litecoin", "monero", "nem", "neo", "numeraire", "omisego", "qtum", "ripple", "stratis", "waves"]


class Coin:
    def __init__(self, coin_name="ethereum"):
        if coin_name not in available_coins:
            raise Exception("Bad coin name!")
        self.coin_name = coin_name
        self.series = pd.read_csv("%s/cryptocurrencypricehistory/%s_price.csv" % (os.path.dirname(os.path.abspath(__file__)), self.coin_name), parse_dates=["Date"])
        self.series.index = self.series.sort_values(by=["Date"]).index ## reorder so that date increases
        self.length = len(self.series.index)
        self.current_index = 0

        #compute rolling mean and bollinger bands
        self.rm = pd.rolling_mean(self.series["Close"], window=20)
        self.rstd = pd.rolling_std(self.series["Close"], window=20)
        self.upper_band, self.lower_band = self.rm + 2 * self.rstd, self.rm - 2 * self.rstd

    def getNext(self):
        if self.current_index == self.length:
            return None
        data = self.series.loc[self.current_index]
        self.current_index += 1
        return data

    def getCurrentValue(self):
        if self.current_index >= self.length:
            return self.series.loc[self.length - 1]["Close"]
        return self.series.loc[self.current_index]["Close"]

    def getFutureValue(self):
        if self.current_index + 1 >= self.length:
            return None
        return self.series.loc[self.current_index + 1]["Close"]

    def checkBollingerBands(self):
        IsGreaterThanUpper = 0
        if np.isnan(self.upper_band[self.current_index]) is False \
                and self.upper_band[self.current_index] < self.getCurrentValue():
            IsGreaterThanUpper = 1

        IsSmallerThanLower = 0
        if np.isnan(self.lower_band[self.current_index]) is False \
                and self.lower_band[self.current_index] > self.getCurrentValue():
            IsSmallerThanLower = 1

        return [IsGreaterThanUpper, IsSmallerThanLower]


# a = Coin("ethereum")
# print a.series.loc[0]
# # print a.getCurrentValue()
# print a.series.index
