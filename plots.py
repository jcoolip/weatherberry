import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import NullLocator


def plot_graph():
    try:
        plt.style.use("bmh")

        df = pd.read_csv("data/records.csv", parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date")
        fig, ax = plt.subplots()

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
        fig.savefig("./static/temp_plot.png")
        plt.show()
        plt.close(fig)
    except Exception as e:
        print(f"Error generating plot: {e}")


plot_graph()
