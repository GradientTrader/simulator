from env import *
from simple_agents import * 
from portfolio import *

def run_random_agent(coin_name="ethereum", num_coins_per_order=100, recent_k=0):
	ra = RandomAgent(Action)
	env = Environment(coin_name=coin_name, recent_k=recent_k)
	portfolio = Portfolio(num_coins_per_order = num_coins_per_order)

	is_done = False 
	state = env.getStates()

	while not is_done:
		action = ra.act()
		portfolio.apply_action(state[0], action)
		is_done, state = env.step()

	return portfolio.getReturnsPercent(state[0])


def run_bollingerband_agent(coin_name="ethereum", num_coins_per_order=100, recent_k=0):
	bba = BollingerBandAgent()
	env = Environment(coin_name=coin_name, recent_k=recent_k, \
		features=["current_price", "cross_upper_band", "cross_lower_band"])
	portfolio = Portfolio(num_coins_per_order = num_coins_per_order)

	is_done = False 
	state = env.getStates()

	while not is_done:
		# print portfolio.getCurrentHoldings()
		action = bba.act(state)
		# print action
		portfolio.apply_action(state[0], action)
		is_done, state = env.step()

	return portfolio.getReturnsPercent(state[0])


def run_alwaysbuy_agent(coin_name="ethereum", num_coins_per_order=100, recent_k=0):
	env = Environment(coin_name=coin_name, recent_k=recent_k)
	portfolio = Portfolio(num_coins_per_order = num_coins_per_order)

	is_done = False 
	state = env.getStates()

	while not is_done:
		portfolio.apply_action(state[0], Action.BUY)
		is_done, state = env.step()

	return portfolio.getReturnsPercent(state[0])

