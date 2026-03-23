# imports
import csv
import os
import subprocess
import time
from datetime import datetime

import bme280
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import smbus2
import sysrsync
from picamera2 import Picamera2

bme_addr = 0x76
smbus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(smbus, bme_addr)

# csv_path = '/home/pi/dev/weatherberry/data/'

now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

base_dir = "/home/pi/dev/weatherberry/"

csv_path = base_dir + "data/"
rsync_source = base_dir + "data/"
rsync_dest = "/home/justin/dev/weatherberry/data/"
rsync_ssh = "justin@oldie.lan"

local_image_path = base_dir + "data/images/"
remote_image_path = "/home/justin/dev/weatherberry/data/images/"
csv_filename = "records.csv"


def c2f(c):
    return (c * 9 / 5) + 32


def check_dirs(image_filename):
    time.sleep(2)

    remote_image_check = remote_image_path + image_filename

    result = subprocess.run(["ssh", rsync_ssh, f"test -f {remote_image_check}"])
    if result.returncode == 0:
        print("remote exists, rm local picture")
        os.remove(local_image_path + image_filename)
    else:
        print(f"@@{image_filename}@@ missing from remote, no rm picture")


def read_bme(now):
    data = bme280.sample(smbus, bme_addr, calibration_params)
    tempF = round(c2f(data.temperature), 2)
    pressure = round(data.pressure, 2)
    humidity = round(data.humidity, 2)

    stats = [now, tempF, pressure, humidity]

    return stats


def append_csv(data):
    with open(
        "/home/pi/dev/weatherberry/data/records.csv", mode="a", newline=""
    ) as file:
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

    cam_config = cam.create_still_configuration(
        main={"size": (1920, 1080)}, buffer_count=1
    )
    cam.configure(cam_config)

    time.sleep(5)

    cam.start()

    time.sleep(5)

    image_filename = now + ".jpg"

    cam.capture_file(local_image_path + image_filename)

    cam.stop()
    cam.close()

    time.sleep(10)
    return image_filename


def plot_graph():
    try:
        df = pd.read_csv("./data/records.csv", parse_dates=["date"])
        df = df.sort_values("date")
        fig, ax = plt.subplots()
        ax.plot(df["date"], df["temp"], label="Temp F")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m:%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45)

        # Optional: horizontal lines for min, max, mean
        ax.axhline(y=df["temp"].mean(), color="green", linestyle=":", label="Mean")
        ax.axhline(y=df["temp"].min(), color="blue", linestyle=":", label="Min")
        ax.axhline(y=df["temp"].max(), color="red", linestyle=":", label="Max")

        ax.set_ylim(df["temp"].min() - 2, df["temp"].max() + 2)
        ax.legend()
        plt.tight_layout()

        # save to static location for Flask
        fig.savefig("./static/temp_plot.png")
        plt.close(fig)
    except Exception as e:
        print(f"Error generating plot: {e}")


def send_data():
    # sysrsync.run(source='/home/pi/dev/weatherberry/data/images/'+image_filename, destination='/home/justin/dev/weatherberry/data/images/', destination_ssh='justin@oldie.lan', options=['-a'])
    sysrsync.run(
        source="/home/pi/dev/weatherberry/data/records.csv",
        destination="/home/justin/dev/weatherberry/data/",
        destination_ssh="justin@oldie.lan",
        options=["-a"],
    )
    # print("sysrsync")


if __name__ == "__main__":
    # kill_picam()
    data = read_bme(now)
    append_csv(data)
    # image_filename = snap_picture()
    send_data()
    # check_dirs(image_filename)
