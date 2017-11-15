from env import *
from simple_agents import * 
from portfolio import *

def run_random_agent(coin_name="ethereum"):
	ra = RandomAgent(Action)
	env = Environment(coin_name=coin_name)
	portfolio = Portfolio(env)

	is_done = False 
	state = env.getStates()

	while not is_done:
		action = ra.act()
		portfolio.apply_action(action)
		is_done, state = env.step()

	return portfolio.getReturnsPercent()


def run_bollingerband_agent(coin_name="ethereum"):
	bba = BollingerBandAgent(Action)
	env = Environment(coin_name=coin_name, \
		features=["higher_than_upper_band", "lower_than_lower_band"])
	portfolio = Portfolio(env)

	is_done = False 
	state = env.getStates()

	while not is_done:
		# print portfolio.getCurrentHoldings()
		action = bba.act(state)
		# print action
		portfolio.apply_action(action)
		is_done, state = env.step()

	return portfolio.getReturnsPercent()


def run_alwaysbuy_agent(coin_name="ethereum"):
	env = Environment(coin_name=coin_name, \
		features=["higher_than_upper_band", "lower_than_lower_band"])
	portfolio = Portfolio(env)

	is_done = False 
	state = env.getStates()

	while not is_done:
		portfolio.apply_action(Action.BUY)
		is_done, state = env.step()

	return portfolio.getReturnsPercent()

