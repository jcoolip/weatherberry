#imports
from picamera2 import Picamera2
import time
import subprocess
import os
import csv
import smbus2
import bme280
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sysrsync

from datetime import datetime

bme_addr = 0x76
smbus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(smbus, bme_addr)

# csv_path = '/home/pi/dev/weatherberry/data/'

now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

base_dir = '/home/pi/dev/weatherberry/'

csv_path = base_dir + 'data/'
rsync_source = base_dir + 'data/'
rsync_dest = '/home/justin/dev/weatherberry/data/'
rsync_ssh = 'justin@oldie.lan'

local_image_path = base_dir + 'data/images/'
remote_image_path = '/home/justin/dev/weatherberry/data/images/'
csv_filename = 'records.csv'

def c2f(c):
	return (c*9/5)+32

def check_dirs(image_filename):
	time.sleep(2)

	remote_image_check = remote_image_path + image_filename

	result = subprocess.run(['ssh', rsync_ssh, f"test -f {remote_image_check}"],)
	if result.returncode == 0:
		print("remote exists, rm local picture")
		os.remove(local_image_path+image_filename)
	else:
		print(f"@@{image_filename}@@ missing from remote, no rm picture")

def read_bme():

	data = bme280.sample(smbus, bme_addr, calibration_params)
	tempF = round(c2f(data.temperature), 2)
	pressure = round(data.pressure, 2)
	humidity = round(data.humidity, 2)

	stats = [now, tempF, pressure, humidity]

	return stats

def append_csv(data):

	with open(csv_path+csv_filename, mode='a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(data)

def kill_picam():

	subprocess.run(["pkill", "-f", "libcamera"])
	subprocess.run(["pkill", "-f", "picamera"])

def snap_picture():

	kill_picam()

	time.sleep(5)

	cam = Picamera2()

	time.sleep(5)

	cam_config = cam.create_still_configuration(main={"size": (1920,1080)}, buffer_count=1)
	cam.configure(cam_config)

	time.sleep(5)

	cam.start()

	time.sleep(5)

	image_filename = now + '.jpg'

	cam.capture_file(local_image_path+image_filename)

	cam.stop()
	cam.close()

	time.sleep(10)
	return image_filename

def send_data(image_filename):
	sysrsync.run(source='/home/pi/dev/weatherberry/data/images/'+image_filename, destination='/home/justin/dev/weatherberry/data/images/', destination_ssh='justin@oldie.lan', options=['-a'])
	sysrsync.run(source='/home/pi/dev/weatherberry/data/records.csv', destination='/home/justin/dev/weatherberry/data/', destination_ssh='justin@oldie.lan', options=['-a'])
	print("sysrsync")

if __name__ == "__main__":
	kill_picam()
	data = read_bme()
	append_csv(data)
	image_filename = snap_picture()
	send_data(image_filename)
	#check_dirs(image_filename)
