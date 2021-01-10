import time
import argparse
import subprocess
import re
from threading import Thread

nanoseconds_per_second = 1e9

class SurfaceFlingerFPS():
	
	def __init__(self, view):
		self.view = view
		self.refresh_period, self.base_timestamp, self.timestamps = self.__init_frame_data__(self.view)
		self.recent_timestamps = self.timestamps[-2]
		self.fps = 0

	def __init_frame_data__(self, view):
		out = subprocess.check_output(['adb', 'shell', 'dumpsys', 'SurfaceFlinger', '--latency-clear', view])
		out = out.decode('utf-8')
		if out.strip() != '':
			raise RuntimeError("Not supported.")
			time.sleep(0.1)
		(refresh_period, timestamps) = self.__frame_data__(view)
		base_timestamp = 0
		base_index = 0
		for timestamp in timestamps:
			if timestamp != 0:
				base_timestamp = timestamp
				break
			base_index += 1
		if base_timestamp == 0:
			raise RuntimeError("Initial frame collect failed")
		return (refresh_period, base_timestamp, timestamps[base_index:])


	def __frame_data__(self, view):
		out = subprocess.check_output(['adb', 'shell', 'dumpsys', 'SurfaceFlinger', '--latency', view])
		out = out.decode('utf-8')
		results = out.splitlines()
		refresh_period = int(results[0]) / nanoseconds_per_second
		timestamps = []
		for line in results[1:]:
			fields = line.split()
			if len(fields) != 3:
				continue
			(start, submitting, submitted) = map(int, fields)
			if submitting == 0:
				continue

			timestamp = submitting/nanoseconds_per_second
			timestamps.append(timestamp)
		return (refresh_period, timestamps)

	def collect_frame_data(self,view):
		if view is None:
			raise RuntimeError("Fail to get current SurfaceFlinger view")

		#refresh_period, base_timestamp, timestamps = self.__init_frame_data__(view)
		#while True:
		
		self.refresh_period, self.timestamps = self.__frame_data__(view)
		#print(self.timestamps)
		time.sleep(1)
		self.refresh_period, tss = self.__frame_data__(view)
		#print(tss)
		self.last_index = 0
		#print(tss)
		if self.timestamps:
	    		self.recent_timestamp = self.timestamps[-2]
	    		self.last_index = tss.index(self.recent_timestamp)
		self.timestamps = self.timestamps[:-2] + tss[self.last_index:]
		#time.sleep(1)
		
		ajusted_timestamps = []
		for seconds in self.timestamps[:]:
	    		seconds -= self.base_timestamp
	    		if seconds > 1e6: # too large, just ignore
	        		continue
	    		ajusted_timestamps.append(seconds)

		from_time = ajusted_timestamps[-1] - 1.0
		fps_count = 0
		for seconds in ajusted_timestamps:
	    		if seconds > from_time:
	        		fps_count += 1
		self.fps = fps_count

	def start(self):
		th = Thread(target=self.collect_frame_data, args=(self.view,))
		th.start()
	
	def getFPS(self):
		self.collect_frame_data(self.view)
		return self.fps
