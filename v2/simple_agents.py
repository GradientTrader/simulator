import random 
from portfolio import Action

'''
ra = RandomAgent(Action)
print ra.act()
print ra.act()
print ra.act()
'''
class RandomAgent:
    def __init__(self, Action):
        self.Action = Action

    def act(self, state=None):
        return random.choice(list(self.Action))

'''
bba = BollingerBandAgent(Action)
print bba.act([0, 0])
print bba.act([1, 0])
print bba.act([0, 1])
'''
class BollingerBandAgent:

    def act(self, state):
    	cross_upper_band, cross_lower_band = state 
    	if cross_upper_band:
    		return Action.SELL
    	if cross_lower_band:
    		return Action.BUY
    	return Action.HOLD


