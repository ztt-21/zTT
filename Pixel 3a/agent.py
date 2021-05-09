#!/usr/bin/env python3

import warnings
import os
from threading import Thread
import time
import numpy as np
import random
import socket
import struct
import math

with warnings.catch_warnings():  
	warnings.filterwarnings("ignore",category=FutureWarning)
	from keras import backend as K
	from collections import defaultdict
	from keras.models import Sequential
	from keras.optimizers import Adam
	from keras.layers import Dense
	from collections import deque
	import tensorflow as tf
	import matplotlib.pyplot as plt
	

PORT = 8702
experiment_time=500 #14100
clock_change_time=30
cpu_power_limit=1000
gpu_power_limit=1600
action_space=9
target_fps=60
target_temp=65
beta=2 #4

config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)
K.set_session(sess)

class DQNAgent:
	def __init__(self, state_size, action_size):
		self.load_model = False
		self.training=0
		self.state_size=state_size
		self.action_size=action_size
		self.actions=list(range(9))
		self.q_table=defaultdict(lambda:[0.0 for i in range(action_space)])
		self.clk_action_list=[]
		for i in range(3):
			for j in range(3):
				clk_action=(3*i+2,j+1)
				self.clk_action_list.append(clk_action)

		# Hyperparameter
		self.learning_rate=0.05    # 0.01
		self.discount_factor=0.99
		self.epsilon=1
		self.epsilon_decay=0.08 # 0.99
		self.epsilon_min = 0 # 0.1
		self.epsilon_start, self.epsilon_end = 1.0, 0.0 # 1.0, 0.1
#		self.exploration_steps = 500
#		self.epsilon_decay_step = (self.epsilon_start - self.epsilon_end) / self.exploration_steps
		self.batch_size = 64
		self.train_start = 150 #200
#		self.update_target_rate = 10000
		self.q_max=0
		self.avg_q_max=0
		self.currentLoss=0
		# Replay memory (=500)
		self.memory = deque(maxlen=500)
#		self.no_op_steps = 30
		# model initialization
		self.model = self.build_model()
		self.target_model = self.build_model()
		self.update_target_model()
		if self.load_model:
			self.model.load_weights("./save_model/model.h5")
			self.epsilon_start = 0.1
		

#	def get_flops(model):
#		run_meta = tf.RunMetadata()
#		opts = tf.profiler.ProfileOptionBuilder.float_operation()

		# We use the Keras session graph in the call to the profiler.
#		flops = tf.profiler.profile(graph=K.get_session().graph,
#		run_meta=run_meta, cmd='op', options=opts)
		        

#		return flops.total_float_ops  # Prints the "flops" of the model.


# .... Define your model here ....
                
	
	def optimizer(self):
		a = K.placeholder(shape=(None,), dtype='int32')
		y = K.placeholder(shape=(None,), dtype='float32')
		prediction=self.model.output
		
		a_one_hot = K.one_hot(ac, self.action_size)
		q_value = K.sum(prediction * a_one_hot, axis=1)
		error = K.abs(y - q_value)

		quadratic_part = K.clip(error, 0.0, 1.0)
		linear_part = error - quadratic_part
		loss = K.mean(0.5 * K.square(quadratic_part) + linear_part)

		optimizer = RMSprop(lr=0.00025, epsilon = 0.01)
		updates = optimizer.get_updates(self.model.trainable_weights, [], loss)
		train = K.function([self.model.input, a, y], [loss], updates=updates)

		return train
	
	def build_model(self):
		model = Sequential()
		model.add(Dense(6, input_dim=self.state_size, activation='relu', kernel_initializer='normal'))
		model.add(Dense(6, activation='relu', kernel_initializer='normal'))
		model.add(Dense(self.action_size, activation='linear', kernel_initializer='normal'))
		model.summary()
		model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
		return model
	def update_target_model(self):
		self.target_model.set_weights(self.model.get_weights())
	
	def get_action(self, state):
		state=np.array([state])
		#print('state={}'.format(state))
		if np.random.rand() <= self.epsilon:
			q_value=self.model.predict(state)
			print('state={}, q_value={}, action=exploration, epsilon={}'.format(state[0], q_value[0], self.epsilon))
			return random.randrange(self.action_size)
		else:
			q_value = self.model.predict(state)
			print('state={}, q_value={}, action={}, epsilon={}'.format(state[0], q_value[0], np.argmax(q_value[0]), self.epsilon))
			return np.argmax(q_value[0])
	
	def append_sample(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done))

	def train_model(self):
		self.training=1

		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay
		else:
			self.epsilon = self.epsilon_min
			

		mini_batch = random.sample(self.memory, self.batch_size)

		states = np.zeros((self.batch_size, self.state_size))
		next_states = np.zeros((self.batch_size, self.state_size))
		actions, rewards, dones = [], [], []

		for i in range(self.batch_size):
			states[i] = mini_batch[i][0]
			actions.append(mini_batch[i][1])
			rewards.append(mini_batch[i][2])
			next_states[i] = mini_batch[i][3]
			dones.append(mini_batch[i][4])


		target = self.model.predict(states)
		target_val = self.target_model.predict(next_states)


		for i in range(self.batch_size):
			if dones[i]:
				target[i][actions[i]] = rewards[i]
			else:
				target[i][actions[i]] = rewards[i] + self.discount_factor * (np.amax(target_val[i]))

		hist = self.model.fit(states, target, batch_size=self.batch_size, epochs=1, verbose=0)
		self.currentLoss = hist.history['loss'][0]
		print('loss = {}'.format(self.currentLoss))
		self.training=0


		return action
	@staticmethod
	def arg_max(state_action):
		max_index_list=[]
		max_value=state_action[0]
		for index, value in enumerate(state_action):
			if value > max_value:
				max_index_list.clear()
				max_value=value
				max_index_list.append(index)
			elif value==max_value:
				max_index_list.append(index)
		print('{}  {}'.format(max_index_list,max_value))
		return random.choice(max_index_list)



def get_reward(fps, power, target_fps, c_t, g_t, c_t_prev, g_t_prev, beta):
	v1=0
	v2=0
	print('power={}'.format(power))
	u=max(1,fps/target_fps)

	if g_t<= target_temp:
		v2=0
	else:
		v2=2*(target_temp-g_t)
	if c_t_prev < target_temp:
		if c_t >= target_temp:
			v1=-2

	if fps>=target_fps:
		u=1
	else :
		u=math.exp(0.1*(fps-target_fps))
	return u+v1+v2+beta/power
	
if __name__=="__main__":

	agent = DQNAgent(7,9)
	scores, episodes = [], []

	t=1
	learn=1
	ts=[]
	fps_data=[]
	power_data=[]
	avg_q_max_data=[]
	loss_data = []
	avg_reward=[]
	reward_tmp=[]

	cnt=0
	c_c=3
	g_c=3
	c_t=37
	g_t=37
	c_t_prev=37
	g_t_prev=37
	print("TCPServr Waiting on port 8702")
	state=(3,3,20,27,40,40,30)
	score=0
	action=0
	copy=1

	clk=11
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("", PORT))
	server_socket.listen(5)

	try:
		client_socket, address = server_socket.accept()
		fig = plt.figure(figsize=(12,14))
		ax1 = fig.add_subplot(4, 1, 1)
		ax2 = fig.add_subplot(4, 1, 2)
		ax3 = fig.add_subplot(4, 1, 3)
		ax4 = fig.add_subplot(4, 1, 4)

		while t<experiment_time:
			msg = client_socket.recv(512).decode()
			state_tmp = msg.split(',')
			
			if not msg:
				print('No receiveddata')
				break
			c_t_prev=c_t
			g_t_prev=g_t
			c_c=int(state_tmp[0])
			g_c=int(state_tmp[1])
			c_p=int(state_tmp[2])
			g_p=int(state_tmp[3])
			c_t=float(state_tmp[4])
			g_t=float(state_tmp[5])
			fps=float(state_tmp[6])

			ts.append(t)
			fps_data.append(fps)
			power_data.append((c_p+g_p)*100)
			

			next_state=(c_c, g_c, c_p, g_p, c_t, g_t,fps)
			agent.q_max+=np.amax(agent.model.predict(np.array([next_state])))
			agent.avg_q_max=agent.q_max/(t)
			avg_q_max_data.append(agent.avg_q_max)
			loss_data.append(agent.currentLoss)

			# reward
			reward = get_reward(fps, c_p+g_p, target_fps, c_t, g_t, c_t_prev, g_t_prev, beta)

			# Handle dummy value at the first sensing
			if (c_p+g_p<=0):
				c_p=20
				g_p=13
			reward = get_reward(fps, c_p+g_p, target_fps, c_t, g_t, c_t_prev, g_t_prev, beta)
			reward_tmp.append(reward)
			if(len(reward_tmp)>=300) :
				reward_tmp.pop(0)

			done = 1
			# replay memory
			agent.append_sample(state, action, reward, next_state, done)
			for i in range(copy):
				if reward<0:
					agent.append_sample(state, action, reward, next_state, done)
				if reward>1:
					agent.append_sample(state, action, reward, next_state, done)

			print('[{}] state:{} action:{} next_state:{} reward:{} fps:{}, avg_q={}'.format(t, state,action,next_state,reward,fps,agent.avg_q_max))
			if len(agent.memory) >= agent.train_start:
				agent.train_model()
#				print(agent.get_flops(agent.model)) 
			score += reward
			avg_reward.append(sum(reward_tmp) / len(reward_tmp))
			#print('q:{}'.format(agent.q_table[next_state]))
			# get action
			state=next_state


			if c_t>=target_temp:
				c_c=int(3*random.randint(0,int(c_c/3))+2)
				g_c=int(random.randint(1,g_c))

				action=3*int(c_c/3)+int(g_c)-1
			elif target_temp-c_t>=3:
				if fps<target_fps:
					if np.random.rand() <= 0.3:
						print('previous clock : {} {}'.format(c_c,g_c))
						c_c=int(3*random.randint(int(c_c/3),2)+2)
						g_c=int(random.randint(g_c,3))

						print('explore higher clock@@@@@  {} {}'.format(c_c,g_c))
						action=3*int(c_c/3)+int(g_c)-1
					else:
						action=agent.get_action(state)
						c_c=agent.clk_action_list[action][0]
						g_c=agent.clk_action_list[action][1]
				else:
					action=agent.get_action(state)
					c_c=agent.clk_action_list[action][0]
					g_c=agent.clk_action_list[action][1]



			else:
				action=agent.get_action(state)
				c_c=agent.clk_action_list[action][0]
				g_c=agent.clk_action_list[action][1]	


				# do action(one step)
			send_msg=str(c_c)+','+str(g_c)
			client_socket.send(send_msg.encode())
			ax1.plot(ts, fps_data, linewidth=1, color='pink')
			ax1.axhline(y=target_fps, xmin=0, xmax=2000)
			ax1.set_title('Frame rate (Target fps = 60) ')
			ax1.set_ylabel('Frame rate (fps)')
			ax1.set_xlabel('Time (s) ')
			ax1.set_xticks([0, 500, 1000, 1500, 2000])
			ax1.set_yticks([15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65])
			ax1.grid(True)

			ax2.plot(ts, power_data, linewidth=1, color='blue')
			ax2.set_title('Power consumption')
			ax2.set_ylabel('Power (mW)')
			ax2.set_yticks([0, 2000, 4000, 6000, 8000])
			ax2.set_xticks([0, 250, 500, 750, 1000])
			ax2.set_xlabel('Time (s) ')
			ax2.grid(True)
			
			ax3.plot(ts, avg_q_max_data, linewidth=1, color='orange')
			ax3.set_ylabel('Q-value')
			ax3.set_xticks([0, 500, 1000, 1500, 2000])
			ax3.set_xlabel('Time (s) ')
			ax3.grid(True)
			
			ax4.plot(ts, loss_data, linewidth=1, color='black')
			ax4.set_ylabel('Average loss')
			ax2.set_yticks([0, 2000, 4000, 6000, 8000])
			ax4.set_xticks([0, 500, 1000, 1500, 2000])
			ax4.set_xlabel('Time (s) ')
			ax4.grid(True)
			
			plt.pause(0.1)


			if done:
				agent.update_target_model()
			t=t+1
			if t%60 == 0:
				agent.learning_rate=0.1
				print('[Reset learning_rate]')
			if t%500 == 0:
				agent.model.save_weights("./save_model/model.h5")
				print("[Save model]")
			if t==experiment_time:
				break

	finally:
		server_socket.close()
	print(reward_tmp)
	ts = range(0, len(avg_q_max_data))
	plt.figure(1)
	plt.xlabel('time')
	plt.ylabel('Avg Q-max')
	plt.grid(True)
	plt.plot(ts,avg_q_max_data, label='avg_q_max')
	plt.legend(loc='upper left')
	plt.title('Average max-Q')
	plt.show()

	




