from env import *
from portfolio import *

### 

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K
from keras.models import load_model



class QValue_NN:
    def __init__(self, state_size, action_size, units):
        self._state_size = state_size
        self._action_size = action_size
        self._units = units
        self._model = self._build_model()
        
    def _huber_loss(self, target, prediction):
        # sqrt(1+error^2)-1
        error = prediction - target
        return K.mean(K.sqrt(1+K.square(error))-1, axis=-1)

    def _build_model(self):
        model = Sequential()
        model.add(Dense(self._units, input_dim=self._state_size, activation='relu'))
        model.add(Dense(self._units, activation='relu'))
        model.add(Dense(self._action_size, activation='linear'))
        model.compile(loss=self._huber_loss, optimizer='adam')
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


class DDQNAgent:
    def __init__(self, gamma=0.95, num_neutron=24, epsilon_min = 0.001, epsilon_decay=0.99, 
                 init_capital=1000, coin_name='ethereum', num_coins_per_order=100, recent_k = 0,
                 feature_list = ["current_price", "rolling_mean", "rolling_std", 
                                 "cross_upper_band", "cross_lower_band"]):
        self.memory = deque(maxlen=2000)
        self.batch_size = 32
        self.gamma = gamma
        self.epsilon=1.0
        self.epsilon_min=epsilon_min 
        self.epsilon_decay=epsilon_decay
        self.coin_name = coin_name
        self.feature_list = feature_list
        self.env = Environment(coin_name=coin_name, features=feature_list, recent_k=recent_k)
        self.portfolio = Portfolio()
        self.model = QValue_NN(self.env.getStateSpaceSize(), self.portfolio.getActionSpaceSize(), num_neutron)
        self.target_model = QValue_NN(self.env.getStateSpaceSize(), self.portfolio.getActionSpaceSize(), num_neutron)
     
    def plot_features(self):
        self.env.plot(self.feature_list)
    
    
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.choice(list(Action))
        act_values = self.model.predict(state)
        return Action(np.argmax(act_values[0]))
        
    def remember(self, state, action, reward, next_state, isDone):
        self.memory.append((state, action, reward, next_state, isDone))
        
    def update_target_model(self):
        self.target_model._model.set_weights(self.model._model.get_weights())
        
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, isDone in minibatch:
            target = self.model.predict(state)
            if isDone:
                target[0][action.value] = reward
            else:
                a = self.model.predict(next_state)[0]
                t = self.target_model.predict(next_state)[0]
                target[0][action.value] = reward + self.gamma * t[np.argmax(a)]
                ## -0.60 + gamma * -0.50
            self.model.train(state, target)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def train(self, num_episodes=100):
        for i in range(num_episodes):
            
            self.env.reset()
            self.portfolio.reset()
            state = self.env.getStates()

            while (True):
                action = self.act(state)
                self.portfolio.apply_action(state[0], action)
                isDone, next_state = self.env.step()
                reward = self.portfolio.getReturnsPercent(state[0])
                self.remember(state, action, reward, next_state, isDone)
                state = next_state
                
                if isDone:
                    self.update_target_model()
                    print("episode: {}/{}, reward: {}, epsilon: {:.2}"
                          .format(i+1, num_episodes, reward, self.epsilon))
                    break
                    
            if len(self.memory) > self.batch_size:
                self.replay(self.batch_size)
                
        self.target_model.save('model/{}.model.h5'.format(self.coin_name))
                
    
    def test(self, epsilon = None):
        if epsilon is None:
            epsilon = self.epsilon
        
        self.env.reset()
        self.portfolio.reset()
        state = self.env.getStates()
        self.model.load('model/{}.model.h5'.format(self.coin_name))

        while (True):
            action = self.act(state)
            print action
            self.portfolio.apply_action(state[0], action)
            isDone, next_state = self.env.step()
            reward = self.portfolio.getReturnsPercent(state[0])
            state = next_state
            if isDone:
            	break

        print self.portfolio.getReturnsPercent(state[0])      

# trader = DDQNAgent()
# trader.train(50)
# trader.test()
