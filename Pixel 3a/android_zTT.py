#!/usr/bin/env python3

import os
from threading import Thread
import time
import numpy as np
import random
import subprocess
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
from SurfaceFlinger.get_fps import SurfaceFlingerFPS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


little_cpu_clock_list = [300000, 576000, 748800, 998400, 1209600, 1324800, 1516800, 1612800, 1708800]
big_cpu_clock_list = [300000, 652800, 825600, 979200, 1132800, 1363200, 1536000, 1747200, 1843200, 1996800]
gpu_clock_list=[180000000, 267000000, 355000000, 430000000]
dir_thermal='/sys/devices/virtual/thermal'
DEFAULT_PROTOCOL = 0
PORT = 8702
experiment_time=300

class PowerLogger:
	def __init__(self):
		self.power=0
		self.voltage=0
		self.current=0
		self.power_data = []
		self.voltage_data = []
		self.current_data = []
		self.Mon = HVPM.Monsoon()
		self.Mon.setup_usb()
		self.engine = sampleEngine.SampleEngine(self.Mon)
		self.engine.disableCSVOutput()
		self.engine.ConsoleOutput(False)

	def _getTime(self):
		return time.clock_gettime(time.CLOCK_REALTIME)

	def getPower(self):
		self.engine.enableChannel(sampleEngine.channels.MainCurrent)
		self.engine.enableChannel(sampleEngine.channels.MainVoltage)
		self.engine.startSampling(1)
		sample = self.engine.getSamples()
		current = sample[sampleEngine.channels.MainCurrent][0]
		voltage = sample[sampleEngine.channels.MainVoltage][0]
		self.Mon.stopSampling()
		self.engine.disableChannel(sampleEngine.channels.MainCurrent)
		self.engine.disableChannel(sampleEngine.channels.MainVoltage)
		self.power = current * voltage
		self.power_data.append(self.power)
		#print(self.power)
		return current * voltage

	def getVoltage(self):
		self.engine.startSampling(1)
		sample = self.engine.getSamples()
		voltage = sample[sampleEngine.channels.MainVoltage][0]
		self.Mon.stopSampling()
		self.voltage = voltage
		self.voltage_data.append(self.voltage)
		return voltage

	def getCurrent(self):
		self.engine.startSampling(1)
		sample = self.engine.getSamples()
		current = sample[sampleEngine.channels.MainCurrent][0]
		self.Mon.stopSampling()
		self.current = current
		self.current_data.append(self.current)
		return current

def currentCPUstatus():
	fname='/sys/devices/system/cpu/online'
	with open(fname,'r') as f:
		line=f.readline()
		print(line)
		f.close()

def setUserspace():
	for i in range(0,8):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo userspace >', fname+"\""])
		print('[cpu{}]Set userspace '.format(i),end="")

	fname='/sys/class/kgsl/kgsl-3d0/devfreq/governor'
	subprocess.check_output(['adb', 'shell', 'su -c', '\"echo userspace >', fname+"\""])
	print('[gpu]Set userspace')
	

def setdefault(mode):
	for i in range(0,8):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo '+mode+' >', fname+"\""])
		print('[cpu{}]Set {}'.format(i,mode),end="")
	
	fname='/sys/class/kgsl/kgsl-3d0/devfreq/governor'
	subprocess.check_output(['adb', 'shell', 'su -c', '\"echo msm-adreno-tz >', fname+"\""])
	print('[gpu]Set msm-adreno-tz')
	

def getAvailableClock():
	for i in range(0,8):
                fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_available_frequencies' %(i)
                output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
                output = output.decode('utf-8')
                output = output.strip()

def getCurrentClock():
	for i in range(0,8):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %(i)
		output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		print('[cpu{}]{}KHz '.format(i,output),end=""),
			
	fname='/sys/class/kgsl/kgsl-3d0/devfreq/cur_freq'
	output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
	output = output.decode('utf-8')
	output = output.strip()
	print('[gpu]{}Hz'.format(output))

class CPU:
	def __init__(self,idx,cpu_type):
		self.idx=idx
		self.cpu_type = cpu_type
		self.clock_data=[]
		self.temp_data=[]

		if self.cpu_type == 'b':
			self.max_freq = 9
			self.clk = 9
			self.cpu_clock_list = big_cpu_clock_list
		elif self.cpu_type == 'l':
			self.max_freq = 8
			self.clk = 8
			self.cpu_clock_list = little_cpu_clock_list
		

		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_max_freq' %(self.idx)
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[self.max_freq])+" >", fname+"\""])
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %(self.idx)
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[0])+" >", fname+"\""])		
		
	def setCPUclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_setspeed' %(self.idx)
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[i])+" >", fname+"\""])
		
	def getCPUtemp(self):
		fname='{}/thermal_zone10/temp'.format(dir_thermal)
		output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000

	def getCPUclock(self, idx):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %idx
		output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000

	def collectdata(self):
		self.clock_data.append(self.getCPUclock(self.idx))
		self.temp_data.append(self.getCPUtemp())


class GPU:
	def __init__(self):
		self.clk=3
		self.clock_data=[]
		self.temp_data=[]

		fname='/sys/class/kgsl/kgsl-3d0/devfreq/max_freq'
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(gpu_clock_list[3])+" >", fname+"\""])
		fname='/sys/class/kgsl/kgsl-3d0/devfreq/min_freq'
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(gpu_clock_list[0])+" >", fname+"\""])
		
	def setGPUclock(self,i):
		self.clk=i
		fname='/sys/class/kgsl/kgsl-3d0/devfreq/userspace/set_freq'
		subprocess.check_output(['adb', 'shell', 'su -c', '\"echo', str(gpu_clock_list[i])+" >", fname+"\""])
		
	def getGPUtemp(self):
		fname='{}/thermal_zone10/temp'.format(dir_thermal)
		output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000

	def getGPUclock(self):
		fname='/sys/class/kgsl/kgsl-3d0/devfreq/cur_freq'
		output = subprocess.check_output(['adb', 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000000

	def collectdata(self):
		self.clock_data.append(self.getGPUclock())
		self.temp_data.append(self.getGPUtemp())
		
import time
import cv2
import socket
import matplotlib.pyplot as plt
import numpy as np
import csv
import struct
import math
from time import sleep
	
if __name__=="__main__":

	
	setUserspace()
	getCurrentClock()

	c0=CPU(0, cpu_type='l')
	c6=CPU(6, cpu_type='b')

	pl=PowerLogger()

	g=GPU()	
	getCurrentClock()

	c0.setCPUclock(8)
	c6.setCPUclock(8)
	g.setGPUclock(3)
	
	t=0
	fps=0
	ts=[]
	fps_data=[]
	
	
	c_c=8
	g_c=3
	c_t=float(c0.getCPUtemp())
	g_t=float(g.getGPUtemp())
	state=(c_c,g_c,int(pl.getPower()/100),0, c_t, g_t)
	sleep(4)

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(("192.168.1.86",8702))

	#view = "\"SurfaceView - com.tencent.tmgp.kr.codm/com.tencent.tmgp.cod.CODMainActivity#0\""
	view = "\"com.skype.raider/com.skype4life.MainActivity#0\""
	#view = "\"SurfaceView - com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity#0\""
	#view = "\"SurfaceView - com.android.chrome/com.google.android.apps.chrome.Main#0\""
	sf_fps_driver = SurfaceFlingerFPS(view)
	
	while(1):
		fps = float(sf_fps_driver.getFPS())
		if fps > 60:
			fps = 60.0
		fps_data.append(fps)
		
		ts.append(t)

		c0.collectdata()
		c6.collectdata()
		g.collectdata()
		
		c_p=int(pl.getPower()/100)
		if c_p == 0:
			continue
		g_p=0
		sleep(3.5)
		
		c_t=float(c0.getCPUtemp())
		g_t=float(g.getGPUtemp())
		next_state=(c_c, g_c, c_p, g_p, c_t, g_t)
		
		send_msg=str(c_c)+','+str(g_c)+','+str(c_p)+','+str(g_p)+','+str(c_t)+','+str(g_t)+','+str(fps)
		client_socket.send(send_msg.encode())
		print('[{}] state:{} next_state:{} fps:{}'.format(t, state,next_state,fps))
		state=next_state
		# get action
		recv_msg=client_socket.recv(8702).decode()
		clk=recv_msg.split(',')

		c_c=int(clk[0])
		g_c=int(clk[1])

		c0.setCPUclock(c_c)
		c6.setCPUclock(c_c)
		g.setGPUclock(g_c)
		#sleep(1)
		t=t+1
		if t==experiment_time:
			break


	#c0.setCPUclock(8)
	#c6.setCPUclock(8)
	#g.setGPUclock(3)
	#fan.setFANspeed(5)
	if len(ts)>0:
		print('Average Total power={} mW'.format(sum(pl.power_data)/len(pl.power_data)))
		#print('Average CPU power={} mW'.format(sum(c0.power_data)/len(c0.power_data)))
		#print('Average GPU power={} mW'.format(sum(g.power_data)/len(g.power_data)))
		#print('Average DDR power={} mW'.format(sum(ddr.power_data)/len(ddr.power_data)))
#		print('Average max-Q = {}'.format(sum(avg_q_max_data)/len(avg_q_max_data)))
		print('Average fps = {} fps'.format(sum(fps_data)/len(fps_data)))

	if len(ts)>100:
		ts = range(0, len(fps_data))
		f=open('power_skype_zTT.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		#wr.writerow(c0.power_data)
		#wr.writerow(g.power_data)
		wr.writerow(pl.power_data)
		f.close()

		f=open('temp_skype_zTT.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		wr.writerow(c0.temp_data)
		wr.writerow(c6.temp_data)
		wr.writerow(g.temp_data)
		f.close()

		f=open('clock_skype_zTT.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		wr.writerow(c0.clock_data)
		wr.writerow(c6.clock_data)
		wr.writerow(g.clock_data)
		f.close()

		f=open('fps_skype_zTT.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
	#		wr.writerow(learning_fps_data)
		wr.writerow(fps_data)
		f.close()

		plt.figure(1)
		plt.xlabel('time')
		plt.ylabel('power(mw)')
		plt.grid(True)
		#plt.plot(ts,c0.power_data,label='CPU')
		#plt.plot(ts,g.power_data,label='GPU')
		plt.plot(ts,pl.power_data[1:-1],label='TOTAL')
		#plt.plot(ts,ddr.power_data,label='DDR')
	#		plt.plot(ts,g.power_limit_data,label='GPU power limit',linestyle=':',color='deepskyblue')
	#		plt.plot(ts,c0.power_limit_data,label='CPU power limit',linestyle=':',color='blue')

		plt.legend(loc='upper right')
		plt.title('Power')



		plt.figure(2)
		plt.xlabel('time')
		plt.ylabel('temperature')
		plt.grid(True)
		plt.plot(ts,c0.temp_data,label='LITTLE')
		plt.plot(ts,c6.temp_data,label='Big')
		plt.plot(ts,g.temp_data,label='GPU')
		plt.axhline(y=target_temp, color='r', linewidth=1)
		plt.legend(loc='upper right')
		plt.title('temperature')

		plt.figure(3)
		plt.xlabel('time')
		plt.ylabel('clock frequency(MHz)')
		plt.grid(True)
		plt.plot(ts,c0.clock_data,label='LITTLE')
		plt.plot(ts,c6.clock_data,label='Big')
		plt.plot(ts,g.clock_data,label='GPU')
		plt.legend(loc='upper right')
		plt.title('clock')

		plt.figure(4)
		plt.xlabel('time')
		plt.ylabel('FPS')
		plt.grid(True)
	#	plt.plot(ts,learning_fps_data,label='Learning FPS')
		plt.plot(ts,fps_data,label='Average FPS')
		plt.axhline(y=target_fps, color='r', linewidth=1)
		plt.legend(loc='upper right')
		plt.title('fps')
	#		print('Average learning fps={} fps'.format(sum(learning_fps_data)/len(ts)))
		#plt.figure(5)
		#plt.xlabel('time')
		#plt.ylabel('FAN speed')
		#plt.grid(True)
		#plt.plot(ts,fan_data,label='FAN speed')
		#plt.legend(loc='upper right')
		#plt.title('FAN speed')


#		plt.figure(6)
#		plt.xlabel('time')
#		plt.ylabel('FPS violation probability')
#		plt.grid(True)
#		plt.plot(ts,viofps_data,label='violation probability')
#		plt.legend(loc='upper right')
#		plt.title('FPS violation probability')

	#		print('Av

#		plt.figure(5)
#		plt.xlabel('time')
#		plt.ylabel('Average max-Q')
#		plt.grid(True)
#		plt.plot(ts,avg_q_max_data, label='avg_q_max')
#		plt.legend(loc='upper left')
#		plt.title('Average max-Q')
		plt.show()



