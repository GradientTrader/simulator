
'''

### Cryptocurrency Trader Agent
### UCB MIDS 2017 Winter Capstone Project
### Ramsey Aweti, Shuang Chan, GuangZhi(Frank) Xie, Jason Xie

### Class: 
###        DDQNAgent
### Purpose: 
###        Deep Q Learning Implementation
### Sample Usage:

# trader = DDQNAgent()
# trader.train(50)
# trader.test()

'''

from env import *
from portfolio import *

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K
from keras import initializers
from keras.models import load_model

# Neural Network for the Q value approximation
class QValue_NN:
    def __init__(self, state_size, action_size, units):
        self._state_size = state_size
        self._action_size = action_size
        self._units = units
        self._model = self.__build_model()
        
    def __huber_loss(self, target, prediction):
        # sqrt(1+error^2)-1
        error = prediction - target
        return K.mean(K.sqrt(1+K.square(error))-1, axis=-1)

    def __build_model(self):
        model = Sequential()
        model.add(Dense(self._units, input_dim=self._state_size, activation='relu',
                       kernel_initializer=initializers.RandomNormal(stddev=0.001, seed=3456),
                       bias_initializer='zeros'))
        model.add(Dense(self._units, activation='relu',
                       kernel_initializer=initializers.RandomNormal(stddev=0.001, seed=3456),
                       bias_initializer='zeros'))
        model.add(Dense(self._action_size, activation='linear',
                       kernel_initializer=initializers.RandomNormal(stddev=0.001, seed=3456),
                       bias_initializer='zeros'))
        model.compile(loss=self.__huber_loss, optimizer="adam")
        return model

    def train(self, state, qvalues):
        state_reshape = np.reshape(state, [1, len(state)])
        self._model.fit(state_reshape, qvalues, epochs=1, verbose=0)

    def predict(self, state):
        state_reshape = np.reshape(state, [1, len(state)])
        return self._model.predict(state_reshape)
    
    def set_weights(self, model_weights):
        self._model.set_weights(model_weights)
        
    def get_weights(self):
        return self._model.get_weights()
    
    def save(self, path):
        self._model.save_weights(path)
        
    def load(self, path):
        self._model.load_weights(path)
        

import random
import numpy as np
from collections import deque

# Agent Implementation

class DDQNAgent:
    
    # initialize internal variables
    def __init__(self, gamma=0.95, num_neutron=24, epsilon_min = 0.001, epsilon_decay=0.995, 
                 coin_name='ethereum', num_coins_per_order=100, recent_k = 0,
                 external_states = ["current_price", "rolling_mean", "rolling_std", 
                                 "cross_upper_band", "cross_lower_band"],
                 internal_states = ["coin", "cash", "total_value"], verbose=False):
        self.memory = deque(maxlen=2000)
        self.batch_size = 32
        self.gamma = gamma
        self.epsilon=1.0
        self.epsilon_min=epsilon_min 
        self.epsilon_decay=epsilon_decay
        self.coin_name = coin_name
        # External states
        self.external_states = external_states
        self.env = Environment(coin_name=coin_name, states=external_states, recent_k=recent_k)
        # Internal states
        self.internal_states = internal_states
        self.portfolio = Portfolio(num_coins_per_order=num_coins_per_order, states=internal_states,
                                   verbose=verbose, final_price=self.env.getFinalPrice())
        # NN model
        _state_size = self.env.getStateSpaceSize() + self.portfolio.getStateSpaceSize()
        self.model = QValue_NN(_state_size, self.portfolio.getActionSpaceSize(), num_neutron)
        self.target_model = QValue_NN(_state_size, self.portfolio.getActionSpaceSize(), num_neutron)
        
        self.cum_returns = []
     
    def plot_external_states(self):
        self.env.plot(self.external_states)
    
    
    def __act(self, state):
        if np.random.rand() < self.epsilon:
            return random.choice(list(Action))
        act_values = self.model.predict(state)
        return Action(np.argmax(act_values[0]))
        
    def __remember(self, state, action, reward, next_state, isDone):
        self.memory.append((state, action, reward, next_state, isDone))
        
    def __update_target_model(self):
        self.target_model._model.set_weights(self.model._model.get_weights())

    def print_my_memory(self):
        mem = list(self.memory)
        mem_str = []
        for s, a, r, s_, donzo in mem:
            mem_str += ["%s_%s_%s_%s_%s" % (str(s), str(a), str(r), str(s_), str(donzo))]
    
        uniques = list(set(mem_str))
        uniques.sort() 
        
        for elem in uniques:
            print elem
            print mem_str.count(elem)
            print "\n"
        
    def __replay(self, batch_size):
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, isDone in minibatch:
            target = self.model.predict(state)
            if isDone:
                target[0][action.value] = reward
            else:
                a = self.model.predict(next_state)[0]
                t = self.target_model.predict(next_state)[0]
                
                # Bellman Equation
                # -0.60 + gamma * -0.50
                target[0][action.value] = reward + self.gamma * t[np.argmax(a)]

            self.model.train(state, target)
        
        # update the epsilon to gradually reduce the random exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # Agent Training
    def train(self, num_episodes=100):
        self.cum_returns = []
        
        for i in range(num_episodes):
            
            self.env.reset()
            self.portfolio.reset()
            state = self.env.getStates() + self.portfolio.getStates()

            # walk through the environment
            # obtain action based on state values using the Neural Network model
            # collect reward
            # update the experience in Memory
            while (True):
                action = self.__act(state)
                action = self.portfolio.apply_action(self.env.getCurrentPrice(), action)
                
                isDone, next_state = self.env.step()
                next_state = next_state + self.portfolio.getStates()
                #reward = self.portfolio.getReward()
                reward = self.env.getReward(action)
                
                self.__remember(state, action, reward, next_state, isDone)
                state = next_state
                
                if isDone:
                    self.__update_target_model()
                    
                    cum_return = self.portfolio.getReturnsPercent(self.env.getCurrentPrice())
                    self.cum_returns.append(cum_return)
                    
                    print("episode: {}/{}, returns: {}, epsilon: {:.2}"
                          .format(i+1, num_episodes, 
                                  cum_return, 
                                  self.epsilon))
                    break
             
            # train the Neural Network incrementally with the new experiences
            if len(self.memory) > self.batch_size:
                self.__replay(self.batch_size)
                
        self.target_model.save('model/{}.model.h5'.format(self.coin_name))
                
    
    def test(self, epsilon = None):
        if epsilon is not None:
            self.epsilon = epsilon
        
        self.env.reset()
        self.portfolio.reset()
        state = self.env.getStates() + self.portfolio.getStates()
        self.model.load('model/{}.model.h5'.format(self.coin_name))

        while (True):
            action = self.__act(state)
            action = self.portfolio.apply_action(self.env.getCurrentPrice(), action)
            print action
            
            isDone, next_state = self.env.step()
            next_state = next_state + self.portfolio.getStates()
            state = next_state
            
            if isDone:
            	break

        print self.portfolio.getReturnsPercent(self.env.getCurrentPrice())
        
   
    def plot_cum_returns(self):
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10,6))
        x = [i for i in range(len(self.cum_returns))]
        plt.plot(x, self.cum_returns)
        plt.show()
        
    def plot_env(self, states_to_plot=None):
        self.env.plot(states_to_plot)
