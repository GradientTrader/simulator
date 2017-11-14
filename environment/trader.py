from simulator import *
from env import *
from portfolio import *


# Q Value Function Approximator
# Neural Network Implementation

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K
from keras.models import load_model

class QValue_NN:
    
    # init neural network
    def __init__(self, state_size, action_size, units):
        # define input and target shapes
        self._state_size = state_size
        self._action_size = action_size

        self._units = units
        
        # init model
        self._model = self._build_model()
    
    
    # define loss function
    def _huber_loss(self, target, prediction):
        # sqrt(1+error^2)-1
        error = prediction - target
        return K.mean(K.sqrt(1+K.square(error))-1, axis=-1)

    
    # neural net for Deep-Q Learning Model
    def _build_model(self):
        model = Sequential()
        model.add(Dense(self._units, input_dim=self._state_size, activation='relu'))
        model.add(Dense(self._units, activation='relu'))
        model.add(Dense(self._action_size, activation='linear'))
        model.compile(loss=self._huber_loss, optimizer='adam')
        return model

    
    # online training
    def train(self, state, qvalues):
        state_reshape = np.reshape(state, [1, len(state)])
        self._model.fit(state_reshape, qvalues, epochs=1, verbose=0)
    
    
    # get q-values based on state
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


# Cryptocurrency Trader Q-Learning Implementation

import random
import numpy as np
from collections import deque

class Crypto_Trader:

    def __init__(self, gamma = 0.95, epsilon = 1.0, epsilon_min = 0.01, epsilon_decay = 0.99, num_episodes = 1000,
                num_neutron = 24, num_coins_per_order = 100, init_capital = 1000, 
                coin_name = 'ethereum', recent_k = 0):

        self.memory = deque(maxlen=2000)
        self.batch_size = 300
        
        # Reward Discount Rate
        self.gamma = gamma

        # Esiplon (exploration factor)
        self.epsilon = epsilon
        
        self.epsilon_min = epsilon_min
        
        # Reduce exploration overtime
        self.epsilon_decay = epsilon_decay

        # number of episodes for training
        self.num_episodes = num_episodes
        
        # init simulator
        self.coin_name = coin_name
        self.simulator = Simulator(num_coins_per_order, init_capital, Coin(coin_name, recent_k))
        
        # init NN model
        self.model = QValue_NN(self.simulator.get_state_size(), self.simulator.get_action_size(), num_neutron)
        self.target_model = QValue_NN(self.simulator.get_state_size(), self.simulator.get_action_size(), num_neutron)

        
    def plot_coin_price(self):
        self.simulator.plot_coin_price()
        
        
    def act(self, state, epsilon):
        # Choose action by e-greedy
        if np.random.rand() < epsilon:
            #print 'random'
            return self.simulator.get_ran_action()
        
        # Get Q values, choose action by Q values
        act_values = self.model.predict(state)
        return Action(np.argmax(act_values[0]))
    
    
    def remember(self, state, action, reward, next_state, isDone):
        self.memory.append((state, action, reward, next_state, isDone))
        
        
    def update_target_model(self):
        # copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())
        
        
    def replay(self):
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, isDone in minibatch:
            target = self.model.predict(state)
            if isDone:
                target[0][action.value] = reward
            else:
                a = self.model.predict(next_state)[0]
                t = self.target_model.predict(next_state)[0]
                target[0][action.value] = reward + self.gamma * t[np.argmax(a)]
            self.model.train(state, target)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
        
    def train(self):
        for i in range(self.num_episodes):
            
            self.simulator.reset()
            state = self.simulator.get_current_state()
            
            while (True):
                
                action = self.act(state, self.epsilon)
                #print action
                
                # step to the next state and reward based on action
                next_state, reward, isDone = self.simulator.act_and_step(action)
                #print next_state
                #print reward
                
                self.remember(state, action, reward, next_state, isDone)
                state = next_state
                
                if isDone:
                    self.update_target_model()
                    print("episode: {}/{}, reward: {}, epsilon: {:.2}"
                          .format(i+1, self.num_episodes, reward, self.epsilon))
                    #print self.simulator.get_current_holdings()
                    break
            
            if len(self.memory) > self.batch_size:        
                self.replay()
                
        self.target_model.save('model/{}.model.v2.h5'.format(self.coin_name))
        
    
    def test(self, epsilon = None):
        if epsilon is None:
            epsilon = self.epsilon
        
        self.simulator.reset()
        # self.model.load('model/{}.model.v2.h5'.format(self.coin_name))
        state = self.simulator.get_current_state()
        while (True):
                
            action = self.act(state, epsilon)
                
            # step to the next state and reward based on action
            next_state, reward, isDone = self.simulator.act_and_step(action)
            print state, action, reward, next_state, isDone
                
            self.remember(state, action, reward, next_state, isDone)
            state = next_state
                
            if isDone:
                print("Test run: reward: {}, holdings: {}"
                          .format(reward, self.simulator.get_current_holdings()))
                break
