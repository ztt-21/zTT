import subprocess

little_cpu_clock_list = [300000, 576000, 748800, 998400, 1209600, 1324800, 1516800, 1612800, 1708800]
big_cpu_clock_list = [300000, 652800, 825600, 979200, 1132800, 1363200, 1536000, 1747200, 1843200, 1996800]
dir_thermal='/sys/devices/virtual/thermal'

class CPU:
	def __init__(self,idx,cpu_type,ip):
		self.idx=idx
		self.cpu_type = cpu_type
		self.ip = ip
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
		subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[self.max_freq])+" >", fname+"\""])
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_min_freq' %(self.idx)
		subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[0])+" >", fname+"\""])		
		
	def setCPUclock(self,i):
		self.clk=i
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_setspeed' %(self.idx)
		subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo', str(self.cpu_clock_list[i])+" >", fname+"\""])
		
	def getCPUtemp(self):
		fname='{}/thermal_zone10/temp'.format(dir_thermal)
		output = subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000

	def getCPUclock(self, idx):
		fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %idx
		output = subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"cat', fname+"\""])
		output = output.decode('utf-8')
		output = output.strip()
		return int(output)/1000

	def getAvailableClock(self):
		for i in range(0,8):
					fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_available_frequencies' %(i)
					output = subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"cat', fname+"\""])
					output = output.decode('utf-8')
					output = output.strip()

	def collectdata(self):
		self.clock_data.append(self.getCPUclock(self.idx))
		self.temp_data.append(self.getCPUtemp())

	def currentCPUstatus(self):
		fname='/sys/devices/system/cpu/online'
		with open(fname,'r') as f:
			line=f.readline()
			print(line)
			f.close()

	def getCurrentClock(self):
		if self.cpu_type == 'l':
			for i in range(0,6):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %(i)
				output = subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"cat', fname+"\""])
				output = output.decode('utf-8')
				output = output.strip()
				print('[cpu{}]{}KHz '.format(i,output),end=""),

		if self.cpu_type == 'b':
			for i in range(6,8):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/cpuinfo_cur_freq' %(i)
				output = subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"cat', fname+"\""])
				output = output.decode('utf-8')
				output = output.strip()
				print('[cpu{}]{}KHz '.format(i,output),end=""),

	def setUserspace(self):
		if self.cpu_type == 'l':
			for i in range(0,6):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
				subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo userspace >', fname+"\""])
				print('[cpu{}]Set userspace '.format(i),end="")

		if self.cpu_type == 'b':
			for i in range(6,8):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
				subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo userspace >', fname+"\""])
				print('[cpu{}]Set userspace '.format(i),end="")

	def setdefault(self, mode):
		if self.cpu_type == 'l':
			for i in range(0,6):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
				subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo '+mode+' >', fname+"\""])
				print('[cpu{}]Set {}'.format(i,mode),end="")

		if self.cpu_type == 'b':
			for i in range(6,8):
				fname='/sys/devices/system/cpu/cpu%s/cpufreq/scaling_governor' %(i)
				subprocess.check_output(['adb', '-s', self.ip, 'shell', 'su -c', '\"echo '+mode+' >', fname+"\""])
				print('[cpu{}]Set {}'.format(i,mode),end="")