## to do: add side coin information! 

import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


available_coins = ["bitcoin_cash", "bitcoin", "bitconnect", "dash_price", "ethereum_classic", "ethereum", "iota", "litecoin", "monero", "nem", "neo", "numeraire", "omisego", "qtum", "ripple", "stratis", "waves"]


class Coin:
    def __init__(self, coin_name="ethereum", recent_k = 0):
        if coin_name not in available_coins:
            raise Exception("Bad coin name!")
        self.coin_name = coin_name
        self.series = pd.read_csv("%s/cryptocurrencypricehistory/%s_price.csv" % (os.path.dirname(os.path.abspath(__file__)), self.coin_name), parse_dates=["Date"])
        ## reorder so that date increases
        self.series.index = self.series.sort_values(by=["Date"]).index
        self.series = self.series.sort_index()
        
        if recent_k > 0:
            self.series = self.series[-recent_k:]
            self.series.index = [i for i in range(len(self.series))]
        
        self.length = len(self.series.index)
        self.current_index = 0

        #compute rolling mean and bollinger bands
        self.rm = self.series["Open"].rolling(window=20,center=False).mean()
        self.rstd = self.series["Open"].rolling(window=20,center=False).std()
        self.upper_band, self.lower_band = self.rm + 2 * self.rstd, self.rm - 2 * self.rstd
        
        
    def plot(self):
        ax = self.series["Open"].plot()
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        plt.show()

    
    def advance(self):
        if self.current_index+1 < self.length:
            self.current_index += 1
            data = self.series.loc[self.current_index]
            return data
        else:
            return None
        
    def advance_n_step(self, step):
        if self.current_index+step < self.length:
            self.current_index += step
            data = self.series.loc[self.current_index]
            return data
        else:
            return None 

    def getCurrentValue(self):
        return self.series.loc[self.current_index]["Open"]
    

    def getNextValue(self):
        if self.current_index + 1 >= self.length:
            return None
        return self.series.loc[self.current_index + 1]["Open"]

    def checkBollingerBands(self):
        isCrossUpperBand = 0
        if self.checkCrossUpperBand():
            isCrossUpperBand = 1

        isCrossLowerBand = 0
        if self.checkCrossLowerBand():
            isCrossLowerBand = 1

        return [isCrossUpperBand, isCrossLowerBand]
    
    
    def checkCrossUpperBand(self):
        return (
            self.current_index - 1 >= 0
            and self.upper_band.loc[self.current_index - 1] <= self.getCurrentValue()
            and self.upper_band.loc[self.current_index] > self.getCurrentValue()
        )
    
    def checkCrossLowerBand(self):
        return (
            self.current_index - 1 >= 0
            and self.lower_band.loc[self.current_index - 1] >= self.getCurrentValue()
            and self.lower_band.loc[self.current_index] < self.getCurrentValue()
        )
    
    
    def reset(self):
        self.current_index = 0
    
    
    
    

