'''
env = Environment(coin_name="ethereum")
print env.step()
print env.step()
print env.step()
env.plot()
'''

import os
import pandas as pd 
import numpy as np


feature_list = ["current_price", "rolling_mean", "rolling_std", "cross_upper_band", "cross_lower_band"]

class Environment:
    def __init__(self, coin_name="ethereum", features=feature_list, recent_k = 0):
        self.coin_name = coin_name
        self.features = features

        self.series = pd.read_csv("%s/cryptocurrencypricehistory/%s_price.csv" % (os.path.dirname(os.path.abspath(__file__)), self.coin_name), parse_dates=["Date"])
        self.series.index = self.series.sort_values(by=["Date"]).index
        self.series = self.series.sort_index()
        
        if recent_k > 0:
            self.series = self.series[-recent_k:]
            self.series.index = [i for i in range(len(self.series))]
        
        self.length = len(self.series.index)
        self.current_index = 0
        self.__init()

    def __init(self):
        self.isDone = np.zeros(self.series["Open"].shape, dtype=bool)
        self.isDone[-1] = True 

        ### States
        self.rm = self.series["Open"].rolling(window=20, center=False, min_periods=0).mean()
        self.rstd = self.series["Open"].rolling(window=20, center=False, min_periods=0).std()
        self.upper_band, self.lower_band = self.rm + 2 * self.rstd, self.rm - 2 * self.rstd

        ### Mapping features to their names
        self.feature_dict = {}
        self.feature_dict["current_price"] = self.series["Open"]
        self.feature_dict["rolling_mean"] = self.rm
        self.feature_dict["rolling_std"] = self.rstd
        self.feature_dict["cross_upper_band"] = self.__crossUpperBand()
        self.feature_dict["cross_lower_band"] = self.__crossLowerBand()
        
        
    def __crossUpperBand(self):
        crossUpperBand = [0]
        for i in range(1, len(self.series)):
            crossUpperBand.append(self.__checkCrossUpperBand(i)*1)
        return crossUpperBand
    
    
    def __crossLowerBand(self):
        crossLowerBand = [0]
        for i in range(1, len(self.series)):
            crossLowerBand.append(self.__checkCrossLowerBand(i)*1)
        return crossLowerBand
    
        
    def __checkCrossUpperBand(self, curr_index):
        return (
            curr_index - 1 >= 0
            and self.upper_band.loc[curr_index - 1] <= self.feature_dict["current_price"][curr_index]
            and self.upper_band.loc[curr_index] > self.feature_dict["current_price"][curr_index]
        )
    
    def __checkCrossLowerBand(self, curr_index):
        return (
            curr_index - 1 >= 0
            and self.lower_band.loc[curr_index - 1] >= self.feature_dict["current_price"][curr_index]
            and self.lower_band.loc[curr_index] < self.feature_dict["current_price"][curr_index]
        )

    ## This is the only place where the state should be exposed
    ''' 
    isDone, state = env.step()
    '''
    def step(self):
        isDone = self.isDone[self.current_index]
        observation = []
        for feature in self.features:
            observation.append(self.feature_dict[feature][self.current_index])
        if not isDone:
            self.current_index += 1
        return isDone, observation

    def getStates(self, features=None):
        if not features:
            features = self.features
        return [self.feature_dict[feature][self.current_index] for feature in features]

    def getStateSpaceSize(self):
        return len(self.features)

    def plot(self, features_to_plot=None):
        import matplotlib.pyplot as plt
        if not features_to_plot:
            features_to_plot = self.features

        plt.figure()
        for feature in features_to_plot:
            ax = self.feature_dict[feature].plot()
        ax.legend(self.features)
        plt.show()

    def reset(self):
        self.current_index = 0

