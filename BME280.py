import time
from datetime import datetime

import bme280
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import smbus2

from capture import capture
from temp import append_csv

address = 0x76
bus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(bus, address)


def c2f(c):
    return (c * 9 / 5) + 32


def read_data():
    try:
        now = datetime.now()
        data = bme280.sample(bus, address, calibration_params)
        tempC = data.temperature
        pressure = round(data.pressure, 1)
        hum = round(data.humidity, 1)

        tempF = round(c2f(tempC), 1)

        stats = [now, tempF, pressure, hum]
        append_csv(stats)

        print(now)
        print(f"temp: {tempF} F")
        print(f"press: {pressure} hPa")
        print(f"hum: {hum} %")

        # plot
        try:
            df = pd.read_csv("./data/records.csv", parse_dates=["date"])
            df = df.sort_values("date")
            fig, ax = plt.subplots()
            ax.plot(df["date"], df["tempF"], label="Temp F")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.set_major_locator(mdates.HourLocator())
            plt.xticks(rotation=45)

            # Optional: horizontal lines for min, max, mean
            ax.axhline(y=df["tempF"].mean(), color="green", linestyle=":", label="Mean")
            ax.axhline(y=df["tempF"].min(), color="blue", linestyle=":", label="Min")
            ax.axhline(y=df["tempF"].max(), color="red", linestyle=":", label="Max")

            ax.set_ylim(df["tempF"].min() - 2, df["tempF"].max() + 2)
            ax.legend()
            plt.tight_layout()

            # save to static location for Flask
            fig.savefig("./static/temp_plot.png")
            plt.close(fig)
        except Exception as e:
            print(f"Error generating plot: {e}")

    except Exception as e:
        print(f"Error: {e}")

    return stats
