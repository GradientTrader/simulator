'''

### Cryptocurrency Trader Agent
### UCB MIDS 2017 Winter Capstone Project
### Ramsey Aweti, Shuang Chan, GuangZhi(Frank) Xie, Jason Xie

### Class: 
###        Environment
### Purpose: 
###        This is utility class used to simulate the cryptocurrency markets.
###        It maintains the state list of the environment.
### Sample Usage:

env = Environment(coin_name="ethereum")
print env.step()
print env.step()
print env.step()
env.plot()

'''

import os
import pandas as pd 
import numpy as np


state_list = ["current_price", "rolling_mean", "rolling_std", "cross_upper_band", "cross_lower_band", "upper_band",
             "lower_band", "price_over_sma"]

class Environment:
    
    # load pricing data
    # initialize the environment variables
    def __init__(self, coin_name="ethereum", states=state_list, recent_k = 0):
        self.coin_name = coin_name
        self.states = states

        self.series = pd.read_csv("%s/cryptocurrencypricehistory/%s_price.csv" 
                                  % (os.path.dirname(os.path.abspath(__file__)), self.coin_name), 
                                  parse_dates=["Date"])
        
        self.series.index = self.series.sort_values(by=["Date"]).index
        self.series = self.series.sort_index()
        
        if recent_k > 0:
            self.series = self.series[-recent_k:]
            self.series.index = [i for i in range(len(self.series))]
        
        self.length = len(self.series.index)
        self.current_index = 0
        self.__init()

    # deriving the features used for the state definition
    def __init(self):
        self.isDone = np.zeros(self.series["Open"].shape, dtype=bool)
        self.isDone[-1] = True 

        ### States
        self.rm = self.series["Open"].rolling(window=20, center=False, min_periods=0).mean()
        self.rstd = self.series["Open"].rolling(window=20, center=False, min_periods=0).std()
        self.upper_band, self.lower_band = self.rm + 2 * self.rstd, self.rm - 2 * self.rstd

        ### Mapping states to their names
        self.state_dict = {}
        self.state_dict["current_price"] = self.series["Open"]
        self.state_dict["rolling_mean"] = self.rm
        self.state_dict["rolling_std"] = self.rstd
        self.state_dict["cross_upper_band"] = self.__crossUpperBand()
        self.state_dict["cross_lower_band"] = self.__crossLowerBand()
        self.state_dict["upper_band"] = self.upper_band
        self.state_dict["lower_band"] = self.lower_band
        self.state_dict["price_over_sma"] = self.series["Open"]/self.rm
        
        
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
            and self.upper_band.loc[curr_index - 1] <= self.state_dict["current_price"][curr_index]
            and self.upper_band.loc[curr_index] > self.state_dict["current_price"][curr_index]
        )
    
    def __checkCrossLowerBand(self, curr_index):
        return (
            curr_index - 1 >= 0
            and self.lower_band.loc[curr_index - 1] >= self.state_dict["current_price"][curr_index]
            and self.lower_band.loc[curr_index] < self.state_dict["current_price"][curr_index]
        )

    ## This is the only place where the state should be exposed
    ''' 
    isDone, state = env.step()
    '''
    # simulate a forward step in the environment, i.e.: moving one day
    def step(self):
        isDone = self.isDone[self.current_index]
        observation = []
        for state in self.states:
            observation.append(self.state_dict[state][self.current_index])
        if not isDone:
            self.current_index += 1
        return isDone, observation

    def getStates(self, states=None):
        if not states:
            states = self.states
        return [self.state_dict[state][self.current_index] for state in states]

    def getStateSpaceSize(self):
        return len(self.states)
    
    
    ## Add method to get current price as it is commonly used
    def getCurrentPrice(self):
        return self.state_dict["current_price"][self.current_index]
    
    def getFinalPrice(self):
        return self.state_dict["current_price"][self.length-1]
    

    def plot(self, states_to_plot=None):
        import matplotlib.pyplot as plt
        if not states_to_plot:
            states_to_plot = self.states

        plt.figure()
        for state in states_to_plot:
            ax = self.state_dict[state].plot()
        ax.legend(states_to_plot)
        plt.show()

    def reset(self):
        self.current_index = 0

