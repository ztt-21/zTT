#!/usr/bin/env python3

from Util import PowerLogger
fan_speed_list=[0,40,80,120,160,255]
class SYSTEM:
	def __init__(self):
		self.power_data=[]
		self.pl=PowerLogger.PowerLogger(interval=0.3,type=2)
		self.pl.start()

	def getSYSTEMpower(self):
		return self.pl.getValue()
	def collectdata(self):
		self.power_data.append(self.getSYSTEMpower())

class DDR:
	def __init__(self):
		self.power_data=[]
		self.pl=PowerLogger.PowerLogger(interval=0.3,type=3)
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
