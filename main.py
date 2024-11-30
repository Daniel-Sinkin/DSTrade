import datetime as dt
import os

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from src.av_integration import AlphaVantageHandler
from src.av_util import AV_CURRENCY, AV_CURRENCY_DIGITAL

load_dotenv()
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")
if API_KEY_ALPHAVANTAGE is None:
    raise RuntimeError(
        "Couldn't find the Alphavantage api key in the environment variables!"
    )


def main() -> None:
    handler = AlphaVantageHandler(API_KEY_ALPHAVANTAGE)

    months = list(range(1, 10))
    months_fmt = [f"2024-{month:02}" for month in months]
    print(months_fmt)

    months2 = list(range(1, 12))
    months2_fmt = [f"2023-{month:02}" for month in months2]

    for month in months_fmt:
        df: pd.DataFrame = handler.get_candles(ctf="1min", symbol="IBM", month=month)
        df.to_pickle(f"{month}.pkl")

    for month in months2_fmt:
        df: pd.DataFrame = handler.get_candles(ctf="1min", symbol="IBM", month=month)
        df.to_pickle(f"2023-{month}.pkl")


def main_plot():
    # Load the data
    df: pd.DataFrame = pd.read_pickle("2024-08.pkl")

    # Ensure the DataFrame is sorted by index
    df = df.sort_index()

    # Ensure the index is datetime (if it's not already)
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    # Filter data for the first 5-hour range (starting from the first timestamp)
    start_time = df.index.min() + dt.timedelta(hours=13)
    end_time = start_time + pd.Timedelta(hours=5)
    five_hour_range = df.loc[(df.index >= start_time) & (df.index < end_time)]

    # Ensure required columns for candlesticks
    required_columns = ["Open", "High", "Low", "Close"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The DataFrame must contain {required_columns} columns.")

    # Plot candlestick chart
    mpf.plot(
        five_hour_range,
        type="candle",
        style="charles",
        title="First 5 Hours Candlestick Chart",
    )


if __name__ == "__main__":
    main_plot()
