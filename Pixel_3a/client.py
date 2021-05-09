#!/usr/bin/env python3

import os
import time
import cv2
import socket
import argparse
import matplotlib.pyplot as plt
import numpy as np
import csv
import struct
import math

from SurfaceFlinger.get_fps import SurfaceFlingerFPS
from PowerLogger.powerlogger import PowerLogger
from CPU.cpu import CPU
from GPU.gpu import GPU


if __name__=="__main__":

	''' 
		--app			Application name [showroom, skype, call]
		--exp_time 		Time steps for learning
		--server_ip		Agent server IP
		--server_port	Agent server port
		--target_fps	Target FPS
		--pixel_ip		Pixel device IP for connecting device via adb
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument('--app', type=str, required=True, choices=['showroom', 'skype', 'call'], help="Application name for learning")
	parser.add_argument('--exp_time', type=int, default='300', help="Time steps for learning")
	parser.add_argument('--server_ip', type=str, required=True, help="Agent server IP")
	parser.add_argument('--server_port', type=int, default=8702, help="Agent server port number")
	parser.add_argument('--target_fps', type=int, required=True, help="Target FPS")
	parser.add_argument('--pixel_ip', type=str, required=True, help="Pixel device IP for connecting device via adb")

	args = parser.parse_args()
	app = args.app
	experiment_time = args.exp_time
	server_ip = args.server_ip
	server_port = args.server_port
	target_fps = args.target_fps
	pixel_ip = args.pixel_ip
	
	t=0
	ts=[]
	fps_data=[]

	''' Connect to agent server '''
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((server_ip, server_port))

	'''  
		Create big, LITTLE and GPU instances 
		For Pixel 3a, c0 -> LITTLE, c6 -> big, g -> GPU
	'''
	c0=CPU(0, ip=pixel_ip, cpu_type='l')
	c6=CPU(6, ip=pixel_ip, cpu_type='b')
	g=GPU(ip=pixel_ip)
	pl=PowerLogger()

	''' Set CPU and GPU governor to userspace '''
	c0.setUserspace()
	c6.setUserspace()
	g.setUserspace()

	''' Set CPU and GPU clock to maximum before starting '''
	c0.setCPUclock(8)
	c6.setCPUclock(8)
	g.setGPUclock(3)

	''' Check whether setting clocks is properly or not '''
	c0.getCurrentClock()
	c6.getCurrentClock()
	g.getCurrentClock()

	''' Create fps driver '''
	if app == 'showroom':
		view = "\"SurfaceView - com.android.chrome/com.google.android.apps.chrome.Main#0\""
	elif app == 'skype':
		view = "\"com.skype.raider/com.skype4life.MainActivity#0\""
	elif app == 'call':
		view = "\"SurfaceView - com.tencent.tmgp.kr.codm/com.tencent.tmgp.cod.CODMainActivity#0\""	
	
	#view = "\"SurfaceView - com.tencent.tmgp.kr.codm/com.tencent.tmgp.cod.CODMainActivity#0\""
	# view = "\"com.skype.raider/com.skype4life.MainActivity#0\""
	#view = "\"SurfaceView - com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity#0\""
	
	sf_fps_driver = SurfaceFlingerFPS(view, ip=pixel_ip)
	
	''' 
		Set initial state
		c_c -> CPU clock
		g_c -> GPU clock
		c_t -> CPU temperature
		g_t -> GPU temperature
	'''
	c_c=8
	g_c=3
	c_t=float(c0.getCPUtemp())
	g_t=float(g.getGPUtemp())
	state=(c_c,g_c,int(pl.getPower()/100),0, c_t, g_t)
	time.sleep(4)



	''' Start learning '''
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
		# time.sleep(3.7)
		
		c_t=float(c0.getCPUtemp())
		g_t=float(g.getGPUtemp())
		next_state=(c_c, g_c, c_p, g_p, c_t, g_t, fps)
		
		send_msg=str(c_c)+','+str(g_c)+','+str(c_p)+','+str(g_p)+','+str(c_t)+','+str(g_t)+','+str(fps)
		client_socket.send(send_msg.encode())
		print('[{}] state:{} next_state:{} fps:{}'.format(t, state, next_state, fps))
		state=next_state
		# get action
		recv_msg=client_socket.recv(8702).decode()
		clk=recv_msg.split(',')

		c_c=int(clk[0])
		g_c=int(clk[1])

		c0.setCPUclock(c_c)
		c6.setCPUclock(c_c)
		g.setGPUclock(g_c)

		t=t+1
		if t==experiment_time:
			break


	# Logging results
	print('Average Total power={} mW'.format(sum(pl.power_data)/len(pl.power_data)))
	print('Average fps = {} fps'.format(sum(fps_data)/len(fps_data)))

	ts = range(0, len(fps_data))
	f=open('power_skype_zTT.csv','w',encoding='utf-8',newline='')
	wr=csv.writer(f)
	wr.writerow(pl.power_data[1:])
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
	wr.writerow(fps_data)
	f.close()

	# Plot results
	fig = plt.figure(figsize=(12, 14))
	ax1 = fig.add_subplot(2, 2, 1)
	ax2 = fig.add_subplot(2, 2, 2)
	ax3 = fig.add_subplot(2, 2, 3)
	ax4 = fig.add_subplot(2, 2, 4)

	ax1.set_xlabel('time')
	ax1.set_ylabel('power(mw)')
	ax1.set_ylim([0, 4000]) 
	ax1.grid(True)
	ax1.plot(ts,pl.power_data[1:],label='TOTAL')
	ax1.legend(loc='upper right')
	ax1.set_title('Power')

	ax2.set_xlabel('time')
	ax2.set_ylabel('temperature')
	ax2.set_ylim([0, 70])
	ax2.grid(True)
	ax2.plot(ts,c0.temp_data,label='LITTLE')
	ax2.plot(ts,c6.temp_data,label='Big')
	ax2.plot(ts,g.temp_data,label='GPU')
	ax2.legend(loc='upper right')
	ax2.set_title('temperature')

	ax3.set_xlabel('time')
	ax3.set_ylabel('clock frequency(MHz)')
	ax3.set_ylim([0, 2000])
	ax3.grid(True)
	ax3.plot(ts,c0.clock_data,label='LITTLE')
	ax3.plot(ts,c6.clock_data,label='Big')
	ax3.plot(ts,g.clock_data,label='GPU')
	ax3.legend(loc='upper right')
	ax3.set_title('clock')

	ax4.set_xlabel('time')
	ax4.set_ylabel('FPS')
	ax4.set_ylim([0, 61])
	ax4.grid(True)
	ax4.plot(ts,fps_data,label='Average FPS')
	ax4.axhline(y=target_fps, color='r', linewidth=1)
	ax4.legend(loc='upper right')
	ax4.set_title('fps')
	
	plt.show()



