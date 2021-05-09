#!/usr/bin/env python3

#import os
from threading import Thread
import time
#import numpy as np
#import random

dir_power='/sys/bus/i2c/drivers/ina3221x'
dir_power1='/sys/kernel/debug/bpmp/debug/regulator'
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
#			print('[cpu{}]Set userspace '.format(i),end="")
			print('[cpu{}]Set userspace '.format(i))
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
#			print('[cpu{}]Set {}'.format(i,mode),end="")
			f.close()
	fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/governor'
	with open(fname,'w') as f:
#		f.write('simple_ondemand')
		f.write('nvhost_podgov')
		print('[gpu] simple_ondemand')
	

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
#			print('[cpu{}]{}KHz '.format(i,line),end=""),
			f.close()
	fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/cur_freq'
	with open(fname,'r') as f:
		line=f.readline()
		line=line.replace('\n','')
		print('[gpu]{}Hz'.format(line))
		f.close()




