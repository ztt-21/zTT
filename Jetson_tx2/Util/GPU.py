#!/usr/bin/env python3

from Util import PowerLogger
gpu_clock_list=[114750000,216750000,318750000,420750000,522750000,624750000,726750000,828750000,930750000,1032750000,1134750000,1236750000,1300500000]
dir_thermal='/sys/devices/virtual/thermal'
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

		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/max_freq'
		with open(fname,'w') as f:
			f.write('{}'.format(gpu_clock_list[12]))
			f.close()
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/min_freq'
		with open(fname,'w') as f:
			f.write('{}'.format(gpu_clock_list[0]))
			f.close()
		self.pl=PowerLogger.PowerLogger(interval=0.3,type=1)
		self.pl.start()
	def setGPUclock(self,i):
		self.clk=i
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/userspace/set_freq'
#		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/target_freq'
		f=open(fname,'w')
		f.write('{}'.format(gpu_clock_list[i]))
		print('[gpu] Set clock {}'.format(gpu_clock_list[i]))
		f.close()

	def setGPUminclock(self,i):
		self.clk=i
		if (i<140250000):
			i=140250000
		if (i>1300500000):
			i=1300500000
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/min_freq'
		f=open(fname,'w')
		f.write('{}'.format(i))
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

	def getGPUminclock(self):
		fname='/sys/devices/gpu.0/devfreq/17000000.gp10b/min_freq'
		with open(fname,'r') as f:
			line=f.readline()
			f.close()
			return int(line)

	def collectdata(self):
		self.clock_data.append(self.getGPUclock())
		self.temp_data.append(self.getGPUtemp())
		self.power_data.append(self.getGPUpower())
		self.voltage_data.append(self.getGPUvoltage())
		self.current_data.append(self.getGPUcurrent())
		self.maxvoltage_data.append(self.getGPUmaxvoltage())
		self.minvoltage_data.append(self.getGPUminvoltage())




