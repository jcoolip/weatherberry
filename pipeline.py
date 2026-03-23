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
from matplotlib.ticker import NullLocator
from picamera2 import Picamera2

bme_addr = 0x76
smbus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(smbus, bme_addr)

# csv_path = '/home/pi/dev/weatherberry/data/'

# now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

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


def read_bme():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        plt.style.use("bmh")

        df = pd.read_csv("data/records.csv", parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date")
        fig, ax = plt.subplots(figsize=(10, 7))

        # Plotting the data
        ax.plot(df["date"], df["temp"], label="Temp F")

        # Setting up the x-axis to display only specific days
        maj_locator = mdates.DayLocator()
        maj_formatter = mdates.DateFormatter("%b-%d")
        min_locator = mdates.HourLocator(interval=6)
        min_formatter = mdates.DateFormatter("%H:%M")

        ax.xaxis.set_major_locator(maj_locator)
        ax.xaxis.set_major_formatter(maj_formatter)
        ax.xaxis.set_minor_locator(min_locator)
        ax.xaxis.set_minor_formatter(min_formatter)
        # ax.xaxis.set_minor_locator(NullLocator())

        # Rotating the labels for better visibility
        fig.autofmt_xdate()

        # Optional: horizontal lines for min, max, mean
        ax.axhline(
            y=df["temp"].mean(),
            color="green",
            linestyle="-.",
            label="Mean",
            linewidth=1,
            alpha=0.3,
        )
        ax.axhline(
            y=df["temp"].min(), color="blue", linestyle="solid", label="Min", alpha=0.4
        )
        ax.axhline(
            y=df["temp"].max(), color="red", linestyle="solid", label="Max", alpha=0.4
        )

        tmin = df["temp"].min()
        tmax = df["temp"].max()
        tmean = df["temp"].mean()

        dmin = df.loc[df["temp"].idxmin(), "date"]
        dmax = df.loc[df["temp"].idxmax(), "date"]

        bbox = dict(boxstyle="round,pad=0.2", fc="black", alpha=0.3)

        ax.annotate(
            f"{tmax:.1f}°F",
            (dmax, tmax),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            bbox=bbox,
        )

        ax.annotate(
            f"{tmin:.1f}°F",
            (dmin, tmin),
            xytext=(0, -15),
            textcoords="offset points",
            ha="center",
            bbox=bbox,
        )

        ax.annotate(
            f"{tmean:.1f}°F",
            (dmin, tmean),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            bbox=bbox,
        )

        # Setting the y-axis limits
        ax.set_ylim(df["temp"].min() - 2, df["temp"].max() + 2)

        ax.grid(axis="x", which="major", linestyle="solid", linewidth=2, alpha=1)
        ax.grid(axis="x", which="minor", linestyle="solid", linewidth=0.4, alpha=0.4)
        ax.grid(axis="y", which="major", linestyle="dashed", linewidth=1, alpha=0.5)

        # Adding legend and title
        ax.legend()
        plt.tight_layout()

        # Saving to static location for Flask
        fig.savefig("./static/dailyMinMaxMean.png")
        # plt.show()
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


def pipeline_run(append):
    # kill_picam()
    data = read_bme()
    if append:
        append_csv(data)
        send_data()
    # image_filename = snap_picture()
    plot_graph()
    # check_dirs(image_filename)
    return data


if __name__ == "__main__":
    pipeline_run(True)
