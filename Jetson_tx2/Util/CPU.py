#!/usr/bin/env python3


from Util import PowerLogger

cpu_clock_list = [345600,499200,652800,806400,960000,1113600,1267200,1420800,1574400,1728000,1881600,2035200]
dir_thermal='/sys/devices/virtual/thermal'

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


		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_max_freq' %(self.idx)
		with open(fname,'w') as f:
			f.write('{}'.format(cpu_clock_list[11]))
			f.close()
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %(self.idx)
		with open(fname,'w') as f:
			f.write('{}'.format(cpu_clock_list[0]))
			f.close()
		self.pl=PowerLogger.PowerLogger(interval=0.3,type=0)
		self.pl.start()
	def getAvailableClock():
		for i in range(0,6):
		        fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_available_frequencies' %(i)
		        with open(fname,'r') as f:
		                line=f.readline()
		                print(line)
	def setCPUclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_setspeed' %(self.idx)
		f=open(fname,'w')
		f.write('{}'.format(cpu_clock_list[i]))
		print('[cpu{}] Set clock {}'.format(self.idx,cpu_clock_list[i]))
		f.close()

	def setCPUmaxclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_max_freq' %(self.idx)
		f=open(fname,'w')
		if (i>2035200):
			i=2035200
		if (i<345600):
			i=345600
		f.write('{}'.format(i))
#		print('[cpu{}] Set max clock {}'.format(i))
		f.close()
	def setCPUminclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %(self.idx)
		f=open(fname,'w')
		if (i>2035200):
			i=2035200
		if (i<345600):
			i=345600
		f.write('{}'.format(i))
#		print('[cpu{}] Set max clock {}'.format(i))
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
	def getCPUmaxclock(self, idx):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_max_freq' %idx
		with open(fname,'r') as f:
			line=f.readline()
			line=line.replace('\n','')
#			print('[cpu{} max freq]{}KHz '.format(idx,line),end="")
			f.close()
			return int(line)

	def getCPUminclock(self, idx):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %idx
		with open(fname,'r') as f:
			line=f.readline()
			line=line.replace('\n','')
			#print('[cpu{} min freq]{}KHz '.format(idx,line),end="")
			f.close()
			return int(line)

	def collectdata(self):
		self.clock_data.append(self.getCPUclock(self.idx))
		self.temp_data.append(self.getCPUtemp())
		self.power_data.append(self.getCPUpower())
		self.voltage_data.append(self.getCPUvoltage())
		self.current_data.append(self.getCPUcurrent())
		self.maxvoltage_data.append(self.getCPUmaxvoltage())
		self.minvoltage_data.append(self.getCPUminvoltage())



		


