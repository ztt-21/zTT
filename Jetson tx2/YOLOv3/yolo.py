#!/usr/bin/env python3

import os
from threading import Thread
import time
import numpy as np
import random
import mmap
import struct
from inotify_simple import INotify, flags


#import matplotlib.pyplot as plt

cpu_clock_list = [345600,499200,652800,806400,960000,1113600,1267200,1420800,1574400,1728000,1881600,2035200]
gpu_clock_list=[114750000,216750000,318750000,420750000,522750000,624750000,726750000,828750000,930750000,1032750000,1134750000,1236750000,1300500000]
fan_speed_list=[0,40,80,120,160,255]
dir_thermal='/sys/devices/virtual/thermal'
dir_power='/sys/bus/i2c/drivers/ina3221x'
dir_power1='/sys/kernel/debug/bpmp/debug/regulator'
DEFAULT_PROTOCOL = 0
PORT = 8702
experiment_time=800
clock_change_time=30
cpu_power_limit=1000
gpu_power_limit=1600
action_space=9
target_fps=15
target_temp=60
beta=6
fan_speed=0
#config = tf.ConfigProto()
#config.gpu_options.allow_growth=True
#sess = tf.Session(config=config)
#K.set_session(sess)


class PowerLogger:
	def __init__(self, interval=0.01,type=0):
		self.interval=interval
		self._startTime=-1
		self.eventLog=[0]
		self.dataLog=[0]
		self.dataLog1=[0]
		self.dataLog2=[0]
		self.dataLog3=[0]
		self.dataLog4=[0]
		self.power=0
		self.voltage=0
		self.current=0
		self.maxvoltage=0
		self.minvoltage=0
		self.type=type
	def _getTime(self):
		return time.clock_gettime(time.CLOCK_REALTIME)

	def getCPUpower(self):
		fname='{}/0-0041/iio_device/in_power1_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			line.replace('\n','')
			f.close()
			return line
	def getCPUvoltage(self):
		fname='{}/0-0041/iio_device/in_voltage1_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			line.replace('\n','')
			f.close()
			return line
	def getCPUvoltage1(self):
		fname='{}/vdd_cpu/voltage'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return int(line)/1000

	def getCPUmaxvoltage(self):
		fname='{}/vdd_cpu/max_uv'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return int(line)/1000

	def getCPUminvoltage(self):
		fname='{}/vdd_gpu/min_uv'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			return int(line)/1000



	def getCPUcurrent(self):
		fname='{}/0-0041/iio_device/in_current1_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			line.replace('\n','')
			f.close()
			return line


	def getGPUpower(self):
		fname='{}/0-0040/iio_device/in_power0_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return line
	def getGPUvoltage(self):
		fname='{}/0-0040/iio_device/in_voltage0_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return line
	def getGPUvoltage1(self):
		fname='{}/vdd_gpu/voltage'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return int(line)/1000
	def getGPUmaxvoltage(self):
		fname='{}/vdd_gpu/max_uv'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return int(line)/1000

	def getGPUminvoltage(self):
		fname='{}/vdd_gpu/min_uv'.format(dir_power1)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			return int(line)/1000
	def getGPUcurrent(self):
		fname='{}/0-0040/iio_device/in_current0_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return line

	def getSYSTEMpower(self):
		fname='{}/0-0041/iio_device/in_power0_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			line.replace('\n','')
			f.close()
			return line

	def getDDRpower(self):
		fname='{}/0-0041/iio_device/in_power2_input'.format(dir_power)
		with open(fname,'r') as f:
			line=f.readline()
			line.replace('\n','')
			f.close()
			return line

	def threadFun(self):
#			self.start()
		self._startTime=self._getTime()
		while(1):
			t=self._getTime()-self._startTime
			if(self.type==0):
				self.dataLog.append(int(self.getCPUpower()))
				self.dataLog1.append(int(self.getCPUvoltage1()))
				self.dataLog2.append(int(self.getCPUcurrent()))
				self.dataLog3.append(int(self.getCPUmaxvoltage()))
				self.dataLog4.append(int(self.getCPUminvoltage()))
			if(self.type==1):
				self.dataLog.append(int(self.getGPUpower()))
				self.dataLog1.append(int(self.getGPUvoltage1()))
				self.dataLog2.append(int(self.getGPUcurrent()))
				self.dataLog3.append(int(self.getGPUmaxvoltage()))
				self.dataLog4.append(int(self.getGPUminvoltage()))
			if(self.type==2):
				self.dataLog.append(int(self.getSYSTEMpower()))
				if(t>0.3):
					if(len(self.dataLog)>1):
						self.power=sum(self.dataLog)/len(self.dataLog)
						self._startTime=self._getTime()
						self.dataLog=[]
			if(self.type==3):
				self.dataLog.append(int(self.getDDRpower()))
				if(t>0.3):
					if(len(self.dataLog)>1):
						self.power=sum(self.dataLog)/len(self.dataLog)
						self._startTime=self._getTime()
						self.dataLog=[]
			if(t>0.3):
				if(len(self.dataLog)*len(self.dataLog1)*len(self.dataLog2)*len(self.dataLog3)*len(self.dataLog4)>1):
					self.power=sum(self.dataLog)/len(self.dataLog)
					self.voltage=sum(self.dataLog1)/len(self.dataLog1)
					self.current=sum(self.dataLog2)/len(self.dataLog2)
					self.maxvoltage=sum(self.dataLog3)/len(self.dataLog3)
					self.minvoltage=sum(self.dataLog4)/len(self.dataLog4)
					self._startTime=self._getTime()
	#				if(self.type==0):
	#					print(self.dataLog)
					self.dataLog=[self.power]
					self.dataLog1=[self.voltage]
					self.dataLog2=[self.current]
					self.dataLog3=[self.maxvoltage]
					self.dataLog4=[self.minvoltage]
					self._startTime=self._getTime()
					t=0
#			break

#		self._tmr=threading.Timer(self.interval, threadFun)
#		self._tmr.start()
			if self._startTime <0:
				self._startTime=self._getTime()
	def start(self):
		t=Thread(target=self.threadFun)
		t.start()

	def getValue(self):
		return self.power
	def getValue1(self):
		return self.voltage
	def getValue2(self):
		return self.current
	def getValue3(self):
		return self.maxvoltage
	def getValue4(self):
		return self.minvoltage
#	def stop(self):






def currentCPUstatus():
	fname='/sys/devices/system/cpu/online'
	with open(fname,'r') as f:
		line=f.readline()
		print(line)
		f.close()

def setUserspace():
	for i in range(0,6):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
		with open(fname,'w') as f:
			f.write('userspace')
			print('[cpu{}]Set userspace '.format(i),end="")
			f.close()
	fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/governor'
	with open(fname,'w') as f:
		f.write('userspace')
		print('[gpu]Set userspace')
	fname='/sys/kernel/debug/tegra_fan/temp_control'
	with open(fname,'w') as f:
		f.write('1')
		print('[FAN] control on')

def setdefault(mode):
	for i in range(0,6):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
		with open(fname,'w') as f:
			f.write(mode)
			print('[cpu{}]Set {}'.format(i,mode),end="")
			f.close()
	fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/governor'
	with open(fname,'w') as f:
		f.write('userspace')
		print('[gpu]Set nvhost_podgov')
	

def getAvailableClock():
	for i in range(0,6):
                fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_available_frequencies' %(i)
                with open(fname,'r') as f:
                        line=f.readline()
                        print(line)

def getCurrentClock():
	for i in range(0,6):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %(i)
		with open(fname,'r') as f:
			line=f.readline()
			line=line.replace('\n','')
			print('[cpu{}]{}KHz '.format(i,line),end=""),
			f.close()
	fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/cur_freq'
	with open(fname,'r') as f:
		line=f.readline()
		line=line.replace('\n','')
		print('[gpu]{}Hz'.format(line))
		f.close()

class CPU:
	def __init__(self,idx):
		self.idx=idx
		self.clk=11
		self.clock_data=[]
		self.power_data=[]
		self.voltage_data=[]
		self.current_data=[]
		self.temp_data=[]
		self.maxvoltage_data=[]
		self.minvoltage_data=[]

		self.power_limit_data=[]
		self.power_limit=cpu_power_limit
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_max_freq' %(self.idx)
		with open(fname,'w') as f:
			f.write('{}'.format(cpu_clock_list[11]))
			f.close()
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %(self.idx)
		with open(fname,'w') as f:
			f.write('{}'.format(cpu_clock_list[0]))
			f.close()
		self.pl=PowerLogger(interval=0.3,type=0)
		self.pl.start()
	def setCPUclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_setspeed' %(self.idx)
		f=open(fname,'w')
		f.write('{}'.format(cpu_clock_list[i]))
		#print('[cpu{}] Set clock {}'.format(self.idx,cpu_clock_list[i]))
		f.close()
	def getCPUtemp(self):
		if (self.idx==0):
			fname='{}/thermal_zone0/temp'.format(dir_thermal)
			f=open(fname,'r')
			line=f.readline()
			line.replace('\n','')
		#	print('[cpu{}] temp:{}'.format(self.idx,line),end="")
			f.close()
			return float(line)/1000
		else:
			fname='{}/thermal_zone1/temp'.format(dir_thermal)
			f=open(fname,'r')
			line=f.readline()
			line.replace('\n','')
		#	print('[cpu{}] temp:{}'.format(self.idx,line),end="")
			f.close()
			return float(line)/1000
	def getCPUpower(self):
		return self.pl.getValue()
	def getCPUvoltage(self):
		return self.pl.getValue1()
	def getCPUcurrent(self):
		return self.pl.getValue2()
	def getCPUmaxvoltage(self):
		return self.pl.getValue3()
	def getCPUminvoltage(self):
		return self.pl.getValue4()

	def getCPUclock(self, idx):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %idx
		with open(fname,'r') as f:
			line=f.readline()
			line=line.replace('\n','')
                        #print('[cpu{}]{}KHz '.format(i,line),end=""),
			f.close()
			return int(line)/1000

	def collectdata(self):
		self.clock_data.append(self.getCPUclock(self.idx))
		self.temp_data.append(self.getCPUtemp())
		self.power_data.append(self.getCPUpower())
		self.voltage_data.append(self.getCPUvoltage())
		self.current_data.append(self.getCPUcurrent())
		self.maxvoltage_data.append(self.getCPUmaxvoltage())
		self.minvoltage_data.append(self.getCPUminvoltage())

#		self.power_limit_data.append(self.power_limit)

#	def do_limit_power(self,ts):
#		average_power=0
#		if (ts<10):
#			print('need more data')
#		else:
#			for i in range(2):
#				average_power = average_power + self.power_data[ts-i]
#			average_power = average_power/2
#		if (average_power > self.power_limit):
#			return 1
#		else:
#			return 0


class GPU:
	def __init__(self):
		self.clk=12
		self.clock_data=[]
		self.temp_data=[]
		self.power_data=[]
		self.voltage_data=[]
		self.current_data=[]
		self.maxvoltage_data=[]
		self.minvoltage_data=[]
		self.power_limit_data=[]
		self.power_limit=gpu_power_limit
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/max_freq'
		with open(fname,'w') as f:
			f.write('{}'.format(gpu_clock_list[12]))
			f.close()
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/min_freq'
		with open(fname,'w') as f:
			f.write('{}'.format(gpu_clock_list[0]))
			f.close()
		self.pl=PowerLogger(interval=0.3,type=1)
		self.pl.start()
	def setGPUclock(self,i):
		self.clk=i
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/userspace/set_freq'
		f=open(fname,'w')
		f.write('{}'.format(gpu_clock_list[i]))
		#print('[gpu] Set clock {}'.format(gpu_clock_list[i]))
		f.close()
	def getGPUtemp(self):
		fname='{}/thermal_zone2/temp'.format(dir_thermal)
		f=open(fname,'r')
		line=f.readline()
		line.replace('\n','')
		#print('[gpu] temp:{}'.format(line),end="")
		f.close()
		return float(line)/1000

	def getGPUpower(self):
			return self.pl.getValue()
	def getGPUvoltage(self):
			return self.pl.getValue1()
	def getGPUcurrent(self):
			return self.pl.getValue2()
	def getGPUmaxvoltage(self):
			return self.pl.getValue3()
	def getGPUminvoltage(self):
			return self.pl.getValue4()
	def getGPUclock(self):
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/cur_freq'
		with open(fname,'r') as f:
			line=f.readline()
			f.close()
			return int(line)/1000000

	def collectdata(self):
		self.clock_data.append(self.getGPUclock())
		self.temp_data.append(self.getGPUtemp())
		self.power_data.append(self.getGPUpower())
		self.voltage_data.append(self.getGPUvoltage())
		self.current_data.append(self.getGPUcurrent())
		self.maxvoltage_data.append(self.getGPUmaxvoltage())
		self.minvoltage_data.append(self.getGPUminvoltage())
#		self.power_limit_data.append(self.power_limit)

#	def do_limit_power(self,ts):
#		average_power=0
#		if (ts<10):
#			print('need more data')
#		else:
#			for i in range(2):
#				average_power = average_power + self.power_data[ts-i]
#			average_power = average_power/2
#		if (average_power > self.power_limit):
#			return 1
#		else:
#			return 0

		#print(self.clock_data)
class SYSTEM:
	def __init__(self):
		self.power_data=[]
		self.pl=PowerLogger(interval=0.3,type=2)
		self.pl.start()

	def getSYSTEMpower(self):
		return self.pl.getValue()
	def collectdata(self):
		self.power_data.append(self.getSYSTEMpower())

class DDR:
	def __init__(self):
		self.power_data=[]
		self.pl=PowerLogger(interval=0.3,type=3)
		self.pl.start()
	def getDDRpower(self):
		return self.pl.getValue()
	def collectdata(self):
		self.power_data.append(self.getDDRpower())


class FAN:
	def setFANspeed(self,i):
		fname='/sys/kernel/debug/tegra_fan/target_pwm'
		f=open(fname,'w')
		f.write('{}'.format(fan_speed_list[i]))
		print('[Fan] Set speed {}'.format(fan_speed_list[i]))
		f.close()
	def getFANspeed(self):
		fname='/sys/kernel/debug/tegra_fan/cur_pwm'
		with open(fname,'r') as f:
			line=f.readline()
			line=line.replace('\n','')
			f.close()
			return int(line)
		
import time
import cv2
import socket
import matplotlib.pyplot as plt
import numpy as np
import csv
import struct
import math
from time import sleep
def get_reward(fps, power, target_fps, beta):
#	u=max(1,fps/target_fps) 
	if fps>=target_fps:
		u=1
	else :
		u=math.exp(2*(fps-target_fps))
	return u+beta/power
	
if __name__=="__main__":
	setUserspace()
#	setdefault('userspace')
	getCurrentClock()


	c0=CPU(0)
	c1=CPU(1)
	g=GPU()
	fan=FAN()
	sys=SYSTEM()
	ddr=DDR()
	getCurrentClock()
#	agent = DQNAgent(4,9)
#	scores, episodes = [], []

	c0.setCPUclock(11)
	c1.setCPUclock(11)
	g.setGPUclock(11)
#	fan.setFANspeed(fan_speed)
	t=0
	fps=0
	ts=[]
	fps_data=[]
	viofps_data=[]
	avg_q_max_data=[]
	fan_data=[]
#	learning_fps_data=[]
	cnt=0
#	str=''
	c_c=11
	g_c=11
	c_t=float(c0.getCPUtemp())
	g_t=float(g.getGPUtemp())
	state=(c_c,g_c,int(c0.getCPUpower()/100),int(g.getGPUpower()/100), c_t, g_t) #, float(c0.getCPUcurrent()/10), float(g.getGPUcurrent()/10))
	score=0
	action=0

	clk=11
#	file='/home/nvidia/usb/Samsung 4K Demo 2013 (23+ minutes).mp4'
#	file='/home/nvidia/usb/Peru 8K HDR 60FPS (FUHD).mp4'
#	file='/home/nvidia/yolov3/traffic.mp4'

#	capture=cv2.VideoCapture(file)
#	capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
#	capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 90)

	prevTime=0
	curTime=0
	cnt=0
	u=0
#	flag=0
	print('Ready for connection')
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(("192.168.1.7",8702))
	print('connected!')
	mmap_file_name = "/tmp/ipc_fps.txt"
	inotify = INotify()
	wd = inotify.add_watch(mmap_file_name, flags.MODIFY)
	while(1):
		fd = os.open(mmap_file_name, os.O_RDONLY)
		buf = mmap.mmap(fd, os.path.getsize(mmap_file_name), 
		mmap.MAP_SHARED, mmap.PROT_READ)
		line = buf.readline()
		if inotify.read()[0].mask == flags.MODIFY:
			if len(line) == 8:
				fps = float(struct.unpack('d', line)[0])
	
				str_msg="FPS: %0.1f" % fps

				fps_data.append(fps)
				fan_data.append(fan.getFANspeed())
				if fps<target_fps:
					u=u+1
				viofps_data.append(u/(t+1))
				ts.append(t)
		
				c0.collectdata()
				c1.collectdata()
				g.collectdata()
				sys.collectdata()
				ddr.collectdata()
				c_p=int(c0.getCPUpower()/100)
	#			c_i=float(c0.getCPUcurrent()/10)
				g_p=int(g.getGPUpower()/100)
	#			g_i=float(g.getGPUcurrent()/10)
				c_t=float(c0.getCPUtemp())
				g_t=float(g.getGPUtemp())
				next_state=(c_c, g_c, c_p, g_p, c_t, g_t) #, c_i, g_i)
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
				c1.setCPUclock(c_c)
				g.setGPUclock(g_c)
				sleep(2)
				t=t+1
		if t==experiment_time:
			break


	c0.setCPUclock(11)
	c1.setCPUclock(11)
	g.setGPUclock(12)
	fan.setFANspeed(5)
	if len(ts)>0:
		print('Average Total power={} mW'.format(sum(sys.power_data)/len(sys.power_data)))
		print('Average CPU power={} mW'.format(sum(c0.power_data)/len(c0.power_data)))
		print('Average GPU power={} mW'.format(sum(g.power_data)/len(g.power_data)))
		print('Average DDR power={} mW'.format(sum(ddr.power_data)/len(ddr.power_data)))
#		print('Average max-Q = {}'.format(sum(avg_q_max_data)/len(avg_q_max_data)))
		print('Average fps = {} fps'.format(sum(fps_data)/len(fps_data)))

	if len(ts)>100:
		ts = range(0, len(fps_data))
		f=open('power_yolo15.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		wr.writerow(c0.power_data)
		wr.writerow(g.power_data)
		wr.writerow(sys.power_data)
		f.close()

		f=open('temp_yolo15.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		wr.writerow(c0.temp_data)
		wr.writerow(c1.temp_data)
		wr.writerow(g.temp_data)
		f.close()

		f=open('clock_yolo15.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
		wr.writerow(c0.clock_data)
		wr.writerow(c1.clock_data)
		wr.writerow(g.clock_data)
		f.close()

		f=open('fps_yolo15.csv','w',encoding='utf-8',newline='')
		wr=csv.writer(f)
	#		wr.writerow(learning_fps_data)
		wr.writerow(fps_data)
		f.close()

		plt.figure(1)
		plt.xlabel('time')
		plt.ylabel('power(mw)')
		plt.grid(True)
		plt.plot(ts,c0.power_data,label='CPU')
		plt.plot(ts,g.power_data,label='GPU')
		plt.plot(ts,sys.power_data,label='TOTAL')
		plt.plot(ts,ddr.power_data,label='DDR')
	#		plt.plot(ts,g.power_limit_data,label='GPU power limit',linestyle=':',color='deepskyblue')
	#		plt.plot(ts,c0.power_limit_data,label='CPU power limit',linestyle=':',color='blue')

		plt.legend(loc='upper right')
		plt.title('Power')



		plt.figure(2)
		plt.xlabel('time')
		plt.ylabel('temperature')
		plt.grid(True)
		plt.plot(ts,c0.temp_data,label='CPU0')
		plt.plot(ts,c1.temp_data,label='CPU1')
		plt.plot(ts,g.temp_data,label='GPU')
		plt.axhline(y=target_temp, color='r', linewidth=1)
		plt.legend(loc='upper right')
		plt.title('temperature')

		plt.figure(3)
		plt.xlabel('time')
		plt.ylabel('clock frequency(MHz)')
		plt.grid(True)
		plt.plot(ts,c0.clock_data,label='CPU0')
		plt.plot(ts,c1.clock_data,label='CPU1')
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
		plt.figure(5)
		plt.xlabel('time')
		plt.ylabel('FAN speed')
		plt.grid(True)
		plt.plot(ts,fan_data,label='FAN speed')
		plt.legend(loc='upper right')
		plt.title('FAN speed')


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



