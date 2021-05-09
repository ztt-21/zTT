import time
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op

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