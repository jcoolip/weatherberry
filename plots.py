import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import NullLocator


def plot_graph():
    try:
        df = pd.read_csv("data/records.csv", parse_dates=["date"])

        df = df.dropna(subset=["date"])
        df = df.drop_duplicates(subset="date", keep="last")

        df = df.sort_values("date")
        df = df.set_index("date")
        fig, ax = plt.subplots()

        # Plotting the data
        ax.plot(df["date"], df["temp"], label="Temp F")

        # Setting up the x-axis to display only specific days
        # locator = mdates.DayLocator(interval=7)
        # formatter = mdates.DateFormatter("%m-%d")
        # ax.xaxis.set_major_locator(locator)
        # ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_locator(mdates.HourLocator())
        # ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(24), interval=1))
        # ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        # ax.xaxis.set_minor_locator(NullLocator())

        # Rotating the labels for better visibility
        # fig.autofmt_xdate()

        # Optional: horizontal lines for min, max, mean
        # ax.axhline(y=df["temp"].mean(), color="green", linestyle=":", label="Mean")
        # ax.axhline(y=df["temp"].min(), color="blue", linestyle=":", label="Min")
        # ax.axhline(y=df["temp"].max(), color="red", linestyle=":", label="Max")

        # Setting the y-axis limits
        # ax.set_ylim(df["temp"].min() - 2, df["temp"].max() + 2)

        # Adding legend and title
        # ax.legend()
        plt.tight_layout()

        # Saving to static location for Flask
        fig.savefig("static/temp_plot.png")
        plt.show()
        plt.close(fig)
    except Exception as e:
        print(f"Error generating plot: {e}")


plot_graph()
